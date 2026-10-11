"""Pure seventh-extension contract; old extension transactions are never replayed."""
import copy
import math

EXTENSION_ID = 'USER_ADD100H_20261011_7TH'
ADDED_SECONDS = 360000
BEFORE_TOTAL = 828000
AFTER_TOTAL = 1188000


def registered_total(budget):
    total = 36000
    identifiers = set()
    for row in budget['budget_extensions']:
        identifier = row['extension_id']
        if identifier in identifiers or row['state'] != 'applied':
            raise ValueError('Duplicate or unapplied extension')
        if row['authorization_basis'] != 'explicit_user_request':
            raise ValueError('Missing direct time authorization')
        amount = row['additional_training_seconds']
        if type(amount) is not int or amount <= 0:
            raise ValueError('Invalid extension amount')
        identifiers.add(identifier)
        total += amount
    if total != budget['authorized_training_seconds']:
        raise ValueError('Unregistered authorized total')
    charged = budget['charged_training_seconds']
    if not math.isfinite(charged) or charged < 0 or charged > total:
        raise ValueError('Invalid charged time')
    return total


def extend_once(budget, approval, now, receipt_path):
    registered_total(budget)
    if budget['active_segment'] is not None:
        raise ValueError('Original owner must settle active learning first')
    if any(row['extension_id'] == EXTENSION_ID for row in budget['budget_extensions']):
        raise ValueError('Seventh extension already registered; read receipt only')
    if budget['authorized_training_seconds'] != BEFORE_TOTAL or len(budget['budget_extensions']) != 6:
        raise ValueError('Unexpected canonical extension boundary')
    if not approval['approved'] or approval['authorization_basis'] != 'direct_human_user_message':
        raise ValueError('Missing actual human authorization')
    if approval['extension_id'] != EXTENSION_ID or approval['added_seconds'] != ADDED_SECONDS:
        raise ValueError('Authorization scope mismatch')
    after = copy.deepcopy(budget)
    after['budget_extensions'].append({
        'extension_id': EXTENSION_ID,
        'additional_training_seconds': ADDED_SECONDS,
        'authorization_basis': 'explicit_user_request',
        'authorization': approval['human_message'],
        'requested_epoch': approval['recorded_epoch'],
        'applied_epoch': now,
        'authorized_seconds_before': BEFORE_TOTAL,
        'authorized_seconds_after': AFTER_TOTAL,
        'state': 'applied',
        'approved_plan_sha256': approval['historical_master_sha256'],
        'authorization_receipt': approval['central_approval_path'],
    })
    after['authorized_training_seconds'] = AFTER_TOTAL
    after['remaining_training_seconds'] = AFTER_TOTAL - budget['charged_training_seconds']
    after['latest_explicit_extension_receipt'] = receipt_path
    after['budget_scope'] = 'Original10h + four20h + fifth40h + sixth100h + seventh100h; actual charged learning time; no automatic addition'
    allowed = {'authorized_training_seconds', 'remaining_training_seconds', 'budget_extensions',
               'latest_explicit_extension_receipt', 'budget_scope'}
    if any(after[k] != value for k, value in budget.items() if k not in allowed):
        raise ValueError('Accounting history or unrelated field changed')
    if after['budget_extensions'][:-1] != budget['budget_extensions']:
        raise ValueError('Original six extension records changed')
    registered_total(after)
    return after
