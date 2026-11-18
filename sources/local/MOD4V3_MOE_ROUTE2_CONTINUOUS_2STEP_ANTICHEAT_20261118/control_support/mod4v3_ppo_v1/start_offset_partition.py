"""Five start offsets independent of the unchanged native DR partition."""
OFFSETS_MM = (-60, -30, 0, 30, 60)

def offset_indices(environment_ids):
    return environment_ids.div(5, rounding_mode="floor").remainder(5)

def population_by_dr_offset(environment_ids, nominal_mask):
    flat = nominal_mask[environment_ids].long() * 5 + offset_indices(environment_ids)
    return flat.bincount(minlength=10).reshape(2, 5)
