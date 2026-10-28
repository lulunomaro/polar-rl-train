"""Pinned SCUT V14 Rough v1 terrain configuration for an isolated MOD4 adapter.

Call only after Isaac App initialization. This constructs a config; it does not
change the running trainer, its budget, reset logic, or observation dimensions.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import sys
import types


COMMIT = "b8ff79f3df855faf9dc92f4a282bd80c42649466"
HEIGHT_FIELD_SHA = "5f444236205f6ab4a56e0c76387b388d5d2d5a7a83ab63386f5cf15ae5b68d0e"
SOURCE = Path(__file__).parent / "pinned_source" / "height_field.py"
RECIPE = Path(__file__).parent / "ROUGH_V1_RESOLVED_RECIPE.json"


def load_custom_terrains():
    """Preserve upstream function bytes; adapt only the SDK decorator import.

    This Isaac build exposes isaaclab.utils.configclass as a module depending on
    import order. The explicit callable import is required by its own SDK code.
    The original pinned file is kept unedited and its hash checked before loading.
    """
    source = SOURCE.read_bytes()
    if hashlib.sha256(source).hexdigest() != HEIGHT_FIELD_SHA:
        raise ValueError("SCUT custom terrain source does not match pinned commit")
    name = "_mod4_scut_pinned_height_field"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    tree = ast.parse(source.decode("utf-8"), filename=str(SOURCE))
    replaced = 0
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "isaaclab.utils":
            if [a.name for a in node.names] == ["configclass"]:
                node.module = "isaaclab.utils.configclass"
                replaced += 1
    if replaced != 1:
        raise ValueError("Pinned SDK compatibility edit no longer matches")
    module = types.ModuleType(name)
    module.__file__ = str(SOURCE)
    sys.modules[name] = module
    try:
        exec(compile(tree, str(SOURCE), "exec"), module.__dict__)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def make_terrain_cfg(num_envs, *, seed=20261002, profile="upstream_v1"):
    """Return TerrainImporterCfg, plus an explicit adaptation receipt.

    upstream_v1 retains all 11 active families and their numerical parameters.
    intro_v1 is an explicitly labelled MOD4 entry subset; it excludes cliffs and
    15 cm stairs until legal resets and airborne behavior are independently tested.
    Neither profile silently spawns a Plane below the generated mesh.
    """
    import isaaclab.sim as sim_utils
    import isaaclab.terrains as terrain_gen
    from isaaclab.terrains import TerrainImporterCfg
    from isaaclab.terrains.terrain_generator_cfg import TerrainGeneratorCfg

    recipe = json.loads(RECIPE.read_text(encoding="utf-8"))
    if recipe["commit"] != COMMIT or len(recipe["active_terrain_definitions"]) != 11:
        raise ValueError("Unexpected terrain recipe identity")
    custom = load_custom_terrains()
    if profile not in ("upstream_v1", "intro_v1"):
        raise ValueError("Unknown isolated Rough profile")
    intro_weights = {
        "plane_for_rm": .30, "tiny_step": .20, "slope_for_rm_high": .20,
        "inv_slope_for_rm_low": .15, "random_uniform_for_rm": .15,
    }
    terrain_configs = {}
    for definition in recipe["active_terrain_definitions"]:
        key = definition["key"]
        if profile == "intro_v1" and key not in intro_weights:
            continue
        class_name = definition["class"]
        if class_name.startswith("terrain_gen."):
            cls = getattr(terrain_gen, class_name.split(".", 1)[1])
        else:
            cls = getattr(custom, class_name)
        kwargs = definition["parameters"].copy()
        # The AST recipe is serialized through JSON; restore authored range tuples.
        kwargs = {k: tuple(v) if isinstance(v, list) else v for k, v in kwargs.items()}
        if profile == "intro_v1":
            kwargs["proportion"] = intro_weights[key]
        terrain_configs[key] = cls(**kwargs)
    settings = recipe["generator_source_settings"].copy()
    for key in ("size", "difficulty_range"):
        settings[key] = tuple(settings[key])
    settings.update(seed=seed, curriculum=True, sub_terrains=terrain_configs)
    generator = TerrainGeneratorCfg(**settings)
    cfg = TerrainImporterCfg(
        prim_path="/World/ground", terrain_type="generator",
        terrain_generator=generator, num_envs=num_envs,
        collision_group=-1, max_init_terrain_level=0,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            static_friction=1.0, dynamic_friction=1.0, restitution=0.0,
            friction_combine_mode="multiply", restitution_combine_mode="multiply"),
        debug_vis=False,
    )
    receipt = {
        "upstream_commit": COMMIT, "profile": profile,
        "families": list(terrain_configs), "custom_source_sha256": HEIGHT_FIELD_SHA,
        "source_compatibility_edits": ["explicit callable configclass import"],
        "mod4_curriculum_adaptations": ["fixed seed", "initial terrain level 0"],
        "stage": "CONFIG_CANDIDATE_NOT_RUNTIME_ACCEPTED",
        "infinite_plane_below_terrain": False,
        "reset_adapter_installed": False, "production_modified": False,
    }
    if profile == "intro_v1":
        receipt["mod4_curriculum_adaptations"] += [
            "five-family entry subset, explicit proportions", "cliff and stair families deferred"]
        receipt["subset_proportions"] = intro_weights
    return cfg, receipt
