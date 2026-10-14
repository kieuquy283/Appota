from __future__ import annotations

from datetime import date


AUTHORITY_RANK = {"OFFICIAL_POLICY": 4, "APPROVED_PROCEDURE": 3, "GUIDELINE": 2, "FAQ": 1}


def _matches(rule: dict, user: dict) -> bool:
    for key in ("company", "department", "team", "role"):
        if key in rule and rule[key] not in ("*", user.get(key)):
            return False
    if "min_level" in rule and user["level"] < rule["min_level"]:
        return False
    return True


def can_read(user: dict, document: dict) -> bool:
    rules = document.get("access", [])
    if any(r["effect"] == "DENY" and _matches(r, user) for r in rules):
        return False
    return any(r["effect"] == "ALLOW" and _matches(r, user) for r in rules)


def is_applicable(user: dict, document: dict) -> bool:
    return _matches(document.get("applicability", {}), user)


def current_versions(document: dict, query_date: date) -> list[dict]:
    valid = []
    for version in document["versions"]:
        if version["status"] != "APPROVED":
            continue
        start = date.fromisoformat(version["from"])
        end = date.fromisoformat(version["to"]) if version["to"] else None
        if start <= query_date and (end is None or query_date < end):
            valid.append(version)
    # A malformed overlap is ambiguous and must not be resolved by similarity.
    if len(valid) > 1:
        raise ValueError(f"Multiple current versions: {document['id']}")
    return valid


def resolve_authority(chunks: list[dict]) -> tuple[str, list[dict]]:
    if not chunks:
        return "INSUFFICIENT", []
    highest = max(AUTHORITY_RANK[x["authority"]] for x in chunks)
    selected = [x for x in chunks if AUTHORITY_RANK[x["authority"]] == highest]
    if len({x["value"] for x in selected}) > 1:
        return "CONFLICT", selected
    return "SELECTED", selected
