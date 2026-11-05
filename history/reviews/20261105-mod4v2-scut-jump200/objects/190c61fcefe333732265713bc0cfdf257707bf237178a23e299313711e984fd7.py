"""Record actual local FIRST/bound receiver; no SSH, PT read, or simulation."""
from pathlib import Path
import json,time
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200'
A=N/'supermimic_final881_host_replay02_1h';old=N/'supermimic_final881_1h'
read=lambda p:json.loads(Path(p).read_bytes())
plan=read(A/'PLAN.json')
actual=read(A/'reports/FIRST_ACTUAL_RETURNED.json')if(A/'reports/FIRST_ACTUAL_RETURNED.json').exists()else{}
validation=read(A/'reports/FIRST_VALIDATION.json')if(A/'reports/FIRST_VALIDATION.json').exists()else{}
f=actual.get('files',{});valid=validation.get('valid',False)
if valid:status='ACTUAL_VALID_20K_SUPERMIMIC_H32_FIRST_FULLSAVE_CPU_REPLAY'
elif f.get('OWNER_EXIT.json',{}).get('error'):status='SUPERMIMIC_HOST_REPLAY_RETRY_FAILED_ORIGINAL_ERROR_PRESERVED'
else:status='SUPERMIMIC_HOST_REPLAY_20K_LAUNCHED_FIRST_PENDING'
controller_name='POSTROUND_EXACT_CIM.json'if(A/'reports/POSTROUND_EXACT_CIM.json').exists()else'LAUNCH_EXACT_CIM.json'
controller=read(A/'reports'/controller_name)
prior=read(old/'reports/FAILED_FORMAL_RETURNED.json')
report=dict(epoch=time.time(),status=status,root=str(A),remote=plan['remote_root'],
    first_validation=validation,actual_FIRST=f.get('production/FIRST_UPDATED.json'),
    actual_GO=f.get('GO_PRODUCTION.json'),startup=f.get('production/STARTUP.json'),
    controller=controller,prior_failure=dict(root=str(old),owner=prior['files']['OWNER_EXIT.json'],
        checkpoint=prior['interrupted_checkpoint'],BPTT_updates=0,original_failed_return_preserved=True),
    memory_repair=dict(replay_CPU_bytes=2261760000,GPU_batches=True,full_precision=True,
        unused_PPO_runner_released=True,unchanged_20k_physics_reward=True),
    tests=[str(N/'reports/HOST_REPLAY_PARITY.json'),str(N/'supermimic_host_replay08/RESULT.json')],
    cumulative_seconds_before=plan['cumulative_authorized_seconds_before_this_segment'],
    next='Only exact own local controller/children/stdoutstderr/error/returned files while healthy; no second SSH, reader, launch, or hotpatch. Fullsave/safeclose then immediate80/native actual-pose review; true200mm acceptance before stairs.')
name='SUPERMIMIC_HOST_REPLAY_ACTUAL_FIRST.json'if valid else'SUPERMIMIC_HOST_REPLAY_LAUNCH_STATUS.json'
target=N/'reports'/name
with target.open('x',encoding='utf8')as stream:json.dump(report,stream,indent=2,ensure_ascii=False)
for p in [N.parents[1]/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json']:
    value=read(p)
    value.update(epoch=time.time(),current_training=status,current_training_root=str(A),
        current_training_remote=plan['remote_root'],local_controller=controller,next=report['next'])
    migration=value['newton_migration']
    migration.update(status=status,current_root=str(A),current_remote=plan['remote_root'],
        source_iteration=881,source_Adam_step=17620,source_lr=.0008649755859375004,
        source_SHA=plan['source_checkpoint']['SHA'],source_root=str(N/'newton_fudan_final620_1h/episode_reset04'),
        FIRST_pending=not bool(actual),FIRST=f.get('production/FIRST_UPDATED.json'),
        GO=f.get('GO_PRODUCTION.json'),production_running=not bool(f.get('OWNER_EXIT.json')),
        sole_collector=controller if controller_name.startswith('POSTROUND')else None)
    value['supermimic_interleaving'].update(current_root=str(A),actual_launch_pending_FIRST=not bool(actual),
        production_switch_ready=valid,actual_20k_H32_fullsave_verified=valid,
        replay_storage='cpu',replay_sample_device='cuda:0',replay_bytes_estimate20k=2261760000,
        memory_path_parity_and_real_resume_passed=True,previous20kOOM=report['prior_failure'],
        cumulative_actual_seconds_before_current=report['cumulative_seconds_before'],next=report['next'])
    if valid:
        first=f['production/FIRST_UPDATED.json'];go=f['GO_PRODUCTION.json']
        value['supermimic_interleaving'].update(FIRST=first,GO=go,sole_collector=controller)
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(dict(saved=True,status=status,controller=controller['row']['ProcessId'],valid_FIRST=valid)))
