import rule_engine
import traceback
from .logger import logger
from .model.Rule import Rule
from .model.Tag import Tag
from .model.Transaction import Transaction
from .extensions import db, ma

class RuleEngine:
    def __init__(self):
        self.some_var = None

    def action_tag(self, transactions, rule):
        tags = Tag.query.all()
        try:
            for transaction in transactions:
                newtag = Tag()
                newtag.tag = rule.action_value_1
                newtag.transaction_id = transaction.id
                newtag.account_id = transaction.account_id
                if newtag not in tags:
                    db.session.add(newtag)
        except Exception as e:
            logger.info(e)
            logger.error(traceback.format_exc())
        else:
            db.session.commit()


    def run_rules(self, transactions=None):
        def custom_resolver(obj, name):
            return getattr(obj, name)

        logger.info("[RR] Starting")

        # Stage 1 - Find matches
        rules = Rule.query.all()
        if transactions is None:
            transactions = Transaction.query.all()
        rule_context = rule_engine.Context(resolver=custom_resolver)

        matches = {}
        for rule in rules:
            matches[rule.id] = []
            logger.info(f"[RRStage1_#{rule.id}] Running rule: {rule.rule}")

            try:
                rule_engine_rule = rule_engine.Rule(
                    rule.rule,
                    context=rule_context
                )

                matches[rule.id] = list(rule_engine_rule.filter(transactions))
            except rule_engine.errors.RuleSyntaxError as e:
                matches[rule.id] = []
                logger.error(f"[RRStage1_#{rule.id}] {e}")

            logger.info(f"[RRStage1_#{rule.id}] Found {len(matches[rule.id])} matching transactions")

        # Part 2 - Run actions on matches
        for match in matches:
            if len(matches[match]) == 0:
                continue

            rule = next((rule for rule in rules if rule.id == match), None)

            if rule.action == "tag":
                logger.info(f"[RRStage2_#{rule.id}] Running tag action for {len(matches[rule.id])} transactions")
                self.action_tag(matches[match], rule)
            else:
                logger.error(f"[RRStage2_#{rule.id}] Unknown action: {rule.action}")

        logger.info("[RR] Finished")

        return None