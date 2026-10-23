from pathlib import Path
import ast,hashlib,json,time
OLD=Path(__file__).resolve().parent;T=OLD.parent;W=T.parent;D=T/'MOE_SMALL_CURB_CONTACT_REPLAY_20261024';D.mkdir();R=D/'reports';R.mkdir();PLAYER=W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def write(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8') as f:f.write(s)
run=PLAYER/'player/rm7v7_moe_runs/1792775317859666200';snap=[]
for name in ('INTERACTIVE_STARTED.json','INTERACTIVE_CURRENT.json'):
 p=run/name;raw=p.read_bytes();dest=D/('HUMAN_'+name);dest.write_bytes(raw);snap.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),captured_path=str(dest)))
put('HUMAN_SMALL_CURB_FLY_AND_TILT_FEEDBACK_ACTUAL.json',dict(epoch=time.time(),human_feedback='我测试了，平地走遇到一些小坎，车会直接飞起来然后失稳',last_player_snapshot=json.loads((D/'HUMAN_INTERACTIVE_CURRENT.json').read_bytes()),snapshots=snap,scope='Only started metadata and last coarse current packet were retained; no original control history, XYZ, contact forces or full flight trajectory. Do not claim exact human replay.',protocol='New independent full-CAD normal-driving small-contact diagnostic on remote4090 host. Primary MuJoCo3.14/ORT1.30 CPU matching local package versions, TorchCUDA frozen references on4090; auto/fixedE0/fixedW35 x0.6/1.2m/s with original10ms command ramp. Stop at original flat route endpoint or original UI fall, at most500controls. Record every0.5ms physics callback contacts/wrenches/control/wheel velocity/root state, no policy update or physics assist.',official_package_sources=['https://pypi.org/project/mujoco/3.14.0/','https://pypi.org/project/onnxruntime/1.30.0/'],no_local_policy_or_physics_test=True,no_training_or_budget_change=True))
source=(OLD/'moe_matched_player_cuda_worker_v1.py').read_text('utf8');prefix=source[:source.index(' cases=[];start=time.monotonic()')]
prefix=prefix.replace('import numpy as np,torch,mujoco','import numpy as np,torch,mujoco,onnxruntime as ort\n assert mujoco.__version__==\'3.14.0\' and ort.__version__==\'1.30.0\'\n ort.disable_telemetry_events()')
prefix=prefix.replace("self.path=Path(path);self.input_width=35;self.last=None","self.path=Path(path);self.input_width=35;self.last=None;self.sessions={role:ort.InferenceSession(str(B/'policy'/(('hybrid_moe' if role=='auto' else role)+'.onnx')),providers=['CPUExecutionProvider']) for role in ('auto','E0','W35')}")
a="raw=options[:,choice].clamp(-6,6);self.last=dict(observation=x[0].cpu().numpy(),logits=logits[0].cpu().numpy(),gate_choice=gate_choice,choice=choice,expert_actions=options[0].clamp(-6,6).cpu().numpy())\n   return raw[0].cpu().numpy()"
b="raw=self.sessions[self.variant].run(['action'],{'observation':x.cpu().numpy()})[0][0];candidate=options[0].clamp(-6,6).cpu().numpy();error=np.max(np.abs(candidate-np.clip(raw,-6,6)),axis=1);actual_choice=int(error.argmin()) if self.variant=='auto' else choice;self.last=dict(observation=x[0].cpu().numpy(),logits=logits[0].cpu().numpy(),gate_choice=gate_choice,choice=actual_choice,expert_actions=candidate,CUDA_reference_parity_error=float(error[actual_choice]))\n   return raw"
assert prefix.count(a)==1;prefix=prefix.replace(a,b)
prefix=prefix.replace("mujoco_version=mujoco.__version__,numpy_version=np.__version__","mujoco_version=mujoco.__version__,onnxruntime_version=ort.__version__,primary_policy_backend='ORT CPUExecutionProvider, same package versions as human Windows player; CUDA4090 frozen actor/gate references only',numpy_version=np.__version__")
body=r'''
 cases=[];start=time.monotonic();real_step=mujoco.mj_step;physics=[];contacts=[];names={};physics_index=0
 tire_ids=[mujoco.mj_name2id(sim.model,mujoco.mjtObj.mjOBJ_GEOM,n) for n in ('left_tire','right_tire')]
 def instrumented(model,data,*args,**kwargs):
  nonlocal physics_index
  real_step(model,data,*args,**kwargs);physics_index+=1
  count=[0,0];normal_sum=[0.,0.];ground_count=0;max_force=0.;max_geom=-1
  for j in range(data.ncon):
   c=data.contact[j];g1=int(c.geom1);g2=int(c.geom2);b1=int(model.geom_bodyid[g1]);b2=int(model.geom_bodyid[g2])
   if not ((b1==0) != (b2==0)):continue
   robot=g2 if b1==0 else g1;ground=g1 if b1==0 else g2;wrench=np.zeros(6);mujoco.mj_contactForce(model,data,j,wrench);ground_count+=1
   for g in (g1,g2):
    if g not in names:names[g]=dict(name=mujoco.mj_id2name(model,mujoco.mjtObj.mjOBJ_GEOM,g),body=mujoco.mj_id2name(model,mujoco.mjtObj.mjOBJ_BODY,int(model.geom_bodyid[g])))
   f=float(abs(wrench[0]));
   if f>max_force:max_force=f;max_geom=ground
   for k,g in enumerate(tire_ids):
    if robot==g:count[k]+=1;normal_sum[k]+=f
   contacts.append([physics_index,g1,g2,float(c.dist),*c.pos.copy(),*c.frame.copy(),*wrench])
  rot=data.xmat[sim.chassis_id].reshape(3,3);upright=float(rot[2,2]);wheels=[float(data.qvel[sim.qvel[n]]) for n in ('left_wheel_spin','right_wheel_spin')]
  physics.append([float(data.time),*data.qpos[:3].copy(),*data.qvel[:6].copy(),upright,*wheels,*count,*normal_sum,ground_count,max_force,max_geom,*data.ctrl.copy(),*data.actuator_force.copy(),*data.actuator_velocity.copy()])
 mujoco.mj_step=instrumented
 for variant in ('auto','E0','W35'):
  for target in (.6,1.2):
   name=variant+'_vx_'+str(target).replace('.','p');sim.reset_route('flat_run');actual_policy.variant=variant;sim.select_skill(0);initial=np.r_[sim.data.qpos.copy(),sim.data.qvel.copy()];initial_SHA=hashlib.sha256(initial.tobytes()).hexdigest();physics=[];contacts=[];physics_index=0;rows=[];obs=[];logits=[];choice=[];qpos=[];qvel=[];actions=[];vx=0.;fault=None;boundary=None
   with torch.inference_mode():
    for i in range(500):
     vx+=float(np.clip(target-vx,-.008,.008));sim.command.vx=vx;sim.command.wz=0.;sim.step_control();health=sim.health();assert health['finite'];v=np.zeros(6);mujoco.mj_objectVelocity(sim.model,sim.data,mujoco.mjtObj.mjOBJ_XBODY,sim.chassis_id,v,1);last=actual_policy.last;rows.append([float(sim.data.time),vx,float(v[3]),health['upright_cos'],float(sim.base_position[2]),health['closure_error_m'],health['mimic_error_rad'],last['CUDA_reference_parity_error']]);obs.append(last['observation']);logits.append(last['logits']);choice.append([last['gate_choice'],last['choice']]);qpos.append(sim.data.qpos.copy());qvel.append(sim.data.qvel.copy());actions.append(sim.last_action.copy())
     if health['upright_cos']<.60 or sim.base_position[2]<.12:fault=dict(control=i+1,health=health);break
     if sim.base_position[0]>-5.5:boundary=dict(control=i+1,reason='Original flat route endpoint reached; later wall/terrain not included in small-curb classification');break
     assert time.monotonic()-start<600,'Finite contact experiment duration'
   path=O/(name+'.npz');np.savez_compressed(path,state=np.asarray(rows),observation=np.asarray(obs),logits=np.asarray(logits),choices=np.asarray(choice),qpos=np.asarray(qpos),qvel=np.asarray(qvel),action=np.asarray(actions),physics=np.asarray(physics,dtype=np.float64),contacts=np.asarray(contacts,dtype=np.float64).reshape(-1,22),initial_qpos_qvel=initial)
   r=np.asarray(rows);p=np.asarray(physics);ch=np.asarray(choice)[:,1];summary=dict(case=name,variant=variant,target_vx=target,controls=len(rows),physics_callbacks=len(physics),expected_callbacks=len(rows)*sim.decimation,initial_state_SHA=initial_SHA,fault=fault,route_endpoint_stop=boundary,max_root_z_m=float(p[:,3].max()),min_root_z_m=float(p[:,3].min()),max_root_upward_v_m_s=float(p[:,6].max()),max_contact_normal_force_N=float(p[:,18].max()),both_tire_no_contact_callbacks=int(((p[:,13]+p[:,14])==0).sum()),max_tilt_deg=float(np.degrees(np.arccos(np.clip(p[:,10].min(),-1,1)))),expert_switches=int((ch[1:]!=ch[:-1]).sum()),selected_expert_counts={'E0':int((ch==0).sum()),'W35':int((ch==1).sum())},max_CUDA_reference_parity_error=float(r[:,7].max()),artifact=dict(path=str(path),bytes=path.stat().st_size,SHA=H(path)),last_health=sim.health());assert summary['physics_callbacks']==summary['expected_callbacks'];put(name+'_COMPLETE.json',summary);cases.append(summary)
 assert len({x['initial_state_SHA'] for x in cases})==1
 assert all(torch.equal(w.cpu(),frozen[role][k]) for role,sd in actors.items() for k,w in sd.items())
 put('CONTACT_AND_PHYSICS_COLUMNS.json',dict(contact_columns=['physics_index','geom1','geom2','dist','posX','posY','posZ']+[f'frame{i}' for i in range(9)]+[f'local_wrench{i}' for i in range(6)],physics_columns=['time','x','y','z','vx','vy','vz','wx','wy','wz','upright','left_wheel_rad_s','right_wheel_rad_s','left_tire_contacts','right_tire_contacts','left_tire_normal_N','right_tire_normal_N','ground_contact_count','max_ground_normal_N','max_ground_geom']+[f'ctrl{i}' for i in range(6)]+[f'actuator_force{i}' for i in range(6)]+[f'actuator_velocity{i}' for i in range(6)],geometry_names=names,contact_scope='Actual mj_step followed by mj_contactForce readback at every0.5ms step, cached solver contact frame; no fresh mj_forward or force injection. Contacts and velocities may represent solver/integration stages; do not treat an approximate power integral as an exact energy proof.',no_contact_callback_missing=True))
 put('FINAL.json',dict(epoch=time.time(),passed_frozen_execution=True,cases=cases,all6_initial_physical_states_literal_SHA_equal=True,actor9_STD_unchanged=True,gate_not_updated=True,no_optimizer_training_or_budget_write=True,primary_MuJoCo_3_14_ORT_1_30_on_remote4090_host=True,no_local_simulation=True,not_exact_original_human_command_history=True,elapsed_seconds=time.monotonic()-start))
 print(json.dumps(dict(passed=True,cases=len(cases),faults=sum(x['fault'] is not None for x in cases))))
if __name__=='__main__':
 try:main()
 except BaseException:put('ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay=True));raise
'''
write(D/'small_curb_actual_contact_worker_v1.py',prefix+body)
deploy=(OLD/'deploy_moe_router_matched_4090_unused_once.py').read_text('utf8');deploy=deploy.replace('moe_matched_player_cuda_worker_v1.py','small_curb_actual_contact_worker_v1.py').replace('MoE_matched_player_4090_2410v1','MoE_small_curb_contact_4090_2410v1').replace('4090_MATCHED_','4090_SMALL_CURB_').replace('MOE_MATCHED_4090_PAYLOAD.zip','SMALL_CURB_4090_PAYLOAD.zip').replace("local=D/'actual_4090'","local=D/'actual_contact_4090'")
deploy=deploy.replace("speeds_m_s=[.3,.6,1.2,-.6]","speeds_m_s=[.6,1.2]")
deploy=deploy.replace("probe=json.loads((R/'4090_RESOURCE_AND_EXISTING_PACKAGE_PROBE_ACTUAL.json').read_bytes())","probe=json.loads((D.parent/'MOE_ROUTING_MATCHED_4090_DIAGNOSTIC_20261024/reports/4090_RESOURCE_AND_EXISTING_PACKAGE_PROBE_ACTUAL.json').read_bytes())")
deploy=deploy.replace("checkpoints={role:dict(relative='checkpoints/'+role+'.pt',**manifest['sources'][role]) for role in ('E0','W35','gate148')}","checkpoints={role:dict(relative='/home/lc01/Zonglin Li/zonglin2/tasks/MoE_matched_player_4090_2410v1/checkpoints/'+role+'.pt',**manifest['sources'][role]) for role in ('E0','W35','gate148')},primary_package_versions={'mujoco':'3.14.0','onnxruntime':'1.30.0'},primary_actor='ONNX CPU, matching local player; CUDA frozen gate/actor reference',route_endpoint_x=-5.5,actual_contact_sample_dt=.0005")
start=deploy.index("  z.write(worker,'worker.py');");end=deploy.index(" put('4090_SMALL_CURB_DEPLOY_STARTED_ACTUAL.json'",start)
pack="""  z.write(worker,'worker.py');z.write(D/'CONFIG.json','CONFIG.json');z.write(PLAYER/'policy/manifest.json','policy/manifest.json')
  for role in ('hybrid_moe','E0','W35'):z.write(PLAYER/'policy'/(role+'.onnx'),'policy/'+role+'.onnx')
  for name in ('sim_runtime.py','current_sim.py','current_moe_sim.py','rm7v7_moe_sim.py','runtime_config.json','routes.json','rm7v7_latest_moe.xml'):
   z.write(PLAYER/'player'/name,'player/'+name)
  for name in ('reset_bank.json','import_contract.json'):z.write(PLAYER/'player/src_snapshot'/name,'player/src_snapshot/'+name)
"""
deploy=deploy[:start]+pack+deploy[end:]
needle=" z.extractall(base)\n\nenv=dict"
install=""" z.extractall(base)
os.symlink('/home/lc01/Zonglin Li/zonglin2/tasks/MoE_matched_player_4090_2410v1/player/assets',base/'player/assets',target_is_directory=True)
assert (base/'player/assets').is_dir()
dep=base/'isolated_python_deps';install_start=time.time()
args=[v['python'],'-m','pip','--isolated','install','--disable-pip-version-check','--no-cache-dir','--no-deps','--only-binary=:all:','--index-url','https://pypi.org/simple','--target',str(dep),'mujoco==3.14.0','onnxruntime==1.30.0']
with (base/'ISOLATED_PACKAGE_INSTALL.log').open('xb') as f:
 installed=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,timeout=240)
(base/'ISOLATED_PACKAGE_INSTALL_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),returncode=installed.returncode,target=str(dep),global_environment_not_modified=True,no_cache=True,elapsed=time.time()-install_start),indent=2))
assert installed.returncode==0,'Isolated package install failed; retain error and no rerun'

env=dict"""
assert deploy.count(needle)==1;deploy=deploy.replace(needle,install)
deploy=deploy.replace("PYTHONUNBUFFERED='1',OMP_NUM_THREADS='1'","PYTHONUNBUFFERED='1',OMP_NUM_THREADS='1',PYTHONPATH=str(dep),ORT_DISABLE_TELEMETRY='1'")
write(D/'deploy_small_curb_contact_4090_unused_once.py',deploy)
wrapper=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v16.py';s=wrapper.read_text('utf8');needle="        'deploy_confirmed_series_baseline_4090_unused_once.py',";assert s.count(needle)==1;write(wrapper.with_name('same_authorized_session_compressed_transport_v17.py'),s.replace(needle,needle+"\n        'deploy_small_curb_contact_4090_unused_once.py',"))
print(json.dumps(dict(prepared=True,new_stage=str(D),no_local_actor_or_physics_run=True)))
