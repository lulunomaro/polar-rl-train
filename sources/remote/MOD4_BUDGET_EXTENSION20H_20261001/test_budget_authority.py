from copy import deepcopy
from budget_authority import validate_budget

old = dict(authorized_training_seconds=36000, charged_training_seconds=24000)
assert validate_budget(old) == 36000
new = deepcopy(old)
new['budget_extensions'] = [dict(extension_id='test-explicit-20h', state='applied',
    authorization_basis='explicit_user_request', additional_training_seconds=72000)]
new['authorized_training_seconds'] = 108000
assert validate_budget(new) == 108000
assert new['authorized_training_seconds']-new['charged_training_seconds'] == 84000
for mutation in ('duplicate', 'unregistered', 'pending', 'negative'):
    bad = deepcopy(new)
    if mutation == 'duplicate': bad['budget_extensions'] *= 2
    elif mutation == 'unregistered': bad['authorized_training_seconds'] += 3600
    elif mutation == 'pending': bad['budget_extensions'][0]['state'] = 'pending'
    else: bad['charged_training_seconds'] = -1
    try: validate_budget(bad)
    except AssertionError: pass
    else: raise AssertionError('Unexpected acceptance: '+mutation)
print('PASS: legacy budget, explicit addition, preserved charge, duplicate/unregistered/pending/negative rejection')

