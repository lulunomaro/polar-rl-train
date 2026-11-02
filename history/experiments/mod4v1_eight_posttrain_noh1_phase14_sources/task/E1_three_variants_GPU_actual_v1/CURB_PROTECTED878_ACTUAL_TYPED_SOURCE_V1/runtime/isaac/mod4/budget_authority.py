"""Validate explicit additions to the one canonical effective-training budget."""


def validate_budget(budget):
    total = 36000
    seen = set()
    for extension in budget.get('budget_extensions', []):
        identifier = extension['extension_id']
        assert identifier not in seen, 'duplicate budget extension'
        seen.add(identifier)
        assert extension['state'] == 'applied'
        assert extension['authorization_basis'] == 'explicit_user_request'
        seconds = extension['additional_training_seconds']
        assert isinstance(seconds, int) and seconds > 0, 'invalid training-time addition'
        total += seconds
    assert budget['authorized_training_seconds'] == total, 'unregistered budget change'
    assert float(budget.get('charged_training_seconds', 0)) >= 0, 'negative charged time'
    return total

