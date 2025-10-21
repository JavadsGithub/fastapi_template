# app/auth/engine.py
from typing import Tuple, Dict, Any
import logging
from app.auth import policies

from app.auth.utils import get_attr

logger = logging.getLogger(__name__)


class ABACEngine:
    def __init__(self):
        self.pmap = {
            "delete_product": policies.can_delete_product,
            "download_product": policies.can_download_product,
        }

    def evaluate(
        self, policy_name: str, user: Any, resource: Any, env: Dict[str, Any]
    ) -> Tuple[bool, str]:
        logger.debug(
            f"Evaluating policy: {policy_name} for user {getattr(user, 'id', 'unknown')}"
        )
        policy = self.pmap.get(policy_name)
        if not policy:
            logger.warning(f"Policy not found: {policy_name}")
            return False, "policy_not_found"
        try:
            return policy(user, resource, env)
        except Exception as e:
            logger.error(f"Policy evaluation error in {policy_name}: {e}")
            return False, "policy_evaluation_error"

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
