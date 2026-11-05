from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train');CODE=G/'project/isaac/mod4v2_scut'
A=N/'newton_fudan_final620_1h';P=N/'fudan_warp_final461_1h'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda raw:hashlib.sha256(raw).hexdigest()
assert read(N/'reports/NEWTON_ACTUAL_PPO_GRAPH05.json')['passed']
A.mkdir(exist_ok=False);(A/'reports').mkdir()
review=dict(epoch=time.time(),checkpoint_SHA='3da87af137a5244a56a8cfb6ecb4df7636fef7bc23cde62eb3eff2e04648a544',
    all_actual_images_reviewed=True,complete_all80_review=True,
    images=['recorded_native/actual_mod4v2_fudan_warp_final620_side.png',
            'recorded_native/actual_mod4v2_fudan_warp_final620_top.png',
            'recorded_native_late/actual_mod4v2_fudan_warp_final620_side.png',
            'recorded_native_late/actual_mod4v2_fudan_warp_final620_top.png'],
    native_observation='Early0/1/40/41 spawn descent; late low wheel-supported approach then stop before x.8 edge. No airborne edgeclear or top landing.',
    independent80_successes=0,ground_takeoff=0,
    decision='MIGRATE_TO_ACTUAL_NEWTON_AS_HUMAN_REQUESTED',model_reads=0,physics=0,
    previous_owner_error_preserved=True,missing_eval_only_recovered=True)
with(P/'reports/FINAL620_ACTUAL_NATIVE_REVIEW.json').open('x',encoding='utf8')as f:json.dump(review,f,indent=2)
old=read(P/'PLAN.json');remote=old['remote_root'].rsplit('/',1)[0]+'/'+A.name
plan=dict(remote_root=remote,run_id=A.name+'_'+str(time.time_ns()),
    package_root=old['package_root'],runtime=old['runtime'],
    previous_overlay_paths=[old['module_overlay'],*old['previous_overlay_paths']],
    hardware_remote=old['assets'].rsplit('/assets',1)[0],
    reset_bank=old['runtime']+'/reset_bank.json',
    scut_source_paths='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_SCUT_STEP270_2H_1793711274668684600/env20000_1h/SOURCE_PATHS.json',
    num_envs=20000,seed=66,profile='jump200',train_seconds=3600,max_parent_seconds=3900,
    human_direct_no_ledger_admission=True,canonical_reads=0,canonical_writes=0,
    source_checkpoint=dict(path=old['remote_root']+'/production/model_final.pt',bytes=37204527,
        SHA=review['checkpoint_SHA'],iteration=620,format='MOD4V2_SCUT_HW300N60_FULL_V1'),
    source_optimizer_step=12400,source_learning_rate=.0005766503906250003,
    reward_family='FUDAN_JUMP',physics_backend='Newton/SolverMuJoCo/MuJoCo-Warp',
    original_physics_backend='PhysX_TGS32_4',full_IsaacLab3_manager_migration=False,
    previous_native_review=str(P/'reports/FINAL620_ACTUAL_NATIVE_REVIEW.json'),
    cumulative_authorized_seconds_before_this_segment=old['cumulative_authorized_seconds_before_this_segment']+3592.992456674576,
    cumulative_limit_seconds=360000,private_GPU_lock_required=True,
    supermimic_development_only_after_actual_FIRST=True,
    next='Independent80 immediately after fullsave/safeclose. BPTT compatibility during this real PPO hour.')
assert plan['cumulative_authorized_seconds_before_this_segment']+3900<360000
with(A/'PLAN.json').open('x',encoding='utf8')as f:json.dump(plan,f,indent=2)
files=[]
def add(path,relative):
 raw=path.read_bytes();files.append(dict(path=str(path),relative=relative,bytes=len(raw),SHA=H(raw)))
for name in ['newton_model.py','newton_env.py','newton_checkpoint.py','newton_train.py','newton_evaluate.py']:
 add(CODE/name,'overlay/'+name)
add(N/'newton_owner.py','owner.py');add(N/'newton_entry.py','entry.py')
add(Path('F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/mjcf/scene.xml'),'model_source.xml')
launcher='''#!/bin/bash
set -euo pipefail
base='/home/lc01/Zonglin Li/zonglin2'
exec "$base/compat/glibc240/ld-linux-x86-64.so.2" --library-path "$base/compat/glibc240:$base/envs/mod4/lib" "$base/toolchains/mod4v2_newton17/venv/bin/python" "$@"
'''
(A/'run-newton.sh').write_text(launcher,encoding='utf8',newline='\n');add(A/'run-newton.sh','run-newton.sh')
with(A/'SOURCE_PREPARED.json').open('x',encoding='utf8')as f:
 json.dump(dict(epoch=time.time(),files=files,shared_text=read(P/'INDEX_SOURCE_FROZEN.json')['shared_text'],
                asset_copies=0,checkpoint_copies=0,whole_tree_copies=0),f,indent=2)
print(json.dumps(dict(prepared=str(A),files=len(files),source_iteration=620)))
