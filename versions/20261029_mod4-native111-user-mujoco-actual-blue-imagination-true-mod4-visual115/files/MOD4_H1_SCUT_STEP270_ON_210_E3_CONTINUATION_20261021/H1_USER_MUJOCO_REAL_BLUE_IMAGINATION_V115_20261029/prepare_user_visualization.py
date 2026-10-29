"""New user-requested display purpose: recorded112 actual poses and frozen111 Pi+WM.

One existing controls read and one checkpoint decode for this visualization only.
No physical replay, training, optimizer, CUDA, SDK, network or account access.
"""
from pathlib import Path
import hashlib,json,os,sys,time,traceback
HERE=Path(__file__).resolve().parent
T=HERE.parent
R=HERE/'reports'
R.mkdir(exist_ok=True)
COUNTS=dict(controls_reads=0,checkpoint_decodes=0,checkpoint_integrity_passes=0)

def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def require(v,m):
    if not bool(v):raise ValueError(m)

def main():
    started=time.monotonic()
    require(os.environ.get('CUDA_VISIBLE_DEVICES')=='','explicit CPU-only inference')
    require(not (R/'USER_VISUALIZATION_PURPOSE_CONSUMED.json').exists(),'new purpose already consumed')
    q=read(T/'H1_NATIVE111_ACTUAL_ACTION_WM_FORWARD_CPU_V113_20261029/PURPOSE113_TYPED_BINDING_SOURCE_ONLY.json')
    B=Path(q['source_payload'])
    actual=T/'H1_NATIVE111_COHERENT_REWARD_FROZEN_MOTION_WM_N1_V112_20261029/actual_case_text'
    shapes_path=next(actual.glob('*ACTUAL_RENDER_GEOMETRY.json'))
    fresh_path=next(actual.glob('*FRESH_N1_SOURCE_SDK_RESET_GAS_BEFORE_FORWARD_ACTUAL.json'))
    render=read(shapes_path);fresh=read(fresh_path)
    require(H(q['manifest'])==q['manifest_SHA'],'actual111 manifest binding')
    for row in q['source_PY_rows']:require(H(B/row['relative'])==row['SHA'],'source '+row['relative'])
    require(H(q['qualified111_CPU'])==q['qualified111_CPU_SHA'],'existing qualified111 receipt')
    qual=read(q['qualified111_CPU'])
    require(qual['passed'] and qual['model']['SHA']==q['formal_SHA'],'qualified111 identity')
    require(H(q['actual_case_report'])==q['actual_case_report_SHA'],'actual112 receipt')
    case=read(q['actual_case_report'])
    require(case['actual_waited_exit']==0 and case['case']['passed'] and not case['errors'],'closed actual112 case')
    purpose=dict(epoch=time.time(),user_request='Open MuJoCo with translucent blue imagined robot like supplied image',
        actual_gray='Recorded112 actual PhysX terminal body poses, 100Hz,20s',
        blue='NEW frozen111 Pi+WM CPU closed-loop32-step imagination from actual112 states and actual ten-frame actor history',
        model_SHA=q['formal_SHA'],actual_control_producer=q['raw_control_producer'],
        maximum_controls_reads=1,maximum_checkpoint_decodes=1,normal86_reads=0,
        not_current114_rollout=True,not_live_physics=True,not_training_or_skill_acceptance=True,
        source_manifest_SHA=q['manifest_SHA'],geometry_source=str(shapes_path),geometry_SHA=H(shapes_path),
        expected_render='same fixed-world coordinates; no synthetic blue offset or motion script',
        explicit_user_GUI_exception_to_prior_no_GUI=True,CPU_neural_inference_only=True,
        source_files={p.name:H(p) for p in HERE.glob('*.py')})
    put('USER_VISUALIZATION_PURPOSE_CONSUMED.json',purpose)
    import numpy as np
    import torch,psutil
    torch.set_num_threads(2)
    require(not torch.cuda.is_initialized(),'no local neural CUDA')
    proc=psutil.Process()
    put('USER_VISUALIZATION_PREPARE_EXACT_IDENTITY.json',dict(pid=proc.pid,creation=proc.create_time(),exe=proc.exe(),argv=proc.cmdline(),cwd=proc.cwd()))
    sys.path.insert(0,str(B/'source'))
    from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel
    from supermimic_wheel_leg_v3.networks import Policy
    from supermimic_wheel_leg_v3.geometry import unflatten_state
    from native_fudan_step_adapter_candidate_v2 import OwnFudanStepReference,OwnFudanStepMdp
    row=q['raw_control_producer'];rp=Path(row['local_path']);st=rp.stat()
    require(st.st_size==row['bytes'],'actual controls byte count')
    COUNTS['controls_reads']+=1
    raw=rp.read_bytes();require(hashlib.sha256(raw).hexdigest()==row['SHA'],'actual controls producer SHA')
    records=[json.loads(line) for line in raw.splitlines() if line.strip()];del raw
    require(len(records)==2000 and [r['control'] for r in records]==list(range(1,2001)),'entire20s real case')
    require([r['age_for_action'] for r in records]==list(range(2000)),'unaltered original action clock')
    require(sum(bool(r['actual_original_done']) for r in records)==1 and records[-1]['actual_original_done'],'one final original termination')
    require(rp.stat().st_mtime_ns==st.st_mtime_ns,'recorded case changed')
    names=fresh['actual_names']
    provider=OwnFudanStepReference(read(B/'source/OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json')).bind_named_order(names,scope='source_CPU_fixture')
    mdp=OwnFudanStepMdp(provider,read(B/'job0/assets/import_contract.json'),read(B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json'),provider.metadata['actuator_leg_joint_names'])
    require(list(mdp.wheel_geometry.body_names)==render['body_names'],'actual/Pi FK body mapping')
    s=torch.tensor([r['packed127_for_action'] for r in records],dtype=torch.float32)
    xi=torch.tensor([r['xi31_for_action'] for r in records],dtype=torch.float32)
    frames=torch.tensor([r['packed_frame_for_action'] for r in records],dtype=torch.long)
    obs=torch.tensor([r['actor_obs86_for_action'] for r in records],dtype=torch.float32)
    require(s.shape==(2000,127) and xi.shape==(2000,31) and obs.shape==(2000,86),'typed state/context/actor observation')
    require(all(torch.isfinite(x).all() for x in (s,xi,obs)),'finite actual inputs')
    origins=np.asarray([r['env_origin3_world'] for r in records],dtype=np.float32)
    require(np.max(np.abs(origins-origins[0]))==0,'fixed recorded environment origin')
    pos=np.asarray([r['terminal_pre_reset']['state']['body_position31_world'] for r in records],dtype=np.float32)
    quat=np.asarray([r['terminal_pre_reset']['state']['body_quaternion31_sdk_xyzw'] for r in records],dtype=np.float32)
    bottom=np.asarray([r['terminal_pre_reset']['state']['metrics']['wheel_bottom_above_floor_m'] for r in records],dtype=np.float32)
    # SDK convention was explicitly captured as xyzw; drawing uses rotation matrices.
    require(pos.shape==(2000,31,3) and quat.shape==(2000,31,4),'actual31body data')
    require(np.max(np.abs(np.linalg.norm(quat,axis=-1)-1))<.01,'actual body quaternion norms')
    x,y,z,w=np.moveaxis(quat,-1,0)
    rot=np.stack((1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)),axis=-1).reshape(2000,31,3,3)
    terminal=torch.tensor([r['terminal_packed127_same_point'] for r in records],dtype=torch.float32)
    terminal_R=unflatten_state(terminal)[1].numpy()
    root_rotation_error=float(np.abs(rot[:,0]-terminal_R).max())
    require(root_rotation_error<1e-3,'recorded SDK body quaternion convention differs from bound native world orientation')
    put('ACTUAL_INPUTS_AND_DRAW_MAPPING_ADMITTED_BEFORE_MODEL.json',dict(rows=2000,actual_bodies=render['body_names'],actual_joint_order=names,raw_read_count=1,body_quaternion_convention='recorded SDK xyzw',source_context='actual xi31 at each branch start',not_resimulated=True))
    mp=Path(q['formal_local_path']);mst=mp.stat();require(mst.st_size==q['formal_bytes'],'native111 formal bytes')
    with mp.open('rb') as f:
        COUNTS['checkpoint_integrity_passes']+=1
        require(hashlib.file_digest(f,'sha256').hexdigest()==q['formal_SHA'],'trusted formal full integrity')
        f.seek(0);COUNTS['checkpoint_decodes']+=1;saved=torch.load(f,map_location='cpu',weights_only=False)
    require(mp.stat().st_mtime_ns==mst.st_mtime_ns,'native source changed')
    native=saved['UniSuperMimic_H1_test'];args=native['args']
    require(native['iteration']==18597 and args['hist']==10 and args['goal_frames']==10,'original native111 contract')
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(20260928)
        wm=AugmentedWheelLegWorldModel(context_dim=31,hidden=args['wm_hidden'],num_joints=30,auxiliary_dim=54,action_dim=6)
        pi=Policy(86,1460,hist=10,z_dim=args['z_dim'],num_joints=6,hidden=args['policy_hidden'])
    wm.load_state_dict(native['wm'],strict=True);pi.load_state_dict(native['pi'],strict=True)
    wm.eval();pi.eval()
    for model in (wm,pi):
        for p in model.parameters():p.requires_grad_(False)
        require(all(torch.isfinite(v).all() for v in model.state_dict().values()),'finite frozen parameter/norm')
    literal=[{k:v.clone() for k,v in model.state_dict().items()} for model in (wm,pi)]
    del saved,native
    starts=np.arange(1,1968,5,dtype=np.int64)
    histories=torch.stack([obs[torch.arange(max(0,int(k)-9),int(k)+1).clamp_min(0)] if k>=9 else obs[torch.arange(int(k)-9,int(k)+1).clamp_min(0)] for k in starts])
    pred_pos=[];pred_rot=[];pred_bottom=[]
    max_action_match=0.
    with torch.inference_mode():
        for begin in range(0,len(starts),96):
            ids=starts[begin:begin+96];state=unflatten_state(s[ids].clone());hist=histories[begin:begin+len(ids)].clone();f=frames[ids].clone();ctx=xi[ids].clone();normal=mdp.normalize_context(ctx)
            pp=[];pr=[];pb=[]
            for h in range(32):
                action=pi(hist,mdp.goal(f,10)).clamp(-6,6)
                if h==0:
                    actual_mean=torch.tensor([records[int(k)]['mean6'] for k in ids],dtype=torch.float32).clamp(-6,6)
                    max_action_match=max(max_action_match,float((action-actual_mean).abs().max()))
                state=wm.step(state,action,normal);f=f+1
                geom=mdp.wheel_geometry(state)
                pp.append(geom['body_position'].cpu().numpy()+origins[0]);pr.append(geom['body_rotation'].cpu().numpy());pb.append(geom['low'][...,2].cpu().numpy())
                newobs=mdp.add_noise(mdp.obs(state,action,ctx,f))
                hist=torch.cat((hist[:,1:],newobs[:,None]),1)
                require(time.monotonic()-started<480,'finite display extraction budget')
            pred_pos.append(np.stack(pp,axis=1));pred_rot.append(np.stack(pr,axis=1));pred_bottom.append(np.stack(pb,axis=1))
            print(json.dumps(dict(stage='DISPLAY_BLUE_POLICY_ROLLOUT',branches_done=begin+len(ids),branches_total=len(starts))),flush=True)
    for model,old in zip((wm,pi),literal):require(all(torch.equal(model.state_dict()[k],v) for k,v in old.items()),'display changed saved model/norms')
    require(not torch.cuda.is_initialized(),'display preparation initialized CUDA')
    pp=np.concatenate(pred_pos);pr=np.concatenate(pred_rot);pb=np.concatenate(pred_bottom)
    require(np.isfinite(pp).all() and np.isfinite(pr).all(),'nonfinite blue pose')
    target=HERE/'USER_ACTUAL112_AND_BLUE111_DISPLAY_POSES.npz'
    np.savez_compressed(target,actual_position=pos,actual_rotation=rot,actual_wheel_bottom=bottom,blue_position=pp,blue_rotation=pr,blue_wheel_bottom=pb,branch_input_control=starts,origin=origins[0])
    out=HERE/'DISPLAY_RECORDED_SHAPES.json';out.write_text(json.dumps(render,allow_nan=False),encoding='utf8')
    put('USER_DISPLAY_DATA_COMPLETE.json',dict(passed=True,epoch=time.time(),CPU_seconds=time.monotonic()-started,read_counts=COUNTS,
        pose_file=dict(path=str(target),bytes=target.stat().st_size,SHA=H(target)),shape_file=dict(path=str(out),bytes=out.stat().st_size,SHA=H(out)),
        actual_case='112 frozen111 mean policy,2000controls20s; recordedPhysX,not MuJoCo dynamics',actual_source_SHA=q['formal_SHA'],
        blue='frozen111 Pi+WM closed-loop32steps; actual ten observation frames at branch start; no future actual actions or state injection',
        blue_branch_count=len(starts),blue_dt=.01,actual_dt=.01,blue_start_stride_controls=5,blue_horizon_seconds=.32,
        first_action_CPU_vs_recorded_GPU_max_abs=max_action_match,actual_root_rotation_mapping_max_abs=root_rotation_error,CPU_torch=str(torch.__version__),CPU_GPU_bitwise_equivalence_not_claimed=True,
        models_and_norms_literal_unchanged=True,critic_and_optimizer_constructed=False,physical_steps=0,network_calls=0,
        display_is_prior_case_not114=True,actual_true270_success=False))
    print(json.dumps(dict(passed=True,display_poses=str(target),branches=len(starts),seconds=time.monotonic()-started)),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException:
        put('USER_VISUALIZATION_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),counts=COUNTS,no_old_once_replay=True));raise
