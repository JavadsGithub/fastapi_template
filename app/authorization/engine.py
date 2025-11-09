# app/authorization/engine.py
import logging
from typing import Any, Dict, Tuple
from functools import lru_cache
from app.authorization.policy_loader import load_policy_config
from app.constants.auth_const import RULE_FUNCTIONS
from app.utils.auth_utils import get_attr

type Condition = str | list["Condition"]


logger = logging.getLogger(__name__)


class ABACEngine:
    def __init__(self):
        self.config = load_policy_config()

    @lru_cache(maxsize=128)
    def _get_policy(self, policy_name: str):
        if policy_name not in self.config.policies:
            raise ValueError(f"Policy '{policy_name}' not defined")
        return self.config.policies[policy_name]

    def _evaluate_condition(
        self, cond: Condition, user: Any, resource: Any, env: Dict[str, Any]
    ) -> bool:
        if isinstance(cond, str):
            func_name = self.config.rules.get(cond)
            if not func_name or func_name not in RULE_FUNCTIONS:
                logger.error(f"Rule '{cond}' not found or not mapped")
                return False
            rule_func = RULE_FUNCTIONS[func_name]
            return rule_func(user, resource, env)
        elif isinstance(cond, list):
            return all(self._evaluate_condition(c, user, resource, env) for c in cond)
        else:
            logger.error(f"Invalid condition type: {type(cond)}")
            return False

    def evaluate(
        self, policy_name: str, user: Any, resource: Any, env: Dict[str, Any]
    ) -> Tuple[bool, str]:
        logger.debug(
            f"Evaluating policy: {policy_name} for user {getattr(user, 'id', 'unknown')}"
        )
        try:
            policy = self._get_policy(policy_name)
        except ValueError as e:
            logger.warning(str(e))
            return False, "policy_not_found"

        for condition in policy:
            if self._evaluate_condition(condition, user, resource, env):
                return True, "allowed_by_policy"

        return False, "denied_by_policy"

    def check_access(self, context: dict) -> Tuple[bool, str]:
        action = context["action"]
        resource_type = (
            context["resource"].get("type")
            if isinstance(context["resource"], dict)
            else getattr(context["resource"], "type", "unknown")
        )
        policy_name = f"{action}_{resource_type}"
        user = context["user"]
        resource = context["resource"]
        env = context.get("env", {})

        allowed, reason = self.evaluate(policy_name, user, resource, env)

        logger.debug(
            f"ABAC check: {policy_name} → {allowed} ({reason}) for user {get_attr(user, 'id')}"
        )
        return allowed, reason
