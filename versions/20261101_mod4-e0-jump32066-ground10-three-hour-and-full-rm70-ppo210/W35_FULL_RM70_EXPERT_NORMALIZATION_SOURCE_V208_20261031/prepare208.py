"""Freeze new source derivatives from allowlisted small text, never model/raw."""
from pathlib import Path
import ast, hashlib, json, time

HERE = Path(__file__).resolve().parent
T = HERE.parent
W = T.parent
OV = T / 'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
OLD = OV / 'W35_PPO50_gas400_source_preparation_20261027'
RUNTIME = OLD / 'runtime_candidate_v1'
MOD = RUNTIME / 'isaac/mod4'
CASE = OV / 'W35_ADAPTED92_NEW86_COMMAND_UID_CYCLE_COMPLETE_CASE_SOURCE_20261030_V2'
SRC = HERE / 'source'
pins = []


def read(path):
    raw = path.read_bytes()
    pins.append(dict(path=str(path), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest(),
                     scope='allowlisted source or small metadata; no binary read'))
    return raw.decode('utf8')


def write(name, value):
    with (SRC / name).open('x', encoding='utf8', newline='\n') as f:
        f.write(value)


def replace_once(value, old, new):
    if value.count(old) != 1:
        raise ValueError('Source derivation mismatch: ' + old)
    return value.replace(old, new)


def main():
    marker = HERE / 'reports/PREPARATION208_ONCE.json'
    with marker.open('x', encoding='utf8') as f:
        json.dump(dict(ID='NEW208_SOURCE_DERIVATION_V1', epoch=time.time(), consumed=True), f)
    base = read(CASE / 'w35_observed_command_uid_cycle_book_v1.py')
    write('w35_base208.py', base)
    # Selected exact latest observer sources remain independent from the older
    # training runtime. No old once entry is called.
    for old, new in [('w35_early_original_retained_resample_observer_v1.py', 'early208.py'),
                     ('w35_profile_env_domain_panel_v2.py', 'panel208.py')]:
        write(new, read(CASE / old))
    command = read(CASE / 'REFERENCE_EXACT_retention_flat_runtime.py.txt')
    tree = ast.parse(command)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'RetainedFlatCommand')
    body = ast.get_source_segment(command, cls)
    body = replace_once(body, 'class RetainedFlatCommand(RoughStraightCommand):',
                        'class RM70Command208(RoughStraightCommand):')
    body = body.replace('eligibility(self._env,ids)', 'rm70_eligibility(self._env,ids)')
    # The source's original method sampler, command RNG draws and all fixed SI
    # controls remain. The new course contains no certified old clear-plane cell.
    header = '''"""Original W35 rough sampler/retained RNG, explicit new all-rough arena."""
import torch
from course_math208 import COURSE_PROFILE as PROFILE, COLLISION_USDC_SHA
from terrain208 import RoughStraightCommand
from retained_flat_command_math import sample_commands, update_world_projection
from retention_command_state import FIELDS, validate as legacy_validate, PROFILE as LEGACY_PROFILE

def tensor(v):
 return v.torch if hasattr(v,'torch') else v

def validate(s,n):
 assert s['profile']==PROFILE
 return legacy_validate(dict(s,profile=LEGACY_PROFILE),n)

def rm70_eligibility(env,ids):
 # All routes are this new original-CAD rough lesson. No certification of an
 # old plane cell, no actor terrain mask, and no forced yaw/velocity correction.
 return (torch.zeros(len(ids),device=env.device,dtype=torch.bool),
         torch.full((len(ids),),4,device=env.device,dtype=torch.long))
'''
    ownership = '''
 @property
 def _retention_rng(self):
  return self._retention_rng_owner['generator']
 @_retention_rng.setter
 def _retention_rng(self,value):
  self._retention_rng_owner={'generator':value}
'''
    write('command208.py', header + '\n' + body + ownership)
    terrain = read(CASE / 'REFERENCE_EXACT_e1_terrain_runtime.py.txt')
    terrain = replace_once(terrain, 'from e1_full_pose_reset import query, full_reset',
                           'from reset208 import query, full_reset')
    write('terrain208.py', terrain)
    learning = read(MOD / 'e1_terrain_training_env.py')
    learning = replace_once(learning, 'from e1_terrain_runtime import E1ChassisTerrainEnv,configure_intro',
                            'from terrain208 import E1ChassisTerrainEnv,configure_intro')
    write('base_learning208.py', learning)
    evidence = read(MOD / 'e1_reset_evidence_training_env.py')
    evidence = replace_once(evidence, 'from e1_terrain_training_env import E1TerrainLearningEnv',
                            'from base_learning208 import E1TerrainLearningEnv')
    write('evidence208.py', evidence)
    learning = read(CASE / 'REFERENCE_EXACT_retention_learning_env.py.txt')
    learning = replace_once(learning, 'from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv',
                            'from evidence208 import E1ResetEvidenceLearningEnv')
    write('learning208.py', learning)
    trainer = read(CASE / 'REFERENCE_EXACT_train_e1_retention_named_owned_resume_ppo.py.txt')
    trainer = replace_once(trainer, 'from retention_learning_env import RetentionLearningEnv as Mod4Env',
                           'from learning208 import RetentionLearningEnv as Mod4Env')
    trainer = replace_once(trainer, 'from retention_flat_runtime_named_owned import configure_retention as configure_intro',
                           'from config208 import configure208 as configure_intro')
    trainer = trainer.replace('from retention_checkpoint import ', 'from checkpoint208 import ')
    trainer = replace_once(trainer, 'from g3_terrain_checkpoint import current_state,identity',
                           'from checkpoint208 import current_state,identity')
    trainer = replace_once(trainer, "manifest['explicit_G3_derived_geometry_transition']=True",
                           "manifest['explicit_full_RM70_208_original_CAD_transition']=True")
    trainer = replace_once(trainer, 'manifest["active_expert"]="E1"',
                           'manifest["active_expert"]="W35_RM70_FULL208"')
    write('train208.py', trainer)
    worker = read(OLD / 'W35_PPO50_gas400_finite_worker_v1.py')
    worker = worker.replace('36825921fb3e4a368791be7802c8ff16977e899240ac21ed2c067b2287bb9393',
                            'ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f')
    worker = worker.replace('MOD4_W35_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1', 'MOD4_W35_FULL_RM70_208')
    worker = worker.replace("task['role']=='W35'", "task['role']=='W35_RM70_FULL208'")
    worker = worker.replace('W35_N20K_PPO50_GAS400_SOURCE_NOT_GPU_ADMITTED.pt', 'W35_ADAPTED92_FINAL78.pt')
    worker = worker.replace("entry=mod/'train_e1_retention_named_owned_resume_ppo.py'", "entry=mod/'train208.py'")
    worker = worker.replace('646800', '648360').replace('==32259', '==32336')
    worker = worker.replace("'--learning_rate','.00001'", "'--learning_rate','.00011390625000000003'")
    worker = worker.replace('==.00001', '==.00011390625000000003')
    worker = worker.replace("'W35_PPO50_GAS400_v1'", "'W35_FULL_ORIGINAL_RM70_208'")
    worker = replace_once(worker,
        "OUT=job/'adaptation';OUT.mkdir()",
        "OUT=job/'adaptation';OUT.mkdir()\n assert task['new_RM70_course_source_reviewed'] is True\n assert task['actual_RM70_zeroPT_scene_admission_passed'] is True\n assert task['new_geometry_is_original_shared_CAD_arena'] is True")
    worker = replace_once(worker,
        "os.environ.update(env);os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'",
        "os.environ.update(env);os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'\n os.environ['MOD4_RM70_ORIGINAL_ASSET_ROOT']=str(job/'original_field')\n os.environ['MOD4_RM70_ASSET_RECEIPT']=str(job/'RM70_BINARY_INSTALL_ACTUAL.json')\n os.environ['MOD4_RM70_NEW_LAYOUT_ROOT']=str(OUT/'new_original_CAD_layout')")
    worker = replace_once(worker,
        "source_CPU_SHA']==task['source_CPU_SHA']",
        "source_CPU_SHA']==task['source_CPU_SHA']")
    write('worker208.py', worker)
    # Complete new frozen-W35 caller; only original fields are extended. Original
    #2m boundary and original command class stay unchanged in this evaluation.
    caller = read(CASE / 'evaluate_W35_adapted92_new86_UID_cycle800_once_v2.py')
    caller = caller.replace('import w35_uid_cycle_case_contract_v2 as C', 'import skill_task208 as C')
    caller = caller.replace('from w35_profile_env_domain_panel_v2 import W35DomainPanel',
                            'from panel208 import W35DomainPanel')
    caller = caller.replace('from w35_early_original_retained_resample_observer_v1 import W35EarlyObserver',
                            'from early208 import W35EarlyObserver')
    caller = caller.replace('from w35_observed_command_uid_cycle_book_v1 import W35UIDCycleBook,profile_key',
                            'from skill_cycle208 import FullWorldCycle208 as W35UIDCycleBook\n    from w35_base208 import profile_key')
    caller = replace_once(caller,
        "book.observe_original_terminal(ctx,tensor(robot.data.root_pos_w)[:,:2],tensor(robot.data.heading_w),",
        "book.observe208(ctx,tensor(robot.data.root_pos_w)[:,:2],tensor(robot.data.heading_w),")
    caller = replace_once(caller,
        "[(ctx['command'][:,0]-body[:,0]).abs(),(ctx['command'][:,2]-yaw).abs(),(height-.25).abs()],tm.terminated,tm.time_outs)",
        "[(ctx['command'][:,0]-body[:,0]).abs(),(ctx['command'][:,2]-yaw).abs(),(height-.25).abs()],tm.terminated,tm.time_outs,\n                physics_end_tick=int(real._sim_step_counter),termination_reasons={name:tm.get_term(name).bool() for name in names})")
    caller = caller.replace('for i in range(800):', 'for i in range(C.CONTROL_COUNT):')
    caller = caller.replace('requested_controls=800', 'requested_controls=C.CONTROL_COUNT')
    caller = caller.replace('wall_time_limited=completed<800', 'wall_time_limited=completed<C.CONTROL_COUNT')
    caller = caller.replace('FROZEN_W35_ORIGINAL_UID_CYCLE800_NO_PPO', 'FROZEN_W35_FULL_WORLD_SKILL208_NO_PPO')
    write('evaluate_skill208.py', caller)
    install = json.loads(read(OV / 'W35_retention_fixed_next92_source_extension_candidate_v2' /
                              'W35_RETENTION_BASELINE_V2_COMPLETE_INSTALL_MANIFEST.json'))
    # Required selected-runtime deltas from the complete latest exact references.
    rows = list(install['small_source_files'])
    overrides = {
        'runtime/isaac/mod4/e1_full_pose_reset.py': CASE / 'REFERENCE_EXACT_e1_full_pose_reset.py.txt',
        'runtime/isaac/mod4/retention_checkpoint.py': CASE / 'REFERENCE_EXACT_retention_checkpoint.py.txt',
        'runtime/isaac/mod4/train_e1_retention_named_owned_resume_ppo.py': CASE / 'REFERENCE_EXACT_train_e1_retention_named_owned_resume_ppo.py.txt'}
    for relative, path in overrides.items():
        raw = read(path).encode('utf8')
        row = dict(local_path=str(path), installed_relative=relative, bytes=len(raw),
                   SHA=hashlib.sha256(raw).hexdigest())
        rows = [r for r in rows if r['installed_relative'] != relative] + [row]
    manifest = dict(schema='mod4.new208.source_install.v1', base_rows=rows,
        source_qualified=False, all_binaries_metadata_only=install.get('binary_dependencies', install.get('indexed_binary_dependencies')),
        original_full_manifest_path=str(OV / 'W35_retention_fixed_next92_source_extension_candidate_v2' /
                                      'W35_RETENTION_BASELINE_V2_COMPLETE_INSTALL_MANIFEST.json'),
        original_latest_case_manifest=str(CASE / 'W35_UID_CYCLE_COMPLETE_INPUT_MANIFEST_V2.json'),
        new_sources_installed_to='runtime/isaac/mod4',
        source_model=dict(SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f',
            bytes=17619013, Adam17=648360, RSL_iteration=32336, LR=.00011390625000000003),
        no_model_or_raw_reads=True, remote_or_Git_calls=0)
    with (HERE / 'reports/INSTALL208_SOURCE_INPUTS.json').open('x', encoding='utf8') as f:
        json.dump(manifest, f, indent=2)
    with (HERE / 'reports/SOURCE208_DERIVATION_PINS.json').open('x', encoding='utf8') as f:
        json.dump(dict(ID='NEW208_SOURCE_DERIVATION_V1', epoch=time.time(), inputs=pins,
            original_sources_not_overwritten=True, model_NPZ_raw_SDK_remote_reads=0,
            Git_status='PENDING_ROOT_UNIQUE208_ARCHIVE'), f, indent=2)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        import traceback
        with (HERE / ('reports/PREPARATION208_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json')).open('x', encoding='utf8') as f:
            json.dump(dict(ID='NEW208_SOURCE_DERIVATION_V1', traceback=traceback.format_exc()), f, indent=2)
        raise
