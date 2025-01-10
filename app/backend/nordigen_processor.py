import os
import requests
import traceback
from .logger import logger
from .model.Account import Account
from .model.Transaction import Transaction
from .extensions import db
from .rule_engine import RuleEngine
from nordigen import NordigenClient
import json

class NordigenProcessor:
    def __init__(self):
        self.secret_id = os.environ.get("NORDIGEN_SECRET_ID")
        self.secret_key = os.environ.get("NORDIGEN_SECRET_KEY")
        self.nordigen_client = self._initialize_client()

    def _initialize_client(self):
        client = NordigenClient(secret_id=self.secret_id, secret_key=self.secret_key)
        token_data = client.generate_token()
        client.exchange_token(token_data["refresh"])
        return client

    def nordigen_update_balances(self):
        logger.info("[BALUPD] Starting")
        for accid in [account.id for account in Account.query.with_entities(Account.id).all()]:
            account = Account.query.filter_by(id=accid).first()
            accountClient = self.nordigen_client.account_api(accid)

            try:
                balances = accountClient.get_balances()
            except urllib3.exceptions.ReadTimeoutError:
                errorMsg = f"[BALUPD_{accid[-6:]}] Timeout connecting to remote server. Skipping all BALUPD"

                logger.error(errorMsg)
                return errorMsg     
            except requests.exceptions.HTTPError as e:
                errorMsg = None
                if e.response is not None:
                    match e.response.status_code:
                        case 401:
                            errorMsg = f"[BALUPD_{accid[-6:]}] Nordigen token is invalid or expired. Skipping all BALUPD"
                        case 429:
                            errorMsg =  f"[BALUPD_{accid[-6:]}] API rate limit exceeded. Skipping all BALUPD"

                if errorMsg is None:
                    errorMsg = f"[BALUPD_{accid[-6:]}] HTTP Error fetching balances: {e}. Skipping all BALUPD"

                logger.error(errorMsg)
                return errorMsg

            for balance in balances['balances']:
                if balance['balanceType'] == account.balance_type:
                    account.balance = round(float(balance['balanceAmount']['amount']), 2)
                    db.session.commit()
                    continue

            logger.info(f"[BALUPD_{accid[-6:]}] Updated")

        logger.info("[BALUPD] Finished")
        return True

    def nordigen_update_transactions(self, transactionfile=None):
        logger.info("[TXNUPD] Starting")

        for accid in [account.id for account in Account.query.with_entities(Account.id).all()]:
            account = Account.query.filter_by(id=accid).first()
            transaction_ids = [transaction.id for transaction in list(account.transactions)]

            if transactionfile is not None:
                try:
                    with open(transactionfile, 'r') as json_data:
                        data = json.load(json_data)[accid]
                        txns = {'transactions': {'booked': data}}
                except Exception as e:
                    logger.error(f"[TXNUPD_{accid[-6:]}] Error reading transaction file: {e}")
                    return f"[TXNUPD_{accid[-6:]}] Error reading transaction file: {e}"        
            else:  
                try:
                    accountClient = self.nordigen_client.account_api(accid)
                    txns = accountClient.get_transactions()
                except requests.exceptions.HTTPError as e:
                    errorMsg = None
                    if e.response is not None:
                        match e.response.status_code:
                            case 401:
                                errorMsg = f"[TXNUPD_{accid[-6:]}] Nordigen token is invalid or expired. Skipping all TXNUPD"
                            case 429:
                                errorMsg =  f"[TXNUPD_{accid[-6:]}] API rate limit exceeded. Skipping all TXNUPD"

                    if errorMsg is None:
                        errorMsg = f"[TXNUPD_{accid[-6:]}] HTTP Error fetching transactions: {e}. Skipping all TXNUPD"

                    logger.error(errorMsg)
                    return errorMsg

            logger.info(f"[TXNUPD_{accid[-6:]}] Found {len(txns['transactions']['booked'])} transactions")
            newtransactions = []
            for txn in txns['transactions']['booked']:
                if txn['internalTransactionId'] in transaction_ids:
                    existingtxn = Transaction.query.filter_by(id=txn['internalTransactionId'], account_id=accid).first()
                else:
                    try:
                        transaction = Transaction()
                        transaction.id = txn['internalTransactionId']
                        transaction.datetime = txn['bookingDate']
                        transaction.amount = txn['transactionAmount']['amount']
                        if 'creditorName' in txn:
                            transaction.creditor = txn['creditorName']
                        transaction.remittance_information = txn['remittanceInformationUnstructured']
                        transaction.account_id = accid
                        db.session.add(transaction)
                        newtransactions.append(transaction)
                    except KeyError as e:
                        logger.error(f"[TXNUPD_{accid[-6:]}] Missing key {e} in transaction: {txn}")
                    except Exception as e:
                        logger.error(f"[TXNUPD_{accid[-6:]}] An error occurred: {e}")
                        logger.error(traceback.format_exc())

            db.session.commit()
            if newtransactions:
                RuleEngine().run_rules(newtransactions)
                logger.info(f"[TXNUPD_{accid[-6:]}] Added {len(newtransactions)} new transactions")
            else:
                logger.info(f"[TXNUPD_{accid[-6:]}] No new transactions")

        logger.info("[TXNUPD] Finished transaction updates")
