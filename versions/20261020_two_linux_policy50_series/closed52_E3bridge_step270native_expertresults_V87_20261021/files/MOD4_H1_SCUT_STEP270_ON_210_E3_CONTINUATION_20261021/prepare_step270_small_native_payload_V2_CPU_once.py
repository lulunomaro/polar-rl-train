from pathlib import Path
import ast,hashlib,json,shutil,time,zipfile
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';G=W/'MOD4_CURRENT_EXPERT_GRADUATION_JUMP_FROZEN_20261021'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,v):(R/n).open('x',encoding='utf8').write(json.dumps(v,indent=2))
put('STEP270_SMALL_NATIVE_V2_PREPARER_STARTED.json',dict(epoch=time.time(),not_actual_GPU_admission=True))
C=B/'candidate_uninstalled';p=C/'h1_step270_sdk_runtime_candidate.py';s=p.read_text(encoding='utf8')
s=s.replace("-float('inf')",'-1e6')
s=s.replace("self.goal=Step270Events(self.n,self.device)","self.goal=Step270Events(self.n,self.device);self.goal.was_ready=torch.zeros(self.n,device=self.device,dtype=torch.bool)")
s=s.replace("self.previous_front=torch.full", "self.target_body_peak=torch.full((self.n,),.5,device=self.device);self.previous_front=torch.full")
s=s.replace("self.previous_front[ids]=-1e6", "self.previous_front[ids]=-1e6;self.target_body_peak[ids]=.5")
s=s.replace("peak_body=.27+(root[:,2]-lo[:,:,2].amin(-1)).clamp_min(0)+.02", "measured_peak=.27+(root[:,2]-lo[:,:,2].amin(-1)).clamp_min(0)+.02\n        if (fresh & (measured_peak<=.31)).any():raise RuntimeError('Measured wheel/body offset cannot qualify SCUT release reference')\n        self.target_body_peak=torch.where(fresh,measured_peak,self.target_body_peak);peak_body=self.target_body_peak")
p2=C/'h1_step270_sdk_runtime_candidate_v2.py';ast.parse(s);p2.open('x',encoding='utf8').write(s)
P=B/'H1_step270_native32_V2_payload';assert not P.exists();shutil.copytree(G/'H1_jump80_native180_V2_payload',P)
for f in C.glob('*.py'):shutil.copy2(f,P/f.name)
shutil.copy2(p2,P/'h1_step270_sdk_runtime_candidate.py')
# Patch only this new isolated worker, preserving source actor and all plant SDK code.
s=(G/'frozen_H1_jump80_worker_v2_original_SDK_readback.py').read_text(encoding='utf8')
s=s.replace("assert steps in (180,1500)","assert steps==600")
s=s.replace("'--num_envs','80'","'--num_envs','32'").replace('c.scene.num_envs=80','c.scene.num_envs=32').replace('env.num_envs==80','env.num_envs==32').replace('torch.arange(80,','torch.arange(32,').replace('(80,31,3)','(32,31,3)').replace('(80,31)','(32,31)').replace('list(range(80))','list(range(32))').replace('fresh80_seed','fresh32_seed').replace('(80,35)','(32,35)').replace('num_envs=80','num_envs=32')
needle="factory.__globals__['Mod4EnvCfg']=small_cfg;env=factory()"
assert needle in s
s=s.replace(needle,"import h1_scut_fudan_jump_reward_v1 as scut\n  import h1_step270_sdk_runtime_candidate as terrain\n  original_reward_configure=scut.configure\n  scut.configure=lambda cfg:terrain.configure_rewards(cfg,original_reward_configure)\n  factory.__globals__['Mod4Env']=terrain.H1Step270Env\n  factory.__globals__['Mod4EnvCfg']=small_cfg;env=factory()")
s=s.replace("and not x[:,:3].any()","and torch.equal(x[:,0],env.h1_phase.public_request().float()*.8) and not x[:,1:3].any()")
s=s.replace("probe=isolated_actual_SDK_dt_probe(env);", "probe=isolated_actual_SDK_dt_probe(env);put('ACTUAL_STEP270_TERRAIN_AND_REWARD_TASK.json',dict(**env.step270_geometry_receipt,new_task_terrain_reward_phase_migration=True,original_actor35_critic38_action6=True,no_original_H1_scope_claim=True));")
s=s.replace("normal100_request4_next80=True", "normal100_request4_next80=True,actual_270mm_vertical_platform=True,new_public4_forward_command_m_s=.8")
s=s.replace("no_jump_height_or_graduation_claim_before_CPU=True", "no_jump_height_or_graduation_claim_before_CPU=True,new_task_native_only_not_learning=True")
ast.parse(s);(P/'worker.py').write_text(s,encoding='utf8')
cfg=json.loads((P/'FROZEN_CONFIG.json').read_bytes());cfg.update(kind='H1_step270_native32_V2',GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',steps=600,wall_seconds=1800,python='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',num_envs=32,shared_GPU_explicitly_authorized=False,new_task_terrain_reward_phase_migration=True)
(P/'FROZEN_CONFIG.json').write_text(json.dumps(cfg,indent=2),encoding='utf8')
s=(P/'parent.py').read_text(encoding='utf8')
s=s.replace("/home/lc01/Zonglin Li/zonglin2/state/MOD4_H1_SHARED_FROZEN_EVAL_20261021.lock","/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock")
start=s.index(" with Path('/home/lc01/");end=s.index(" uuid=cfg",start)
s=s[:start]+s[end:]
s=s.replace('>7000','>15669')
s=s.replace("uuid=cfg['GPU_UUID'];line=", "uuid=cfg['GPU_UUID'];compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader,nounits'],text=True);assert uuid not in compute;line=")
ast.parse(s);(P/'parent.py').write_text(s,encoding='utf8')
files=[dict(relative=p.relative_to(P).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in P.rglob('*') if p.is_file() and p.name!='SOURCE_MANIFEST.json' and '__pycache__' not in p.parts]
(P/'SOURCE_MANIFEST.json').write_text(json.dumps(dict(epoch=time.time(),source_SHA=cfg['source_SHA'],files=files,new_task_not_old_H1_native=True),indent=2),encoding='utf8')
z=B/'H1_step270_native32_V2_payload.zip';assert not z.exists()
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=1) as f:
 for p in P.rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:f.write(p,p.relative_to(P).as_posix())
put('STEP270_SMALL_NATIVE_V2_SOURCE_AST_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed_source_AST_only=True,previous_runtime_V1_preserved=True,finite_state_sentinel=True,typed_goal_keys_initialized=True,SCUT_target_uses_fresh_actual_wheel_body_offset=True,source_SHA=cfg['source_SHA'],source_Adam=cfg['source_Adam'],num_envs=32,controls=600,physical_callbacks=2400,platform_top_m=.270,policy_hz=100,newtask_not_actual_native_or_learning=True,payload=str(P),zip=dict(path=str(z),bytes=z.stat().st_size,SHA=H(z)),files=files))
print(json.dumps(dict(prepared=True,zip_bytes=z.stat().st_size,no_GPU_yet=True)))
