from pathlib import Path
import ast,hashlib,json,time,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports';S=W/'MOD4_LOCAL_WASD_SERIES_20261011';P=W/'MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def write(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8') as f:f.write(s)
old=(D/'moe_matched_player_cuda_worker_v1.py').read_text('utf8')
worker=old.replace("stub.OnnxPolicy=FrozenCudaPolicy","stub.TorchPolicy=FrozenCudaPolicy")
a="from rm7v7_moe_sim import RM7V7MoESim\n sim=RM7V7MoESim();actual_policy=sim.policy.base;assert isinstance(actual_policy,FrozenCudaPolicy)"
b="from series_sim import SeriesSim,MODELS,SERIES\n for row in MODELS:row['local_path']=str(B/'checkpoints'/('E0.pt' if row['id']=='e0' else 'W35.pt'))\n for row in SERIES['scenes']:row['xml']=str(P/'flat.xml')\n sim=SeriesSim('flat','e0');actual_policy=sim.policy;assert isinstance(actual_policy,FrozenCudaPolicy)"
assert worker.count(a)==1;worker=worker.replace(a,b)
worker=worker.replace("original_player_manifest=sim.delivery","confirmed_series_baseline=cfg['human_baseline']")
worker=worker.replace("for target in (.3,.6,1.2,-.6):","for target in (.6,1.5):")
worker=worker.replace("sim.reset_route('flat_run');actual_policy.variant=variant;sim.select_skill(0);","sim.reset_entry(False);actual_policy.variant=variant;")
worker=worker.replace('mujoco.mjtObj.mjOBJ_BODY,sim.chassis_id','mujoco.mjtObj.mjOBJ_XBODY,sim.chassis_id')
worker=worker.replace('all12_initial_physical_states_literal_SHA_equal','all6_initial_physical_states_literal_SHA_equal')
worker=worker.replace('raw=options[:,choice].clamp(-6,6)','raw=options[:,choice]')
worker=worker.replace('expert_actions=options[0].clamp(-6,6).cpu().numpy()','expert_actions=options[0].cpu().numpy()')
worker=worker.replace("B/'CONFIG.json'","B/'SERIES_BASELINE_CONFIG.json'")
write(D/'series_baseline_matched_cuda_worker_v1.py',worker)
deploy=(D/'deploy_moe_router_matched_4090_unused_once.py').read_text('utf8')
deploy=deploy.replace('moe_matched_player_cuda_worker_v1.py','series_baseline_matched_cuda_worker_v1.py')
deploy=deploy.replace('MoE_matched_player_4090_2410v1','MoE_confirmed_series_baseline_4090_2410v1')
deploy=deploy.replace('4090_MATCHED_','4090_SERIES_BASELINE_').replace('MOE_MATCHED_4090_PAYLOAD.zip','SERIES_BASELINE_4090_PAYLOAD.zip')
deploy=deploy.replace('4090_SERIES_BASELINE_FROZEN_FINITE_RETURNED_ACTUAL.json','4090_SERIES_BASELINE_FROZEN_FINITE_RETURNED_ACTUAL.json')
deploy=deploy.replace("speeds_m_s=[.3,.6,1.2,-.6]","speeds_m_s=[.6,1.5]")
deploy=deploy.replace("checkpoints={role:dict(relative='checkpoints/'+role+'.pt',**manifest['sources'][role]) for role in ('E0','W35','gate148')}","checkpoints={role:dict(relative='/home/lc01/Zonglin Li/zonglin2/tasks/MoE_matched_player_4090_2410v1/checkpoints/'+role+'.pt',**manifest['sources'][role]) for role in ('E0','W35','gate148')},human_baseline=dict(environment='本机 MuJoCo 播放器',entry='平地／起伏／小陀螺系列播放器（可切 E0、W35）',source=str(W/'MOD4_LOCAL_WASD_SERIES_20261011'),exact_E0_checkpoint=True,old_terrain_registry_not_current_W35=True)")
start=deploy.index("  z.write(worker,'worker.py');")
end=deploy.index(" put('4090_SERIES_BASELINE_DEPLOY_STARTED_ACTUAL.json'",start)
payload="""  z.write(worker,'worker.py');z.write(D/'CONFIG.json','CONFIG.json')
  source=W/'MOD4_LOCAL_WASD_SERIES_20261011'
  for name in ('sim_runtime.py','series_sim.py','runtime_config.json','SERIES.json','DOWNLOAD_RECEIPT.json','terrain.npz'):
   z.write(source/name,'player/'+name)
  for name in ('reset_bank.json','import_contract.json'):
   z.write(source/'src_snapshot'/name,'player/src_snapshot/'+name)
  import xml.etree.ElementTree as ET
  root=ET.fromstring((source/'scenes/flat.xml').read_bytes());root.find('compiler').set('meshdir','assets')
  z.writestr('player/flat.xml',ET.tostring(root,encoding='utf-8',xml_declaration=True))
  for mesh in root.findall('asset/mesh'):
   name=mesh.get('file');z.write(W/'chassis_mod4/assets'/name,'player/assets/'+name)
"""
deploy=deploy[:start]+payload+deploy[end:]
deploy=deploy.replace("local=D/'actual_4090'","local=D/'actual_series_4090'")
deploy=deploy.replace("D/'CONFIG.json'","D/'SERIES_BASELINE_CONFIG.json'").replace("'CONFIG.json')","'SERIES_BASELINE_CONFIG.json')")
# The prior package probe is consumed evidence; this deployer itself performs fresh admission.
deploy=deploy.replace("4090_RESOURCE_AND_EXISTING_PACKAGE_PROBE_ACTUAL.json","4090_RESOURCE_AND_EXISTING_PACKAGE_PROBE_ACTUAL.json")
write(D/'deploy_confirmed_series_baseline_4090_unused_once.py',deploy)
wrapper=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v15.py'
ws=wrapper.read_text('utf8');needle="        'read_missing_saved_pose_velocity_frame_V2_unused_once.py',"
assert ws.count(needle)==1;write(wrapper.with_name('same_authorized_session_compressed_transport_v16.py'),ws.replace(needle,needle+"\n        'deploy_confirmed_series_baseline_4090_unused_once.py',"))
x=ET.fromstring((S/'scenes/flat.xml').read_bytes());y=ET.fromstring((P/'rm7v7_latest_moe.xml').read_bytes())
def norm(n):return None if n is None else (n.tag,dict(sorted(n.attrib.items())),[norm(c) for c in n])
parts={k:norm(x.find(k))==norm(y.find(k)) for k in ('option','default','equality','actuator','sensor')}
bx=x.find("worldbody/body[@name='chassis']");by=y.find("worldbody/body[@name='chassis']")
cfg0=json.loads((S/'runtime_config.json').read_bytes());cfg1=json.loads((P/'runtime_config.json').read_bytes());assert cfg0==cfg1
put('HUMAN_CONFIRMED_SERIES_BASELINE_SOURCE_AND_NEW_REMOTE_PROTOCOL_ACTUAL.json',dict(epoch=time.time(),human_answers=['本机 MuJoCo 播放器','平地／起伏／小陀螺系列播放器（可切 E0、W35）'],known_E0_SHA='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8',same_E0_as_bundle=True,runtime_configuration_equal=True,XML_parts_equal=parts,chassis_tree_equal=norm(bx)==norm(by),old_registry=json.loads((S/'DOWNLOAD_RECEIPT.json').read_bytes()),new_test=['auto','E0','W35'],speeds=[.6,1.5],controls_each=500,physics='Original old series flat XML, compiler meshdir relocated only; MuJoCo remote host CPU, CUDA actors on4090',differences_remaining=['Remote MuJoCo3.12 versus local3.14','Remote CUDA actor versus original CPU Torch','Old registry terrain3c97 differs from bundleW35b026; exact former user selected model not known'],no_local_policy_inference_or_MuJoCo_execution=True,files={str(p):dict(bytes=p.stat().st_size,SHA=H(p)) for p in (D/'series_baseline_matched_cuda_worker_v1.py',D/'deploy_confirmed_series_baseline_4090_unused_once.py',wrapper.with_name('same_authorized_session_compressed_transport_v16.py'))}))
put('LOCAL_BASELINE_READONLY_PATH_AND_SEARCH_OUTPUT_ERRORS_ACTUAL.json',dict(epoch=time.time(),scope='Read-only local source inspection only',errors=[dict(operation='Broad rg --files globs',actual_exit_code=1,original_output_tokens=173561,returned_output_truncated=True,full_output_not_captured=True),dict(operation='Get-Content OLD_D/NEXT49...json',reason='report is under reports subdirectory',helper_started=False),dict(operation='Optional PREPARE_BRANCH_CONFIG.json read',reason='not present; ignored optional read',helper_started=False)],no_remote_query_or_mutation_or_training_failure=True))
print(json.dumps(dict(prepared=True,XML_parts_equal=parts,chassis_tree_equal=norm(bx)==norm(by),no_local_simulation=True)))
