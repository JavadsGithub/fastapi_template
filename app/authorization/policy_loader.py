# app/authorization/policy_loader.py

from pathlib import Path
from typing import Dict
from pydantic import BaseModel, validator
import yaml


# نوع شرط: یا یک رشته (نام قانون)، یا لیستی از شرط‌ها (AND)
type Condition = str | list["Condition"]
type Policy = list[Condition]


class PolicyConfig(BaseModel):
    rules: Dict[str, str]  # نام منطقی → نام تابع
    policies: Dict[str, Policy]

    @validator("rules")
    def validate_rule_functions_exist(cls, v):
        available_functions = {
            "is_admin",
            "is_owner",
            "in_working_hours",
            "is_public",
            "has_purchased",
            "is_self",
            "is_admin_or_self",
            "anyone",
        }
        for logical_name, func_name in v.items():
            if func_name not in available_functions:
                raise ValueError(
                    f"Rule function '{func_name}' not found in rules module"
                )
        return v


def load_policy_config() -> PolicyConfig:
    config_path = Path(__file__).parent.parent / "config" / "abac_policies.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"ABAC policy file not found at {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return PolicyConfig(**data)
