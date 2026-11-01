"""New0PT64 producer->worker JSON/AST ABI;no prior off/SDK fixture replay."""
from pathlib import Path
import ast,hashlib,json,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 assert json.loads((R/'CPU_DR064_PURPOSE_FROZEN.json').read_bytes())['executions']==1
 put(R/'CPU_DR064_ONCE_CONSUMED.json',dict(epoch=time.time(),old_fixtures=0))
 names=['dr0_contract.py','dr0_actual_readback.py','authority235_dr064.py','audit235_dr064.py','launcher213.py','probe_dr0_64_worker_ROOT_ONLY.py','derive_probe64_sources.py','run_ROOT_dr064_once.py','check_new_dr064_source_interface_once.py']
 source={x:(N/x).read_text(encoding='utf8') for x in names}
 for s in source.values():ast.parse(s)
 caller=ast.parse(source['run_ROOT_dr064_once.py'])
 embedded={x.targets[0].id:ast.literal_eval(x.value) for x in caller.body if isinstance(x,ast.Assign) and isinstance(x.value,ast.Constant) and isinstance(x.value.value,str) and x.targets[0].id in ('AUTH','SETUP','CASE')}
 assert set(embedded)=={'AUTH','SETUP','CASE'}
 for s in embedded.values():ast.parse(s)
 case=ast.parse(embedded['CASE']);worker=ast.parse(source['probe_dr0_64_worker_ROOT_ONLY.py'])
 task=next(x.value for x in ast.walk(case) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='task' for t in x.targets))
 keys={x.arg for x in task.keywords};consumed={x.slice.value for x in ast.walk(worker) if isinstance(x,ast.Subscript) and isinstance(x.value,ast.Name) and x.value.id=='task' and isinstance(x.slice,ast.Constant)}
 assert consumed<=keys,(consumed-keys)
 kind=next(ast.literal_eval(x.value) for x in task.keywords if x.arg=='kind');assert kind=='DR0_OFF64_ZERO_PT_ORIGINAL_PHYSICAL_ADMISSION_V1' and kind in source['probe_dr0_64_worker_ROOT_ONLY.py']
 synthetic=dict(kind=kind,num_envs=64,controls=8,NN_model_reads=0,PPO_updates=0,actual_parent_private_validation_EX_held=True)
 assert json.loads(json.dumps(synthetic))==synthetic
 assert "'off'" in source['dr0_contract.py'] and "profile='off'" not in embedded['CASE']
 assert 'child.wait(timeout=360)' in embedded['CASE'] and 'rc=child.wait()' in embedded['CASE']
 assert 'active_GPU_UUID' in embedded['AUTH'] and 'active_GPU_UUID' in embedded['CASE'] and 'audit_current' in embedded['CASE']
 assert "Path(x).suffix in ('.pt','.pth','.onnx','.jsonl')" in embedded['SETUP']
 assert 'IsolatedAppLauncher213' in source['probe_dr0_64_worker_ROOT_ONLY.py'] and 'real=ChassisPDMod4Env(cfg=cfg)' in source['probe_dr0_64_worker_ROOT_ONLY.py']
 assert 'range(8)' in source['probe_dr0_64_worker_ROOT_ONLY.py'] and 'tick==64' not in source['probe_dr0_64_worker_ROOT_ONLY.py']
 assert 'app.close()' in source['probe_dr0_64_worker_ROOT_ONLY.py'] and source['probe_dr0_64_worker_ROOT_ONLY.py'].index("put(N/'DR064_APPCLOSING_BEFORE_CLOSE.json'")<source['probe_dr0_64_worker_ROOT_ONLY.py'].index('app.close()')
 prohibited=[]
 for name,s in dict(source,**embedded).items():
  for x in ast.walk(ast.parse(s)):
   if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ('kill','terminate','send_signal'):prohibited.append(name)
 assert not prohibited
 assert not any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ('load','load_state_dict') for x in ast.walk(worker))
 assert 'OnPolicyRunner' not in source['probe_dr0_64_worker_ROOT_ONLY.py']
 core=N.parent/'E0_ALL_RANDOMIZATION_OFF_DR0_SOURCE_CONTRACT_V1_20261101'
 assert all((N/x).read_bytes()==(core/x).read_bytes() for x in ('dr0_contract.py','dr0_actual_readback.py'))
 put(R/'CPU_DR064_NEW_SOURCE_INTERFACE_ACTUAL.json',dict(epoch=time.time(),passed=True,source_AST=9,embedded_AST=3,new_producer_worker_Task_keys_match=True,
  new_JSON_synthetic_roundtrip=1,off_core_bytes_unchanged=True,child_wait_no_signal=True,model_NN_loader_calls=0,
  actual_SDK_readback=False,actual_Target_admission='UNSELECTED_PENDING_ROOT_3060_EVIDENCE_AND_FRESH_AUTHORITY',Torch_model_asset_raw_network_Git=0,old_fixtures=0))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'CPU_DR064_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
