"""NEW necessary120 CPU purpose, using saved118 SMALL terminal publication only.
Compare original anchor-stop truth, own q-FK reconstruction and imagined soft stop.
No checkpoint, rawJSONL, NPZ, SDK, GPU, physics, SSH, optimizer or account action.
"""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,importlib.util,json,os,sys,time,traceback
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';B=T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029/payloads/seed27'
D=L/'native120_original_closure_vs_imagined_stop_CPU_review_v1';assert not D.exists();(D/'reports').mkdir(parents=True)
def H(b):return hashlib.sha256(b).hexdigest()
def save(n,v):
    with (D/'reports'/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    original=B/'job0/runtime/isaac/mod4/mod4_task.py';raw=original.read_bytes();tree=ast.parse(raw.decode('utf8'))
    names={'_closure_cache','closure_errors','closure_broken','_past_spawn_grace'};nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names];assert {x.name for x in nodes}==names
    snippets='\n\n'.join(ast.get_source_segment(raw.decode('utf8'),x) for x in nodes);(D/'ORIGINAL_CLOSURE_AND_GRACE_FUNCTIONS_EXACT_SOURCE.txt').write_text(snippets,encoding='utf8')
    source=B/'source/native_fudan_step_adapter_candidate_v2.py';module=ast.parse(source.read_text(encoding='utf8'));mdp=next(x for x in module.body if isinstance(x,ast.ClassDef) and x.name=='OwnFudanStepMdp');stop=next(x for x in mdp.body if isinstance(x,ast.FunctionDef) and x.name=='soft_termination')
    (D/'ORIGINAL116_IMAGINED_SOFT_TERMINATION_EXACT_SOURCE.txt').write_text(ast.get_source_segment(source.read_text(encoding='utf8'),stop),encoding='utf8')
    path=T/'H1_NATIVE116_LATEST_USER_MUJOCO_MOTION_WM_V118_20261029/reports/FROZEN118_SINGLE_CASE_AND_WM_DIAGNOSTIC_RETURNED_ACTUAL.json'
    save('SOURCE120_TYPED_NECESSARY_PURPOSE_CONSUMED.json',dict(epoch=time.time(),purpose='User says policy stands and charges untilclosure, notjump. Compare the genuine118 closure terminal with the116 analytic imagination stop before any further training.',cached_terminal_report=str(path),cached_report_reads_planned=1,original_physics_source_SHA=H(raw),original_MDP_source_SHA=H(source.read_bytes()),no_model_raw_JSONL_NPZ_SDK_GPU_or_SSH=True))
    cached_bytes=path.read_bytes();cached=json.loads(cached_bytes);result=cached['case']['result'];last=result['last_original_state'];assert cached['actual_waited_exit']==0 and result['last_termination_terms']['values']['closure']
    import torch
    torch.set_num_threads(2);assert not torch.cuda.is_initialized();sys.path.insert(0,str(B/'source'))
    from own_step_differentiable_geometry_v1 import OwnStepWheelGeometry,qmat
    from private_phase_frame_v1 import encode
    from native_fudan_step_adapter_candidate_v2 import OwnFudanStepMdp
    contract_path=B/'job0/assets/import_contract.json';geometry_path=B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json'
    contract=json.loads(contract_path.read_bytes());geometry=json.loads(geometry_path.read_bytes());body_names=result['body_names'];assert body_names==geometry['body_names']
    tensor=lambda x:torch.tensor(x,dtype=torch.float32)
    pos=tensor(last['body_position31_world'])[None];quat=tensor(last['body_quaternion31_sdk_xyzw'])[None]
    assert pos.shape==(1,31,3) and quat.shape==(1,31,4)
    def quat_apply_xyzw(q,v):
        xyz=q[...,:3];w=q[...,3:4];twice=2*torch.cross(xyz,v,dim=-1);return v+w*twice+torch.cross(xyz,twice,dim=-1)
    runenv=json.loads((B/'job0/original_run_manifest.json').read_bytes())['env'];grace=int(runenv.get('RM_SPAWN_GRACE_STEPS','10'))
    actual_env=SimpleNamespace(scene={'robot':SimpleNamespace(body_names=body_names,data=SimpleNamespace(body_pos_w=pos,body_quat_w=quat))},num_envs=1,device=torch.device('cpu'),episode_length_buf=torch.tensor([last['public_age']],dtype=torch.long))
    ns=dict(torch=torch,CONTRACT=contract,quat_apply=quat_apply_xyzw,os=SimpleNamespace(environ={'RM_SPAWN_GRACE_STEPS':str(grace)}));exec(compile(ast.Module(body=nodes,type_ignores=[]),str(original),'exec'),ns)
    actual_errors=ns['closure_errors'](actual_env);actual_stop=ns['closure_broken'](actual_env,threshold=.002)
    r=tensor(last['root13_sdk_xyzw']);qroot=torch.cat((r[6:7],r[3:6]));R=qmat(qroot)[None]
    assert abs(float(R[0,2,2])+float(last['projected_gravity_b'][2]))<1e-5,'recorded SDK xyzw and native R convention disagree'
    aux=torch.cat((tensor(last['contact_history18']).flatten(),tensor(last['applied_torque30']),tensor(last['physical_applied_processed6'])))[None];assert aux.shape==(1,54)
    state=(r[None,:3],R,r[None,7:10],r[None,10:13],tensor(last['q30'])[None],tensor(last['qd30'])[None],aux)
    fk=OwnStepWheelGeometry(contract,geometry,contract['joint_names'] if 'joint_names' in contract else list(contract['joints'])).to('cpu')
    # q30 uses actual runtime names, not dictionary insertion order.
    fresh=json.loads(next((T/'H1_NATIVE116_LATEST_USER_MUJOCO_MOTION_WM_V118_20261029/actual_case_text').glob('*FRESH_N1_SOURCE_SDK_RESET_GAS_BEFORE_FORWARD_ACTUAL.json')).read_bytes())
    fk=OwnStepWheelGeometry(contract,geometry,fresh['actual_names']).to('cpu');derived=fk(state)
    reconstructed={}
    for name,c in contract['closures'].items():
        i,j=body_names.index(c['body0']),body_names.index(c['body1']);p=derived['body_position'];rot=derived['body_rotation'];a0=tensor(c['anchor0_m']);a1=tensor(c['anchor1_m'])
        reconstructed[name]=(p[:,i]+(rot[:,i]@a0)-p[:,j]-(rot[:,j]@a1)).norm(dim=-1)
    model=OwnFudanStepMdp.__new__(OwnFudanStepMdp);frame=encode(torch.tensor([last['public_age']],dtype=torch.long),torch.tensor([0],dtype=torch.long));imagined_stop=model.soft_termination(state,frame)
    worst_actual=max(float(x) for x in actual_errors.values());worst_fk=max(float(x) for x in reconstructed.values())
    state_accesses=sorted({x.slice.value for x in ast.walk(stop) if isinstance(x,ast.Subscript) and isinstance(x.value,ast.Name) and x.value.id=='state' and isinstance(x.slice,ast.Constant)})
    output=dict(epoch=time.time(),passed_execution=True,cached_terminal_report_SHA=H(cached_bytes),cached_report_byte_reads=1,source_model_SHA=cached['case']['result'].get('source_identity',{}).get('SHA','see118sourcebinding'),actual_public_age=last['public_age'],actual_seconds=last['public_age']*.01,original_threshold_m=.002,original_spawn_grace_controls=grace,
        actual_cached_terminal_flags=result['last_termination_terms']['values'],actual_body_pose_anchor_errors_m={k:float(v) for k,v in actual_errors.items()},original_anchor_function_reconstructed_stop=bool(actual_stop.item()),max_actual_body_anchor_error_m=worst_actual,
        native_q_FK_anchor_errors_m={k:float(v) for k,v in reconstructed.items()},max_native_q_FK_anchor_error_m=worst_fk,q_FK_detects_original_threshold=worst_fk>.002,
        FK_vs_actual_body_position_max_m=float((derived['body_position']-pos).norm(dim=-1).max()),
        current116_imagined_soft_termination_probability=float(imagined_stop.item()),imagined_stop_certain=bool(imagined_stop.item()==1),soft_termination_state_tuple_indices_consumed=state_accesses,
        source_analytic_stop_has_no_closure_or_mimic_term=True,actual_original_closure_terminal_not_certainly_stopped_by_current_imagination=True,
        no_model_forward_or_optimizer_or_runtime_change=True,no_checkpoint_raw_NPZ_SDK_GPU_SSH_or_account_action=True,not_runtime_repair_or_unique_root_cause=True,
        limits=['Only one genuine saved terminal state, not a full rollout/firstsubstep timeline or population validation.','Not proof a particular32step imagined rollout reached this state or a measured policygradient was wrong.','q-FK and original PhysX body-anchor compliance may differ; do not declare them interchangeable.','Native127 lacks full31body poses; no fabricated missing physics state.','Physical2mm per-envguard unchanged; no newprecision or triangle gate.','Jump-process reward history gap remains separate and newlearning held.'])
    save('SOURCE120_ACTUAL_CLOSURE_TERMINAL_VS_IMAGINED_STOP_CPU_ACTUAL.json',output)
    print(json.dumps(dict(passed_execution=True,actual_cached_closure=True,actual_anchor_error_m=worst_actual,q_FK_anchor_error_m=worst_fk,imagined_soft_done=float(imagined_stop.item()),original_spawn_grace=grace)))
if __name__=='__main__':
    try:main()
    except BaseException:save('SOURCE120_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_model_raw_GPU_or_remote=True));raise
