"""CURB geometry with the previously admitted, unchanged conditional commands."""
from retention_flat_runtime_named_owned import configure_retention as admitted_configure
from curb20_geometry import configure_curb
def configure_retention(cfg):
    admitted=admitted_configure(cfg)
    command_class=cfg.commands.twist.class_type
    zero_reward=cfg.rewards.spin_contact_consistency.func
    generator_class=cfg.scene.terrain.terrain_generator.class_type
    importer_class=cfg.scene.terrain.class_type
    # Configuration only: no old mesh or physical scene is instantiated here.
    current=configure_curb(cfg)
    cfg.commands.twist.class_type=command_class
    cfg.rewards.spin_contact_consistency.func=zero_reward
    cfg.scene.terrain.terrain_generator.class_type=generator_class
    cfg.scene.terrain.class_type=importer_class
    for key in ('retained_command_scope','private_command_rng_ownership','SDK_reward_signature_repair'):
        current[key]=admitted[key]
    current['old_conditional_command_math_and_private_ownership_exact_reused']=True
    return current
