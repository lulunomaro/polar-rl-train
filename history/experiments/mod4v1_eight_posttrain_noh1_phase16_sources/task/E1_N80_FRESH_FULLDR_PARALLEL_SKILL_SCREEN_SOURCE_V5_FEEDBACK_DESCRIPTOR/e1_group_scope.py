"""Purestdlib groupcontract/barrier; noSDK/model/actor/physics/RNG calls."""
from pathlib import Path
import json,os,time
KIND='N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_NOT_FULL20K_RESUME'
ROLES=('CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50')

def validate_group_task(task,role,group_root,case,contracts,*,environment=None,fd_check=None):
    environment=os.environ if environment is None else environment
    assert role in ROLES and task['role']==role and task['kind']==KIND and task['purpose']==KIND
    assert task['num_envs']==80 and task['seed']==20260928 and task['optimizer_updates']==0
    assert task['fresh_fullDR_cohort'] is True and task['saved20k_DR_physically_applied'] is False
    assert task['state_projection_or_slicing'] is False and task['whole20k_savedrestore_claim'] is False
    assert task['policy_hz']==50 and task['feedback_hz']==100 and task['physics_dt']==.0025 and task['TGS']==[32,4]
    assert task['closure_m']==.01 and task['mimic_rad']==.01 and task['gas_N']==400 and task['stiffness_N_m']==2000
    c=contracts[role];assert task['source_SHA']==c['source']['SHA'] and task['source_bytes']==c['source']['bytes']
    assert task['source_iteration']==c['core']['original_iteration'] and task['source_Adam17']==c['core']['original_17Adam_step'] and task['source_LR']==c['core']['original_LR']
    assert task['asset_SHA']=='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3' and task['contract_SHA']=='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
    expected=1000 if role=='SLOPE_INDEPENDENT50' else 750
    assert task['controls']==expected and task['physics_callbacks']==expected*8 and task['feedback_samples']==expected*2
    assert environment['CUDA_VISIBLE_DEVICES']==task['GPU_UUID']
    a=task['actual_group_admission'];assert a['group_id']==task['group_id'] and a['GPU_UUID']==task['GPU_UUID']
    assert a['source_SDK_admitted'] is True and a['private_GPU_EX_held'] is True and a['global_finite_EX_held'] is True
    assert len(a['inherited_lock_fds'])>=2 and len(set(a['inherited_lock_fds']))==len(a['inherited_lock_fds'])
    for fd in a['inherited_lock_fds']:
        assert type(fd) is int and fd>=0
        (fd_check or os.fstat)(fd)  # Validate inheriteddescriptor existence, neverflock/release parentlocks.
    root=Path(group_root).resolve();case=Path(case).resolve();assert case.is_relative_to(root)
    assert task['absolute_worker_deadline_epoch']>time.time()
    return True


def put_json(path,value):
    path=Path(path);tmp=path.with_name(path.name+'.partial')
    with tmp.open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)


def wait_group_start(task,group_root,*,ready_time=None,maximum_seconds=900,now=None,pause=None,read_json=None):
    """Onlyfilesystem+clock. CallerhasalreadywrittenReady; zero env/actor/RNG refs."""
    now=now or time.monotonic;pause=pause or time.sleep
    read_json=read_json or (lambda p:json.loads(Path(p).read_bytes()) if Path(p).is_file() else None)
    start=now() if ready_time is None else ready_time;root=Path(group_root)
    while True:
        if time.time()>=task['absolute_worker_deadline_epoch']:raise TimeoutError('Originalgroupownerdeadline reached duringbarrier; no independent extension')
        if read_json(root/'GROUP_STARTUP_ABORT.json') is not None:raise RuntimeError('Groupstartupaborted byoriginalparent; no independent retry')
        v=read_json(root/'GROUP_EVAL_START.json')
        if v is not None:
            assert v['group_id']==task['group_id'] and v['GPU_UUID']==task['GPU_UUID']
            assert v['all_members_ready'] is True and task['role'] in v['members']
            return dict(wait_wall_seconds=now()-start,barrier_start=v,no_actor_or_physics_or_RNG_calls=True)
        if now()-start>=maximum_seconds:raise TimeoutError('Groupbarrier900s; parentmustclosewholegroup ownscope')
        pause(.2)
