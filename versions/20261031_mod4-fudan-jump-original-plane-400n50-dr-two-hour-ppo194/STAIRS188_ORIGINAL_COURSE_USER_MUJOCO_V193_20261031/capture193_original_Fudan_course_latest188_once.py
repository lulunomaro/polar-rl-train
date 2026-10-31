"""New user display purpose: current188 PPO on its original Fudan stairs3 course.
Original cached rigid-body poses are recorded; no optimizer or budget writer.
"""
from pathlib import Path
import argparse,hashlib,io,json,os,runpy,sys,time,traceback

P=Path(__file__).resolve().parent
TASK=json.loads((P/'TASK193.json').read_bytes())
ROOT=Path(TASK['qualified188_package_root']);payload=ROOT/'payload'
OUT=P/'actual_capture';OUT.mkdir(exist_ok=False)
def put(name,value):
    with (OUT/name).open('x',encoding='utf8') as file:json.dump(value,file,indent=2,allow_nan=False)

started=time.time();deadline=started+840;real=ns=None
try:
    original=json.loads((payload/'job0/original_run_manifest.json').read_bytes())['env']
    for key in list(os.environ):
        if key.startswith('RM_') or key in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
    os.environ.update({key:str(value) for key,value in original.items() if key not in
        ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SPIN_STAGE','RM_SLOPE_INITIAL_ADMISSION')})
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
    sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','1','--seed','27',
              '--log_root',str(OUT/'unused_learning_logs')]
    ns=runpy.run_path(str(entry),run_name='capture193_config_only_no_old_main')
    import numpy as np
    import torch
    from spring_nominal_sdk_readback import tensor
    import stairs3_sdk188 as sdk
    cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=1;cfg.seed=27;cfg.sim.device='cuda:0';sdk.configure(cfg)
    real=sdk.Stairs3Mod4Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000
    vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.)
    obs=vec.get_observations();robot=real.scene['robot']
    assert real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8
    assert obs['policy'].shape==(1,35) and real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
    assert real.cfg.terminations.closure.params['threshold']==.002 and real.cfg.terminations.mimic.params['threshold']==.01
    level0=int(real.literal.terrain_levels[0]);type0=int(real.literal.terrain_types[0])
    put('ACTUAL193_ORIGINAL_STAIRS3_BEFORE_MODEL.json',dict(passed=True,geometry=sdk.DATA['geometry'],
        literal_reward_names=real.literal.reward_names,original_weights_per_second={key:value/.02 for key,value in real.literal.reward_scales.items()},
        original31_methods_and16_weights_unmodified=True,policy35_critic38=True,physics_us=2500,policy_us=20000,
        TGS=[32,4],nominal_gas_k=2000,nominal_gas_N=400,DR='original D0-D7 engineering recipe',
        initial_course_level=level0,initial_course_type=type0,fresh_N1_physics_not_live_training=True))
    source=Path(TASK['model_path']);stat=source.stat()
    with source.open('rb') as file:raw=file.read()
    assert len(raw)==TASK['model_bytes'] and hashlib.sha256(raw).hexdigest()==TASK['model_SHA']
    checkpoint=torch.load(io.BytesIO(raw),map_location='cuda:0',weights_only=True);del raw
    assert checkpoint['iter']==5065
    actor=torch.nn.Sequential(torch.nn.Linear(35,256),torch.nn.ELU(),torch.nn.Linear(256,128),torch.nn.ELU(),
                              torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,6)).to(real.device)
    weights={key.removeprefix('mlp.'):value for key,value in checkpoint['actor_state_dict'].items() if key.startswith('mlp.')}
    actor.load_state_dict(weights,strict=True);actor.eval()
    assert all(torch.equal(value,actor.state_dict()[key]) for key,value in weights.items())
    put('ACTUAL193_ONE_GPU_MODEL_LITERAL_MEAN_RESTORE.json',dict(passed=True,model_SHA=TASK['model_SHA'],
        source_iteration=5065,model_bytes=stat.st_size,new_GPU_file_reads=1,new_GPU_decodes=1,
        actor35_6_literal=True,optimizer_constructed=False,physics_or_model_injection=False))
    del weights,checkpoint
    frames=[];pending={};old_compute=real.termination_manager.compute
    def capture_terminal(*args,**kwargs):
        value=old_compute(*args,**kwargs)
        # Necessary new display reads reuse the current SDK rigid-body buffers.
        # No extra physics, actor, contact view, or random draw is performed.
        pending['position']=tensor(robot.data.body_pos_w)[0].detach().cpu().numpy().copy()
        pending['quat_xyzw']=tensor(robot.data.body_quat_w)[0].detach().cpu().numpy().copy()
        pending['root13']=tensor(robot.data.root_state_w)[0].detach().cpu().numpy().copy()
        pending['q30']=tensor(robot.data.joint_pos)[0].detach().cpu().numpy().copy()
        pending['flags']={name:bool(real.termination_manager.get_term(name)[0]) for name in real.termination_manager.active_terms}
        return value
    real.termination_manager.compute=capture_terminal
    tick0=int(real._integrated_contact.tick);fb0=int(real._feedback_100hz_tick)
    terminal_flags={};reward_sum=0.;completed=0
    with torch.inference_mode():
        for control in range(1000):
            if time.time()>=deadline:raise RuntimeError('Original finite capture bound reached before completion')
            pending.clear();action=actor(obs['policy'])
            command=real.command_manager.get_command('twist')[0].detach().cpu().numpy().copy()
            raw_action=action[0].detach().cpu().numpy().copy()
            obs,reward,done,extra=vec.step(action)
            assert set(pending)=={'position','quat_xyzw','root13','q30','flags'}
            assert np.isfinite(pending['position']).all() and np.isfinite(pending['quat_xyzw']).all()
            assert pending['position'].shape==(31,3) and pending['quat_xyzw'].shape==(31,4)
            frames.append(dict(pending,command=command,raw_action=raw_action))
            completed+=1;reward_sum+=float(reward[0])
            if bool(done[0]):terminal_flags=pending['flags'];break
    assert completed>0 and int(real._integrated_contact.tick)-tick0==8*completed
    assert int(real._feedback_100hz_tick)-fb0==2*completed
    position=np.stack([row['position'] for row in frames]).astype(np.float32)
    quat=np.stack([row['quat_xyzw'] for row in frames]).astype(np.float32)
    root=np.stack([row['root13'] for row in frames]).astype(np.float32)
    terrain=sdk.DATA['terrain'];vertices=np.asarray(terrain.vertices,dtype=np.float32).copy()
    vertices[:,:2]-=float(real.literal.cfg.terrain.border_size)
    faces=np.asarray(terrain.triangles,dtype=np.int32)
    lo=position[:,:,:2].reshape(-1,2).min(0)-1.4;hi=position[:,:,:2].reshape(-1,2).max(0)+1.4
    xy=vertices[faces,:2]
    keep=(xy.max(1)>=lo).all(-1)&(xy.min(1)<=hi).all(-1)
    selected=faces[keep];used,inverse=np.unique(selected,return_inverse=True)
    cropped_vertices=vertices[used];cropped_faces=inverse.reshape(-1,3).astype(np.int32)
    artifact=OUT/'ACTUAL193_LATEST188_BODY_POSES_AND_ORIGINAL_TERRAIN.npz'
    np.savez_compressed(artifact,body_position_w=position,body_quat_xyzw=quat,
        root13=root,q30=np.stack([row['q30'] for row in frames]),
        commands=np.stack([row['command'] for row in frames]),raw_action6=np.stack([row['raw_action'] for row in frames]),
        terrain_vertices=cropped_vertices,terrain_faces=cropped_faces,control=np.arange(1,completed+1,dtype=np.int32))
    with artifact.open('rb') as file:sha=hashlib.file_digest(file,'sha256').hexdigest()
    result=dict(passed=True,epoch=time.time(),model_SHA=TASK['model_SHA'],model_iteration=5065,
        controls=completed,physics_callbacks=completed*8,feedback=completed*2,seconds=completed*.02,
        body_names=list(robot.body_names),joint_names=list(robot.joint_names),body_quaternion='SDK xyzw',
        recording='Original PhysX control endpoint before automatic reset',terminal_flags=terminal_flags,
        first_episode_only=True,censored_at_20s_bound=not bool(terminal_flags),reward_sum=reward_sum,
        original_Fudan_STAIRS3_reward_and_course=True,initial_course_level=level0,initial_course_type=type0,
        original_terrain_geometry=sdk.DATA['geometry'],render_crop_only_actual_original_triangles=True,
        rendered_terrain_vertices=len(cropped_vertices),rendered_terrain_triangles=len(cropped_faces),
        artifact=dict(path=str(artifact),bytes=artifact.stat().st_size,SHA=sha),
        new_GPU_model_reads=1,NN_policy='same188 deterministic PPO mean',WM_or_Critic_forward=False,
        optimizer_steps=0,account_writes=0,actual_270_skill_claim=False,
        display_label='CLOSED188 TRAINING / NEW193 ORIGINAL FUDAN COURSE EVAL; not live learning')
    put('CAPTURE193_ACTUAL_RESULT.json',result)
    print(json.dumps({key:value for key,value in result.items() if key not in ('body_names','joint_names')}),flush=True)
except BaseException:
    put('ORIGINAL193_CAPTURE_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_automatic_retry=True))
    raise
finally:
    if real is not None:real.close()
    if ns is not None:ns['app'].close()
    put('APP193_CLOSED.json',dict(epoch=time.time(),closed=True))
