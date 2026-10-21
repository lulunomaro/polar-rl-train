from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,json,time,numpy as np,torch
T=Path(__file__).resolve().parent;R=T/'reports';D=T/'actual_SDK_termination_source_20261022';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
receipt=json.loads((R/'H1_ARENA_REPAIR_ACTUAL_SDK_TERMINATION_SOURCE_CPU_RECEIPT.json').read_bytes())
for row in receipt['actual_installed_source']:assert H(D/row['name'])==row['SHA']
tree=ast.parse((D/'termination_manager.py').read_text('utf8'));cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='TerminationManager');fn=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='compute')
ns=dict(torch=torch);exec(compile(ast.Module(body=[fn],type_ignores=[]),'actual_installed_SDK_TerminationManager_compute','exec'),ns)
runtime=T/'production_candidate_V2_ARENA_EXIT_UNINSTALLED/h1_step270_sdk_runtime_candidate.py';r=ast.parse(runtime.read_text('utf8'));guard=next(x for x in r.body if isinstance(x,ast.FunctionDef) and x.name=='out_of_authored_floor')
ns['tensor']=lambda x:x;exec(compile(ast.Module(body=[guard],type_ignores=[]),'actual_candidate_guard','exec'),ns)
v=json.loads((T/'cooked_query_full20k_V9_actual/out/ACTUAL_COOKED_VS_AUTHORED_STEP270_QUERY_RESULT.json').read_bytes());origins=torch.tensor([[x['actual_Float3_origin'][0]-.25,x['actual_Float3_origin'][1],0.] for x in v['front_rows']])
raw=np.load(T/'relocated_forensic_originals/H1step270_pairV1_closed_control318/control_prefix_13.npz');root=torch.from_numpy(raw['root13'][-1,:,:3])
class Scene(dict):pass
scene=Scene(robot=SimpleNamespace(data=SimpleNamespace(root_pos_w=root)));scene.env_origins=origins;env=SimpleNamespace(scene=scene)
term=SimpleNamespace(func=ns['out_of_authored_floor'],params={},time_out=False)
mgr=SimpleNamespace(_env=env,_term_cfgs=[term],_truncated_buf=torch.zeros(20000,dtype=torch.bool),_terminated_buf=torch.zeros(20000,dtype=torch.bool),_term_dones=torch.zeros((20000,1),dtype=torch.bool),_last_episode_dones=torch.zeros((20000,1),dtype=torch.bool))
actual=ns['compute'](mgr);assert torch.nonzero(actual).flatten().tolist()==[19965] and not mgr._truncated_buf.any() and int(mgr._terminated_buf.sum())==1
scene['robot'].data.root_pos_w=origins.clone();again=ns['compute'](mgr);assert not again.any()
source=(D/'termination_manager.py').read_text('utf8');assert 'cfg_items = self.cfg.__dict__.items()' in source
reg=next(x for x in r.body if isinstance(x,ast.FunctionDef) and x.name=='configure_scene');assign=[x for x in ast.walk(reg) if isinstance(x,ast.Assign) and any(isinstance(y,ast.Attribute) and y.attr=='h1_step270_arena_exit' for y in x.targets)];assert len(assign)==1
call=assign[0].value;assert isinstance(call,ast.Call) and call.func.id=='TerminationTermCfg' and {x.arg:ast.literal_eval(x.value) for x in call.keywords if x.arg=='time_out'}=={'time_out':False}
out=dict(epoch=time.time(),passed_actual_installed_SDK_compute_function_CPU=True,actual_SDK_source_SHA=H(D/'termination_manager.py'),candidate_runtime_SHA=H(runtime),actual_recorded_selected_envs=[19965],other19999_envs_not_terminated=True,ordinary_failure_not_timeout=True,healthy_reset_positions_no_termination=True,SDK_configuration_accepts_cfg_dict_attributes=True,source_registration_uses_real_TerminationTermCfg_time_out_false=True,not_Kit_App_or_PhysX_scene_execution=True,no_new_GPU_native_or_query_or_H1_GO=True,whole_payload_installed_source_SDK_RSL_CPU_and_fresh_resources_still_required=True)
with (R/'H1_ARENA_REPAIR_ACTUAL_SDK_TERMINATION_COMPUTE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))
