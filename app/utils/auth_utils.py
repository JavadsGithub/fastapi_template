# app/utils/auth_utils.py


def get_attr(obj, attr: str, default=None):
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)
