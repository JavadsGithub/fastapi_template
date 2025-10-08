# app/auth/engine.py
from typing import Tuple, Dict, Any
from app.auth import policies

class ABACEngine:
    def __init__(self):
        self.pmap = {
            "delete_product": policies.can_delete_product,
            "download_product": policies.can_download_product,
        }

    def evaluate(self, policy_name: str, user: Any, resource: Any, env: Dict[str, Any]) -> Tuple[bool, str]:
        policy = self.pmap.get(policy_name)
        if not policy:
            return False, "policy_not_found"
        return policy(user, resource, env)

    def check_access(self, context: dict) -> bool:
        """
        Wrapper برای سازگاری با context مدل قدیمی‌تر.
        """
        action = context["action"]
        user = context["user"]
        resource = context["resource"]
        env = context.get("env", {})

        allowed, _ = self.evaluate(f"{action}_{resource['type']}", user, resource, env)
        return allowed
