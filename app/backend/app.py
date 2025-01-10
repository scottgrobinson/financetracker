import random
import logging
import os
from nordigen import NordigenClient
from flask import Flask, jsonify
from flask_cors import CORS
from .extensions import db, ma
from .config import Config
from .globals import Globals
from .routes.Account import AccountBlueprint
from .routes.Rule import RuleBlueprint
from .routes.Transaction import TransactionBlueprint
from .nordigen_processor import NordigenProcessor
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# configure logging
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# app setup
app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(AccountBlueprint, url_prefix='/api/account')
app.register_blueprint(RuleBlueprint, url_prefix='/api/rule')
app.register_blueprint(TransactionBlueprint, url_prefix='/api/transaction')

# enable CORS
CORS(app)

db.init_app(app)
ma.init_app(app)

# apscheduler config/setup
executors = {
    'default': ThreadPoolExecutor(4),
    'processpool': ProcessPoolExecutor(2)
}
scheduler = BackgroundScheduler(executors=executors)

# Functions here to avoid "RuntimeError: Working outside of application context."
def update_balances_job():
    with app.app_context():
        NordigenProcessor().nordigen_update_balances()

def update_transactions_job():
    with app.app_context():
        NordigenProcessor().nordigen_update_transactions()

scheduler.add_job(update_balances_job, CronTrigger.from_crontab("45 0,12,18 * * *"), id="update_balance_job")
scheduler.add_job(update_transactions_job, CronTrigger.from_crontab("50 0,12,18 * * *"), id="update_transactions_job")

@app.errorhandler(400)
def bad_request(e):
    logger.error(f"400 Error: {e}")
    return jsonify(error=str(e), message="Bad Request"), 400

@app.errorhandler(404)
def not_found(e):
    logger.error(f"404 Error: {e}")
    return jsonify(error=str(e), message="Not Found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 Error: {e}")
    return jsonify(error=str(e), message="Internal Server Error"), 500

# Avoid starting the scheduler in the Flask reloader process during debug mode.
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    scheduler.start()

if __name__ == '__main__':
    app.run()
