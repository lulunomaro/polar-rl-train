"""Read-only AST inventory for a future SCUT Rough-v1 adapter. No simulator imports."""
from pathlib import Path
import ast
import hashlib
import json
import time

REF = Path('/home/egde/fangzhen_linux/refs/wheeled-legged_RL-main')
PRODUCTION = Path('/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001')
DEST = Path('/home/egde/rl_candidates/MOD4_SCUT_ROUGH_V1_PREPARE_20261001')
TARGETS = {
    'WheelbipeV14RoughEnvCfg_v1', '_apply_v14_rough_runtime_cfg',
    '_enable_v14_body_height_scanner', '_enable_v14_wheel_height_scanners',
    '_enable_v14_rough_height_offset_curriculum',
    'RM_ROUGH_TERRAINS_CFG', 'V14_ROUGH_TERRAIN_COMMAND_OVERRIDES',
    'V14_ROUGH_HEIGHT_OFFSET_CURRICULUM_DEFAULT_CFG',
}


def assigned_names(node):
    if isinstance(node, ast.Assign):
        return [n.id for target in node.targets for n in ast.walk(target) if isinstance(n, ast.Name)]
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return [node.target.id]
    return [getattr(node, 'name', '')]


def main():
    DEST.mkdir(exist_ok=True)
    found = {}
    for path in (REF/'source').rglob('*.py'):
        source = path.read_text(encoding='utf8')
        if not any(target in source for target in TARGETS):
            continue
        for node in ast.parse(source).body:
            for name in set(assigned_names(node)) & TARGETS:
                key = str(path.relative_to(REF))+'::'+name
                found[key] = {'file': str(path), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                              'start_line': node.lineno, 'source': ast.get_source_segment(source, node)}
    blockers = {
        'terrain_selector': 'mod4_task accepts only flat/field; no SCUT rough selector implemented.',
        'native_plane': 'Do not leave the z0 infinite plane under generated rough terrain.',
        'ground_height': 'Current nonflat raycaster binds RMUC shared mesh. Bind the actual generated collider instead.',
        'closed_loop_reset': 'scut_flat_rescue.consistent_reset explicitly rejects nonflat; adapt complete q/root poses, not four independent motors.',
        'upstream_state_machines': 'V14 Rough-v1 enables airborne/precontact, forward and wheel/body scanning, terrain command overrides and boundary reset. Copying only a terrain flag is insufficient.',
        'checkpoint_interface': 'Keep the existing 35D actor/38D critic/6 actions and optimizer/std unless a separately tested migration is necessary.',
        'budget': 'Use the same canonical 36000-second ledger, safe complete-save boundary, and no concurrent 20k scenes.',
        'admission': 'Wait for the current mild trial two-seed nominal/DR decision before a rough production handover.',
    }
    result = {'stage':'preparation_only_no_deployment', 'created_epoch':time.time(),
              'declared_upstream_commit':'b8ff79f3df855faf9dc92f4a282bd80c42649466',
              'local_reference_git_metadata_available':(REF/'.git').exists(),
              'commit_provenance_note':'Archive has no .git metadata. These are actual local source hashes, not a claimed Git HEAD verification. Verify pinned upstream bytes before deployment.',
              'source_definitions':found, 'blocking_adaptations':blockers,
              'production_modified':False, 'probe_launched':False, 'budget_modified':False}
    path=DEST/'ROUGH_V1_SOURCE_INVENTORY.json'
    path.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({'inventory':str(path),'definitions_found':len(found),'production_modified':False}))


if __name__ == '__main__':main()
