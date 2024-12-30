import os
import json
import logging
import pymongo
from nordigen import NordigenClient
from flask import Flask, jsonify
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# logging config/setup
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# get credentials
mongo_url = os.environ.get("MONGO_URL")
secret_id = os.environ.get("NORDIGEN_SECRET_ID")
secret_key = os.environ.get("NORDIGEN_SECRET_KEY")

# flask config/setup
app = Flask(__name__)

# apscheduler config/setup
executors = {
    'default': ThreadPoolExecutor(16),
    'processpool': ProcessPoolExecutor(4)
}
scheduler = BackgroundScheduler(executors=executors)

# mongodb config/setup
mongoclient = pymongo.MongoClient(mongo_url)
mongodb = mongoclient["money"]

# nordigen config/setup
nordigenClient = NordigenClient(secret_id=secret_id, secret_key=secret_key)
token_data = nordigenClient.generate_token()
nordigenClient.exchange_token(token_data["refresh"])

def fetch_accounts():
    return list(mongodb["accounts"].find())

# SCHEDULED JOB FUNCTIONS
def updateBalances():
    logger.info("Starting balance updates")
    for account in fetch_accounts():
        accountClient = nordigenClient.account_api(account['_id'])
        balances = accountClient.get_balances()
        for balance in balances['balances']:
            logger.info(balance)
            if balance['balanceType'] == account['balanceType']:
                mongodb["accounts"].update_one({ "_id" : account['_id']}, { "$set" : { "balance" : round(float(balance['balanceAmount']['amount']), 2)}})
                continue

        logger.info(f"Balance updated for account {account['_id']}")

    logger.info("Finished balance updates")


def updateTransactions():
    logger.info("Starting transaction updates")
    for account in fetch_accounts():
        accountClient = nordigenClient.account_api(account['_id'])
        transactions = accountClient.get_transactions()
        for transaction in transactions['transactions']['booked']:
            transaction['accountId'] = account['_id']
            transaction['_id'] = f"{account['_id']}_{transaction['internalTransactionId']}"
            del transaction['transactionId']
            del transaction['internalTransactionId']
            try:
                mongodb["transactions"].update_one({ "_id" : transaction['_id']}, {"$set": transaction}, upsert=True)
            except pymongo.errors.DuplicateKeyError:
                continue

        logger.info(f"Transactions updated for account {account['_id']}")

    logger.info("Finished transaction updates")


# SCHEDULED JOB SCHEDULING
defaultCron = "0 0,4,8,12,16,20 * * *"
scheduler.add_job(updateBalances, CronTrigger.from_crontab(defaultCron))
scheduler.add_job(updateTransactions, CronTrigger.from_crontab(defaultCron))

# ROUTES
@app.route("/accounts", methods=['GET'])
def list_accounts():
    try:
        accounts = fetch_accounts()
        return jsonify(accounts), 200
    except Exception as e:
        logger.error(f"Error listing accounts: {str(e)}")
        return jsonify({"error": "Unable to fetch accounts"}), 500


@app.route("/update/balances", methods=['GET'])
def update_balances():
    updateBalances()
    return jsonify({"success": True}), 200


@app.route("/update/transactions", methods=['GET'])
def update_transactions():
    updateTransactions()
    return jsonify({"success": True}), 200


@app.route("/account/<accountId>", methods=['GET'])
def get_account(accountId):
    try:
        account = mongodb["accounts"].find_one({"_id": accountId})
        if account:
            return jsonify(account), 200
        return jsonify({"error": "Account not found"}), 404
    except Exception as e:
        logger.error(f"Error getting account {accountId}: {str(e)}")
        return jsonify({"error": "Unable to fetch account"}), 500


@app.route("/transactions/<accountId>", methods=['GET'])
def list_transactions(accountId):
    try:
        transactions = list(
            mongodb["transactions"]
            .find({"accountId": accountId})
            .sort("bookingDate", pymongo.DESCENDING)
        )
        return jsonify(transactions), 200
    except Exception as e:
        logger.error(f"Error fetching transactions for {accountId}: {str(e)}")
        return jsonify({"error": "Unable to fetch transactions"}), 500


if __name__ == "__main__":
    scheduler.start()
    app.run(host="0.0.0.0", port="8080", debug=True)
