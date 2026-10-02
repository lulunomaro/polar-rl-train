"""Convert desired elastic gas-force bounds over a slide stroke to q=0 force bounds."""
def full_stroke_reference_bounds(force_min_n, force_max_n, stiffness_n_m, q_min_m, q_max_m):
    if not (force_min_n > 0 and force_min_n <= force_max_n):
        raise ValueError("invalid gas force interval")
    bad_limits = q_min_m >= q_max_m
    if hasattr(bad_limits, "any"):
        bad_limits = bool(bad_limits.any())
    if bad_limits:
        raise ValueError("invalid gas slide interval")
    lower = force_min_n + stiffness_n_m * q_max_m
    upper = force_max_n + stiffness_n_m * q_min_m
    return lower, upper
