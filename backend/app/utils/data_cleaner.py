import re
from urllib.parse import urlparse, urlunparse


CLEAN_RULES = {
    'trim',
    'collapse_whitespace',
    'normalize_url',
}


def _trim(value):
    if isinstance(value, str):
        return value.strip()
    return value


def _collapse_whitespace(value):
    if isinstance(value, str):
        return re.sub(r'\s+', ' ', value).strip()
    return value


def _normalize_url(value):
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return text
    parsed = urlparse(text)
    if parsed.scheme not in {'http', 'https'}:
        return text
    path = parsed.path.rstrip('/') or '/'
    normalized = parsed._replace(fragment='', path=path)
    return urlunparse(normalized)


_CLEANERS = {
    'trim': _trim,
    'collapse_whitespace': _collapse_whitespace,
    'normalize_url': _normalize_url,
}


def normalize_clean_rules(rules):
    if not rules:
        return ['trim', 'collapse_whitespace']
    normalized = []
    for rule in rules:
        key = str(rule or '').strip()
        if key in CLEAN_RULES and key not in normalized:
            normalized.append(key)
    return normalized or ['trim', 'collapse_whitespace']


def apply_cleaners(value, rules):
    result = value
    for rule in normalize_clean_rules(rules):
        cleaner = _CLEANERS.get(rule)
        if cleaner:
            result = cleaner(result)
    return result


def clean_item(item, rules=None):
    rules = normalize_clean_rules(rules)
    result = dict(item or {})
    extra = result.get('extra') or {}
    if isinstance(extra, dict):
        result['extra'] = {
            key: apply_cleaners(value, rules) if isinstance(value, str) else value
            for key, value in extra.items()
        }
    for key in ('title', 'content', 'url'):
        if key in result:
            result[key] = apply_cleaners(result.get(key), rules)
    return result


def build_dedup_signature(item, keys=None):
    keys = keys or ['url']
    parts = []
    extra = item.get('extra') or {}
    for key in keys:
        value = ''
        if key in ('title', 'content', 'url'):
            value = item.get(key) or ''
        elif isinstance(extra, dict):
            value = extra.get(key, '')
        parts.append(str(value).strip().lower())
    return '||'.join(parts)


def deduplicate_items(items, keys=None):
    keys = keys or ['url']
    seen = set()
    result = []
    for item in items or []:
        signature = build_dedup_signature(item, keys)
        if not any(part for part in signature.split('||')):
            result.append(item)
            continue
        if signature in seen:
            continue
        seen.add(signature)
        result.append(item)
    return result
