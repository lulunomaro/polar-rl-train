"""New necessary116 WM-only /118 controls closure false-stop calibration.
One checkpoint decode + one controls read. No actor/critic/optimizer/GPU/physics.
"""
from pathlib import Path
from types import SimpleNamespace
import ast
import hashlib
import json
import math
import os
import sys
import time
import traceback

S=Path(__file__).resolve().parent
R=S/'reports'
COUNTS=dict(control_raw_reads=0,checkpoint_decodes=0,checkpoint_integrity_passes=0)


def H(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_bytes())


def put(name,value):
    target=R/name
    assert not target.exists(), 'Do not replay consumed purpose: '+name
    target.write_bytes((json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8'))


def require(value,message):
    if not bool(value):
        raise ValueError(message)


def main():
    start=time.monotonic()
    require(os.environ.get('CUDA_VISIBLE_DEVICES')=='','explicit CPU-only purpose')
    index=read(S/'FROZEN_UNUSED121_SOURCE_AND_PURPOSE_INDEX.json')
    for row in index['source_files']:
        require(H(row['path'])==row['SHA'],'sealed new source '+row['path'])
    binding_path=S/'PURPOSE121_TYPED_WM_CLOSURE_BINDING.json'
    require(H(binding_path)==index['binding_SHA'],'new purpose binding SHA')
    q=read(binding_path);B=Path(q['source_payload'])
    require(q['formal_SHA']=='78f5840ec3db38a3fe2c8c16852b81a5bc7f02b445acd4a7901dafc7078d9976','only qualified116h1')
    require(H(q['manifest'])==q['manifest_SHA'],'actual116 full source manifest')
    for row in q['source_PY_rows']:
        require(H(B/row['relative'])==row['SHA'],'unchanged admitted source '+row['relative'])
    for row in q['additional_small_source_and_receipts']:
        require(H(row['path'])==row['SHA'],'typed source/receipt binding '+row['path'])
    qual=read(q['qualified116_CPU'])
    require(qual['passed'] and qual['model']['SHA']==q['formal_SHA'],'actual qualified116 initial CPU receipt')
    require(read(R/'SOURCE121_SYNTHETIC_TYPED_DOMAIN_AND_ACTUAL_ACTION_SEQUENCE_CPU.json')['passed_source_CPU_only'], 'necessary source fixtures before actual input/model')
    require(q['expected_controls']==431 and q['original_threshold_m']==.002 and q['original_grace_controls']==10,'actual118 and original guard')
    put('NEW121_PURPOSE_CONSUMED_BEFORE_RAW_OR_MODEL.json',dict(epoch=time.time(),purpose=q['purpose'],
        frozen_index_SHA=H(S/'FROZEN_UNUSED121_SOURCE_AND_PURPOSE_INDEX.json'),
        maximum_control_raw_reads=1,maximum_checkpoint_decodes=1,normal86_reads=0,
        no_Pi_Critic_optimizer_GPU_SDK_physics_SSH_account_or_GO=True,no_retry=True))
    import torch
    import psutil
    torch.set_num_threads(2)
    require(not torch.cuda.is_initialized(),'no CUDA before admission')
    proc=psutil.Process()
    put('NEW121_LOCAL_CPU_EXACT_PROCESS_IDENTITY.json',dict(epoch=time.time(),pid=proc.pid,
        creation=proc.create_time(),exe=proc.exe(),argv=proc.cmdline(),cwd=proc.cwd()))
    sys.path[:0]=[str(S),str(B/'source')]
    from wm_closure121_core import (anchor_errors,closure_stop,decode_records,evaluate,
        quat_apply_xyzw,summarize)
    from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel
    from supermimic_wheel_leg_v3.geometry import unflatten_state
    from own_step_differentiable_geometry_v1 import OwnStepWheelGeometry
    from compact_episode_static31_v1 import normalize_static31,FIELDS
    from private_phase_frame_v1 import decode as decode_private_frame

    producer=q['raw_control_producer'];rp=Path(producer['local_path']);before=rp.stat()
    require(before.st_size==producer['bytes'],'original118 control bytes')
    COUNTS['control_raw_reads']+=1
    raw=rp.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==producer['SHA'],'original118 control producer SHA')
    require((rp.stat().st_size,rp.stat().st_mtime_ns)==(before.st_size,before.st_mtime_ns),'raw changed during one read')
    rows=[json.loads(line) for line in raw.splitlines() if line.strip()];del raw
    data=decode_records(rows,q['expected_controls']);del rows
    contract=read(q['import_contract']);geom_doc=read(q['own_geometry'])
    joint_names=q['actual_joint_names'];body_names=q['actual_body_names']
    geometry=OwnStepWheelGeometry(contract,geom_doc,joint_names).to('cpu')
    require(list(geometry.body_names)==body_names,'actual SDK31body / own native FK order')
    closures=list(contract['closures'].items());names=[name for name,_ in closures]
    require(len(closures)==6,'original six closure pairs')
    indices0=torch.tensor([body_names.index(c['body0']) for _,c in closures])
    indices1=torch.tensor([body_names.index(c['body1']) for _,c in closures])
    anchors0=torch.tensor([c['anchor0_m'] for _,c in closures],dtype=torch.float32)
    anchors1=torch.tensor([c['anchor1_m'] for _,c in closures],dtype=torch.float32)
    closure=(indices0,indices1,anchors0,anchors1)
    # Execute only original parsed closure/grace functions on already recorded
    #31body snapshots. No IsaacLab imports, getters, callbacks or simulation.
    original_path=Path(q['original_physics_source'])
    original_tree=ast.parse(original_path.read_bytes().decode('utf-8'))
    fn_names={'_closure_cache','closure_errors','closure_broken','_past_spawn_grace'}
    nodes=[n for n in original_tree.body if isinstance(n,ast.FunctionDef) and n.name in fn_names]
    require({n.name for n in nodes}==fn_names,'original closure function set')
    ns=dict(torch=torch,CONTRACT=contract,quat_apply=quat_apply_xyzw,
        os=SimpleNamespace(environ={'RM_SPAWN_GRACE_STEPS':'10'}))
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(original_path),'exec'),ns)
    actual_age=torch.tensor([x['public_age'] for x in data['terminal']],dtype=torch.long)
    require(torch.equal(actual_age,torch.arange(1,q['expected_controls']+1)),'actual endpoint clock before auto-reset')
    env=SimpleNamespace(scene={'robot':SimpleNamespace(body_names=body_names,
        data=SimpleNamespace(body_pos_w=data['position'],body_quat_w=data['quaternion']))},
        num_envs=q['expected_controls'],device=torch.device('cpu'),episode_length_buf=actual_age)
    physical_errors=ns['closure_errors'](env)
    body_errors=torch.stack([physical_errors[name] for name in names],-1)
    reconstructed_stop=ns['closure_broken'](env,threshold=.002)
    state=unflatten_state(data['t'])
    with torch.inference_mode():
        g=geometry(state)
        actual_q_errors=anchor_errors(g['body_position'],g['body_rotation'],*closure)
    q_stop=closure_stop(actual_q_errors,actual_age)
    reconstructed_vs_cached=int((reconstructed_stop!=data['cached_closure']).sum())
    fk_vs_cached=int((q_stop!=data['cached_closure']).sum())
    body_pos_delta=(g['body_position']+data['origin'][:,None,:]-data['position']).abs().amax()
    curves=[]
    for i in range(len(actual_age)):
        curves.append(dict(control=i+1,public_age=int(actual_age[i]),
            actual_body_anchor_errors6_m=body_errors[i].tolist(),
            actual_q_FK_anchor_errors6_m=actual_q_errors[i].tolist(),
            actual_cached_closure=bool(data['cached_closure'][i]),
            original_body_reconstructed_stop=bool(reconstructed_stop[i]),
            actual_q_FK_stop=bool(q_stop[i]),
            phase=data['phases'][i]))
    put('NEW121_ACTUAL_BODY_ANCHOR_VS_ACTUAL_Q_FK_CLOSURE_ALL431.json',dict(
        closure_names=names,rows=curves,original_threshold_m=.002,original_grace_controls=10,
        reconstructed_body_stop_vs_cached_mismatch_count=reconstructed_vs_cached,
        actual_q_FK_stop_vs_cached_mismatch_count=fk_vs_cached,
        FK_vs_actual_body_position_max_abs_m=float(body_pos_delta),
        not_new_physics_precision_or_skill_gate=True))
    put('NEW121_TYPED_ACTUAL_DATA_ADMITTED_BEFORE_MODEL.json',dict(epoch=time.time(),
        control_raw_reads=1,actual_controls=len(actual_age),input_state127=True,static_xi31=True,
        original_400Hz_4callbacks_100Hz=True,actual_executed_action6_not_PD_target=True,
        auxiliary54_retains_actual_history_torque_last_processed6=True,
        episode_static_context_literal=True,static_context_fields=FIELDS,
        private4096_N1_age_exact=True,request200to1999_exact=True,no_actual_reset_crossing=True,
        actual_cached_closure_only_at431=True,original_body_stop_cached_mismatch_count=reconstructed_vs_cached,
        actual_q_FK_cached_mismatch_count=fk_vs_cached,
        source_body_closure_label_match=(reconstructed_vs_cached==0),
        continuity_max_abs_by_block={name:float(data['continuity'][a:b].max()) for name,a,b in
            [('position_m',0,3),('quaternion_wxyz',3,7),('worldV',7,10),('worldW',10,13),('q30',13,43),('dq30',43,73),('dynamic54',73,127)]},
        continuity_report_not_new_bitwise_physics_gate=True,
        no_model_read_before_this_gate=True))

    mp=Path(q['formal_local_path']);mst=mp.stat()
    require(mst.st_size==q['formal_bytes'],'qualified116 formal bytes')
    with mp.open('rb') as stream:
        COUNTS['checkpoint_integrity_passes']+=1
        require(hashlib.file_digest(stream,'sha256').hexdigest()==q['formal_SHA'],'qualified116 checkpoint integrity')
        stream.seek(0);COUNTS['checkpoint_decodes']+=1
        saved=torch.load(stream,map_location='cpu',weights_only=False)
    require(mp.stat().st_mtime_ns==mst.st_mtime_ns,'qualified formal changed')
    native=saved['UniSuperMimic_H1_test'];publication=saved['UniSuperMimic_publication'];args=native['args']
    require(native['iteration']==20809 and publication['world_updates']==208090 and publication['policy_updates']==19977,'qualified116 source header')
    rng=torch.random.get_rng_state().clone()
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(20261029)
        wm=AugmentedWheelLegWorldModel(context_dim=31,hidden=args['wm_hidden'],num_joints=30,auxiliary_dim=54,action_dim=6)
    wm.load_state_dict(native['wm'],strict=True);wm.eval()
    for parameter in wm.parameters():parameter.requires_grad_(False)
    require(all(torch.isfinite(x).all() for x in wm.state_dict().values()),'finite WM weights/norms')
    literal={k:v.detach().clone() for k,v in wm.state_dict().items()}
    del saved,native,publication
    put('NEW121_ONE_MODEL_DECODE_WM_ONLY_ADMISSION.json',dict(epoch=time.time(),counts=COUNTS,
        formal_SHA=q['formal_SHA'],iteration=20809,world_updates=208090,policy_updates=19977,
        only_WM_constructed_and_forwarded=True,no_Pi_Critic_optimizer_constructed_or_forwarded=True,
        actual_inherited_norm_buffers_loaded_strict=True,CPU_torch=str(torch.__version__),
        GPU_producer='Torch2.10cu128 with TF32 permitted; no bitwise CPU/GPU equivalence claim',
        CUDA_initialized=torch.cuda.is_initialized()))

    def deadline():
        require(time.monotonic()-start<480,'bounded CPU purpose')
    summaries={}
    for horizon in [1,8,32]:
        predictions=evaluate(wm,unflatten_state,normalize_static31,geometry,closure,data,horizon,deadline)
        partitions={name:summarize([r for r in predictions if r['phase']==name]) for name in
            ['standing_request_off','request_on','crosses_request_onset_separate']}
        summary=summarize(predictions)
        summary['by_request_phase']=partitions
        summary['contains_low_air']=summarize([r for r in predictions if r['contains_actual_contact_proven_low_air']])
        if horizon==1:
            summary['CPU_vs_saved_GPU_one_step_rootZ_max_abs_m']=max(r['CPU_saved_GPU_rootZ_abs_error_if_one_step'] for r in predictions)
        put('NEW121_HORIZON_'+str(horizon)+'_ALL_ACTUAL_ACTION_CLOSURE_PREDICTIONS.json',dict(
            horizon=horizon,summary=summary,rows=predictions,closure_names=names,
            only_first_state_true_then_open_loop=True,actual_executed6_and_actual_static_context_every_offset=True,
            no_policy_action_resampling=True,request_onset_crossing_reported_separately=True,
            first_input_support_unknown_not_relabelled_from_first_output=True))
        summaries[str(horizon)]=summary
        print(json.dumps(dict(stage='CPU_CLOSURE_HORIZON_DONE',horizon=horizon,
            windows=summary['windows'],predicted_stop_on_cached_nonclosure_windows=summary['predicted_closure_on_cached_nonclosure_window_count'])),flush=True)
    require(all(torch.equal(wm.state_dict()[k],v) for k,v in literal.items()),'WM/norm changed')
    require(torch.equal(rng,torch.random.get_rng_state()),'inference altered RNG')
    require(not torch.cuda.is_initialized(),'CPU purpose initialized CUDA')
    old_adapter=ast.parse((B/'source/native_fudan_step_adapter_candidate_v2.py').read_text(encoding='utf-8'))
    cls=next(x for x in old_adapter.body if isinstance(x,ast.ClassDef) and x.name=='OwnFudanStepMdp')
    fn=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='soft_termination')
    namespace=dict(torch=torch,math=math,decode_private_frame=decode_private_frame)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual116-soft-stop>','exec'),namespace)
    old_last=float(namespace['soft_termination'](None,tuple(x[-1:] for x in state),actual_age[-1:])[0])
    false_windows={h:s['predicted_closure_on_cached_nonclosure_window_count'] for h,s in summaries.items()}
    result=dict(epoch=time.time(),passed_execution=True,purpose=q['purpose'],counts=COUNTS,
        source_checkpoint_SHA=q['formal_SHA'],actual_case='118 frozenmean431controls/4.31s closure terminal',
        original_threshold_m=.002,original_grace_controls=10,actual_body_closure_cached_mismatch_count=reconstructed_vs_cached,
        actual_q_FK_cached_mismatch_count=fk_vs_cached,old116_stop_at_actual_last_state=old_last,
        summary=summaries,WM_and_norms_literal_unchanged=True,RNG_unchanged=True,CPU_seconds=time.monotonic()-start,
        CPU_torch=str(torch.__version__),no_Pi_Critic_optimizer_GPU_SDK_physics_SSH_account_or_GO=True,
        source120_naive_hard_stop_ready_for_use=False,
        evidence_of_predicted_stop_on_actual_cached_nonclosure_windows=any(false_windows.values()),
        limits=['One previously observed low-flight stand/charge trajectory; overlapping windows are not population trials.',
            'Actual body-anchor reconstruction, actual q-FK and predicted q-FK are reported separately.',
            'Counterfactual predicted state need not match actual terminal; predicted closure exceedance is model error/constraint evidence, not proof a physically executable action would fail.',
            'If body-label alignment differs, cached nonclosure versus predicted threshold is not an established physical false-positive label.',
            'No27cm/highspeed/generalWM accuracy or unique policy-failure cause proved.',
            'Valid takeoff/cross/landing process reward gap remains before any next learning; physical2mm guard unchanged.'])
    put('NEW121_WM_CLOSURE_FALSE_STOP_CALIBRATION_COMPLETE_ACTUAL.json',result)
    print(json.dumps(dict(passed=True,counts=COUNTS,seconds=result['CPU_seconds'],
        body_label_mismatch=reconstructed_vs_cached,qFK_label_mismatch=fk_vs_cached,
        false_stop_windows=false_windows,source120_ready=False)),flush=True)


if __name__=='__main__':
    try:
        main()
    except BaseException:
        put('NEW121_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),
            traceback=traceback.format_exc(),counts=COUNTS,no_retry=True,
            no_physics_GPU_training_or_account_action=True))
        raise
