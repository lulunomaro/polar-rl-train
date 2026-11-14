"""Existing landing return, paid earlier to each truly supported wheel."""
def landing_credit(supported,already,active):
    gained=supported & (~already) & active[:,None]
    already.logical_or_(gained)
    return .15*gained.sum(-1)
