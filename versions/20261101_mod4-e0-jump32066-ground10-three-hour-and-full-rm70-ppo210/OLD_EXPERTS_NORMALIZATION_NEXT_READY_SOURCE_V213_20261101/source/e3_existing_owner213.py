"""Thin handoff to frozenV14; only already naturally-created original objects."""
from existing_owner_v14_reference213 import record_existing_instances


def observe_original_e3_instances(robot,legs,wheels,*,purpose,already_retained_manager_name=None):
    if purpose['kind']!='E3_ACTUAL_EXISTING_INSTANCE_OWNER213':
        raise ValueError('Distinct originalE3 identity-only purpose required')
    if purpose['model_opens']!=0 or purpose['actor_calls']!=0 or purpose['extra_physics_steps']!=0:
        raise ValueError('This component is metadata-only, never an effort or recovery probe')
    value=record_existing_instances(robot,legs,wheels,
        already_retained_manager_name=already_retained_manager_name,
        manager_name_origin='caller supplied already retained original construction metadata; UNKNOWN if absent')
    return dict(value,purpose_id=purpose['purpose_id'],source_expert='E3',
        source_model_identity_reference='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8',
        source_model_was_not_opened=True,
        all_method_files_need_later_distinct_exact_source_purpose=True,
        original_compute_clip_apply_called_again=False,
        original_recovery_skill_or_effort_validated=False)
