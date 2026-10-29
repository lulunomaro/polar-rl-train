"""New candidate source checks only. No checkpoint/raw/USD/NPZ or learned forward."""
from pathlib import Path
import ast,copy,hashlib,json,os,sys,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';B=N/'payloads/seed27'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
    prep=read(R/'NEW116_ONE_TYPED_REWARD_PAYLOAD_PREPARED_SOURCE_ONLY.json');c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');task=read(B/'job0/TASK.json')
    manifest=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');rows={r['relative']:r for r in manifest['files']}
    assert H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')==prep['manifest_SHA'] and task==prep['task']
    for rel,sha in c['approved_python'].items():assert H(B/rel)==sha==rows[rel]['SHA'];ast.parse((B/rel).read_bytes())
    assert set(c['approved_python'])=={p.relative_to(B).as_posix() for p in B.rglob('*.py')}
    assert all(rows[k]['SHA']==v for k,v in c['protected_current88C_files'].items())
    sys.path[:0]=[str(B),str(B/'source')]
    from native_flat90_source_guard_v1 import validate_task_go
    from native116_command_reward_pins_v1 import SOURCE_PINS
    go=copy.deepcopy(task);go.update(payload_manifest_SHA=prep['manifest_SHA'],num_envs=4096,max_parent_seconds=3900,exit_headroom_seconds=300)
    validate_task_go(task,go,prep['manifest_SHA']);rejected=[]
    for field in task['fudan_step_task']['command_reward116']:
        bad=copy.deepcopy(go);bad['fudan_step_task']['command_reward116'][field]='WRONG'
        try:validate_task_go(task,bad,prep['manifest_SHA'])
        except (ValueError,AssertionError,TypeError):rejected.append(field)
        else:raise AssertionError('unbound command reward '+field)
    for field in ('source_SHA','source_progress','source_qualification_kind','native_reference_SHA','native_learning_seed'):
        bad=copy.deepcopy(go);bad[field]='WRONG'
        try:validate_task_go(task,bad,prep['manifest_SHA'])
        except (ValueError,AssertionError,TypeError):rejected.append(field)
        else:raise AssertionError('unbound source '+field)
    import torch
    torch.set_num_threads(2)
    from native_fudan_step_adapter_candidate_v2 import OwnFudanStepReference,OwnFudanStepMdp
    from private_phase_frame_v1 import encode
    doc=read(B/task['native_reference_relative']);provider=OwnFudanStepReference(doc).bind_named_order(doc['joint_names'],scope='source_CPU_fixture')
    mdp=OwnFudanStepMdp(provider,read(B/'job0/assets/import_contract.json'),read(B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json'))
    poses=read(B/'job0/runtime/isaac/mod4/reset_bank.json')['poses'];n=len(poses)
    q=torch.tensor([[r['joint_pos'].get(name,0.) for name in provider.names] for r in poses],dtype=torch.float32)
    root=torch.zeros(n,3);root[:,2]=torch.tensor([r['root_height_m'] for r in poses]);root[:,0]=.056
    R0=torch.eye(3).expand(n,-1,-1);v=torch.zeros(n,3);aux=torch.zeros(n,54);aux[:,:18].reshape(n,3,2,3)[...,:,2]=100.
    state=(root,R0,v,v,q,torch.zeros_like(q),aux);frame=encode(torch.full((n,),300,dtype=torch.long),torch.zeros(n,dtype=torch.long));a=torch.zeros(n,6)
    first=mdp.objective_terms(state,frame,a,a);root2=root.clone();root2[:,0]=.2;second=mdp.objective_terms((root2,*state[1:]),frame,a,a)
    assert torch.isfinite(first['total']).all() and torch.equal(first['total'],sum(first['selected_optimization_terms'].values()))
    assert torch.all(second['total']>=first['total']-2e-7)
    assert torch.equal(first['selected_optimization_terms']['both_wheel_height_270_with_forward_command'],torch.zeros(n))
    from reward116_precontrol_current_pose_readback_v1 import check
    gpu_helper_fixture=check(mdp,state)
    entry=ast.parse((B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py').read_bytes())
    literals={n.arg:n.value.value for n in ast.walk(entry) if isinstance(n,ast.keyword) and n.arg in ('source_reference_artifact_SHA','private_phase_frame_source_SHA','real_callback_counter_source_SHA') and isinstance(n.value,ast.Constant)}
    assert literals['source_reference_artifact_SHA']==SOURCE_PINS['producer']['reference_artifact_SHA']==task['native_reference_SHA']
    assert literals['private_phase_frame_source_SHA']==H(B/'source/private_phase_frame_v1.py') and literals['real_callback_counter_source_SHA']==H(B/'h1_step270_sdk_runtime_candidate.py')
    assert not torch.cuda.is_initialized()
    result=dict(passed=True,epoch=time.time(),negative_fields_rejected=rejected,negative_count=len(rejected),own_FK_bank_poses=n,
        own_FK_stationary_height_bonus_zero=True,minimum_supported_floor_approach_delta=float((second['total']-first['total']).min()),
        source_GPU_readback_helper_CPU_fixture=gpu_helper_fixture,source_producer_pins=literals,
        current_reference_and_input_producer_derived_from_actual_qualified114=True,approved_source_Python=len(c['approved_python']),
        PT_raw_USD_NPZ_reads=0,no_learned_network_forward_or_physics=True,no_actual_target_SDK_GPU_or_GO=True)
    put('SOURCE116_PREINSTALL_TASK_GO_OWN_FK_COUNTEREXAMPLE_CPU_ACTUAL.json',result)
    print(json.dumps(dict(passed=True,negative_checks=len(rejected),own_FK_poses=n,actual_input114=task['source_SHA'])))
if __name__=='__main__':
    try:main()
    except BaseException:put('SOURCE116_PREINSTALL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_models_or_remote=True));raise
