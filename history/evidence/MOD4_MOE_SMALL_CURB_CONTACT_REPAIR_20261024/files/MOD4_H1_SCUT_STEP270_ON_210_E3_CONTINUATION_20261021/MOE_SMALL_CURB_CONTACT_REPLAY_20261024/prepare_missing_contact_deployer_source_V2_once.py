from pathlib import Path
import ast,json
OLD=Path('C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\MOE_ROUTING_MATCHED_4090_DIAGNOSTIC_20261024');T=OLD.parent;W=T.parent;D=T/'MOE_SMALL_CURB_CONTACT_REPLAY_20261024';PLAYER=W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023'
def write(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8') as f:f.write(s)
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
needle=" z.extractall(base)\nenv=dict"
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
