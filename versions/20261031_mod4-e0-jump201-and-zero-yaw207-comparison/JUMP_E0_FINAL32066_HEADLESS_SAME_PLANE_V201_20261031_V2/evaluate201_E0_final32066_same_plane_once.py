"""One new final32066 deterministic actor rollout in the original MOD4 PhysX plant."""
from pathlib import Path
import hashlib,io,json,os,runpy,sys,time,traceback
P=Path(__file__).resolve().parent
TASK=json.loads((P/'TASK201.json').read_bytes());ROOT=Path(TASK['qualified197_package_root']);payload=ROOT/'payload'
OUT=P/'actual_capture';OUT.mkdir(exist_ok=False)
def put(n,v):
    with (OUT/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
deadline=time.time()+840;real=ns=None
try:
    original=json.loads((payload/'job0/original_run_manifest.json').read_bytes())['env']
    for key in list(os.environ):
        if key.startswith('RM_') or key in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
    os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SPIN_STAGE','RM_SLOPE_INITIAL_ADMISSION')})
    os.environ.update(RM_MOD4_USD=str(payload/'job0/assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',
        RM_KEEP_STD='1',RM_JUMP_SCRIPT_PROB='0',RM_GYRO_CURRICULUM='1',RM_HEADING_CMD='0',
        RM_HEIGHT_MIN='.23',RM_HEIGHT_MAX='.33',RM_EPISODE_S='20',RM_HIDDEN_DIMS='256,128,64',
        RM_VALUE_LOSS_COEF='2.0',RM_SCHEDULE='adaptive',RM_ENTROPY_COEF='.005',RM_DESIRED_KL='.01',
        RM_RESCUE_DEADLINE=str(deadline),RM_RESCUE_STOP_FILE=str(OUT/'UNREQUESTED_STOP.json'))
    os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
    kit=OUT/'kit_isolation';kit.mkdir();(kit/'data').mkdir();(kit/'DerivedDataCache').mkdir();(kit/'data/user.config.json').write_text('{}')
    os.environ['MOD4_188_OWN_KIT_ROOT']=str(kit);os.environ['MOD4_188_JOB_ROOT']=str(P)
    runtime=payload/'job0/runtime/isaac/mod4'
    sys.path[:0]=[str(P),str(ROOT),str(payload/'lib'),str(runtime),str(payload/'job0/runtime')]
    entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py'
    sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','1','--seed','27','--log_root',str(OUT/'unused_learning_logs')]
    ns=runpy.run_path(str(entry),run_name='capture201_config_only_no_old_main')
    import numpy as np
    import torch
    from spring_nominal_sdk_readback import tensor
    import jump194_sdk as sdk
    cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=1;cfg.seed=27;cfg.sim.device='cuda:0';sdk.configure(cfg)
    real=sdk.JumpMod4Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000
    vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.);obs=vec.get_observations();robot=real.scene['robot']
    assert real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8
    assert obs['policy'].shape==(1,35) and real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
    assert real.cfg.terminations.closure.params['threshold']==.002 and real.cfg.terminations.mimic.params['threshold']==.01
    put('ACTUAL201_LITERAL_JUMP_PLANE_BEFORE_MODEL.json',dict(passed=True,
        original_JUMP19_methods_config16_scales_no_edits=True,literal_reward_names=real.literal.reward_names,
        original_weights_per_second={k:v/.02 for k,v in real.literal.reward_scales.items()},
        original_clip_single=2.5,original_total_positive_clip=False,original_plane_mu_restitution=[.5,.5],
        binding=real.binding_receipt(),policy35_critic38=True,physics_us=2500,policy_us=20000,TGS=[32,4],
        nominal_gas_k=2000,nominal_gas_N=400,DR='D0white_v3 and D1-D7 engineering recipe',fresh_N1_physics=True))
    source=Path(TASK['model_path'])
    with source.open('rb') as f:raw=f.read()
    assert len(raw)==TASK['model_bytes'] and hashlib.sha256(raw).hexdigest()==TASK['model_SHA']
    ck=torch.load(io.BytesIO(raw),map_location='cuda:0',weights_only=True);del raw
    assert ck['iter']==32066 and ck['source_E0_SHA']==TASK['inputE0_SHA'] and ck['typed_E0_JUMP198_task']['reward_weights_and_functions_no_edits']
    actor=torch.nn.Sequential(torch.nn.Linear(35,256),torch.nn.ELU(),torch.nn.Linear(256,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,6)).to(real.device)
    weights={k.removeprefix('mlp.'):v for k,v in ck['actor_state_dict'].items() if k.startswith('mlp.')}
    actor.load_state_dict(weights,strict=True);actor.eval()
    assert all(torch.equal(v,actor.state_dict()[k]) for k,v in weights.items())
    put('ACTUAL201_ONE_GPU_MODEL_MEAN_RESTORE.json',dict(passed=True,model_SHA=TASK['model_SHA'],source_iteration=32066,
        new_GPU_file_reads=1,new_GPU_decodes=1,actor35_6_literal=True,optimizer_constructed=False,
        learned_STD_in_source_but_deterministic_mean_for_display=True,no_state_or_force_injection=True))
    del ck,weights
    frames=[];pending={};old_compute=real.termination_manager.compute;old_reward=real.original_jump_once
    def capture_terminal(*a,**kw):
        value=old_compute(*a,**kw)
        pending['position']=tensor(robot.data.body_pos_w)[0].detach().cpu().numpy().copy()
        pending['quat_xyzw']=tensor(robot.data.body_quat_w)[0].detach().cpu().numpy().copy()
        pending['root13']=tensor(robot.data.root_state_w)[0].detach().cpu().numpy().copy()
        pending['q30']=tensor(robot.data.joint_pos)[0].detach().cpu().numpy().copy()
        pending['flags']={n:bool(real.termination_manager.get_term(n)[0]) for n in real.termination_manager.active_terms}
        return value
    def capture_reward(*a,**kw):
        value=old_reward(*a,**kw)
        # Reuse the actual original reward's already-read contact tensor; no sensor/view call.
        pending['wheel_forces_z']=real.literal.contact_forces[0,real.literal.feet_indices,2].detach().cpu().numpy().copy()
        pending['flight_flag']=bool(real.literal.was_in_flight[0])
        return value
    real.termination_manager.compute=capture_terminal;real.original_jump_once=capture_reward
    tick0=int(real._integrated_contact.tick);fb0=int(real._feedback_100hz_tick);calls0=real.literal.calls
    endflags={};reward_sum=0.;completed=0
    with torch.inference_mode():
        for control in range(1000):
            assert time.time()<deadline,'Original finite capture bound reached'
            pending.clear();action=actor(obs['policy'])
            command=real.command_manager.get_command('twist')[0].detach().cpu().numpy().copy()
            raw_action=action[0].detach().cpu().numpy().copy()
            obs,reward,done,extra=vec.step(action)
            assert set(pending)=={'position','quat_xyzw','root13','q30','flags','wheel_forces_z','flight_flag'}
            assert pending['position'].shape==(31,3) and pending['quat_xyzw'].shape==(31,4)
            assert all(np.isfinite(pending[k]).all() for k in ('position','quat_xyzw','root13','q30','wheel_forces_z'))
            frames.append(dict(pending,command=command,raw_action=raw_action));completed+=1;reward_sum+=float(reward[0])
            if bool(done[0]):endflags=pending['flags'];break
    assert completed>0 and int(real._integrated_contact.tick)-tick0==8*completed
    assert int(real._feedback_100hz_tick)-fb0==2*completed and real.literal.calls-calls0==completed
    pos=np.stack([x['position'] for x in frames]).astype(np.float32);root=np.stack([x['root13'] for x in frames]).astype(np.float32)
    artifact=OUT/'ACTUAL201_FINAL32066_BODY_POSES_AND_PLANE.npz'
    # Exact original flat plane for display, no foreign step or old trajectory.
    vertices=np.array([[-20,-20,0],[20,-20,0],[20,20,0],[-20,20,0]],dtype=np.float32)
    faces=np.array([[0,1,2],[0,2,3]],dtype=np.int32)
    names=list(robot.body_names);wheels=[names.index('left_wheel'),names.index('right_wheel')]
    np.savez_compressed(artifact,body_position_w=pos,body_quat_xyzw=np.stack([x['quat_xyzw'] for x in frames]),
        root13=root,q30=np.stack([x['q30'] for x in frames]),commands=np.stack([x['command'] for x in frames]),
        raw_action6=np.stack([x['raw_action'] for x in frames]),wheel_contact_z=np.stack([x['wheel_forces_z'] for x in frames]),
        original_flight_flag=np.array([x['flight_flag'] for x in frames],dtype=np.bool_),
        terrain_vertices=vertices,terrain_faces=faces,control=np.arange(1,completed+1,dtype=np.int32))
    with artifact.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    contact=np.stack([x['wheel_forces_z'] for x in frames]);flight=np.array([x['flight_flag'] for x in frames])
    result=dict(passed=True,epoch=time.time(),model_SHA=TASK['model_SHA'],model_iteration=32066,
        controls=completed,physics_callbacks=completed*8,feedback=completed*2,seconds=completed*.02,
        body_names=names,joint_names=list(robot.joint_names),body_quaternion='SDK xyzw',
        recording='Original PhysX50Hz control endpoint before automatic reset',terminal_flags=endflags,
        first_episode_only=True,reward_sum=reward_sum,original_Fudan_JUMP_reward_and_plane=True,
        wheel_center_max_world_z_50Hz=pos[:,wheels,2].max(0).tolist(),
        original_contact_flight_flag_rows=int(flight.sum()),both_wheel_force_z_le1N_rows=int((contact<=1).all(1).sum()),
        contact_flags_not_jump_or_landing_certification=True,
        artifact=dict(path=str(artifact),bytes=artifact.stat().st_size,SHA=sha),
        new_GPU_model_reads=1,NN_policy='E0 branch final32066 deterministic PPO mean',WM_or_Critic_forward=False,
        optimizer_steps=0,account_writes=0,actual_270_skill_claim=False,
        display_label='CLOSED E0 BRANCH TRAINING / NEW201 SAME-PLANE HEADLESS EVAL')
    put('CAPTURE201_ACTUAL_RESULT.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('body_names','joint_names')}),flush=True)
except BaseException:
    put('ORIGINAL201_CAPTURE_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_automatic_retry=True));raise
finally:
    if real is not None:real.close()
    if ns is not None:ns['app'].close()
    put('APP201_CLOSED.json',dict(epoch=time.time(),closed=True))
