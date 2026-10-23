from pathlib import Path
import ast,hashlib,json,time
D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports'
def write(p,s):
 ast.parse(s)
 with p.open('x',encoding='utf8') as f:f.write(s)
receipt=json.loads((R/'4090_SMALL_CURB_FROZEN_FINITE_RETURNED_ACTUAL.json').read_bytes());assert receipt['actual_returncode']==1 and receipt['actual_child_waited'] and receipt['own_eval_lock_released'] and receipt['final'] is None
dep='/home/lc01/Zonglin Li/zonglin2/tasks/MoE_small_curb_contact_4090_2410v1/isolated_python_deps'
worker=(D/'small_curb_actual_contact_worker_v1.py').read_text('utf8');worker=worker.replace("def main():\n import numpy", "def main():\n sys.path.insert(0,"+repr(dep)+")\n import numpy");worker=worker.replace("B/'CONFIG.json'","B/'CONFIG_V2.json'")
worker=worker.replace("ort.disable_telemetry_events()","ort.disable_telemetry_events()\n assert str(Path(mujoco.__file__).resolve()).startswith("+repr(dep)+") and str(Path(ort.__file__).resolve()).startswith("+repr(dep)+")")
write(D/'small_curb_actual_contact_worker_v2.py',worker)
s=(D/'deploy_small_curb_contact_4090_unused_once.py').read_text('utf8');s=s.replace('small_curb_actual_contact_worker_v1.py','small_curb_actual_contact_worker_v2.py').replace('4090_SMALL_CURB_','4090_SMALL_CURB_V2_').replace('SMALL_CURB_4090_PAYLOAD.zip','SMALL_CURB_V2_4090_PAYLOAD.zip').replace('MoE_small_curb_contact_4090_2410v1','MoE_small_curb_contact_4090_2410v2').replace("local=D/'actual_contact_4090'","local=D/'actual_contact_V2_4090'").replace("D/'CONFIG.json'","D/'CONFIG_V2.json'").replace("'CONFIG.json')","'CONFIG_V2.json')")
start=s.index("dep=base/'isolated_python_deps'");end=s.index('\nenv=dict',start)
s=s[:start]+"dep=Path("+repr(dep)+");assert dep.is_dir()\n"+s[end:]
oldroot='/home/lc01/Zonglin Li/zonglin2/tasks/MoE_small_curb_contact_4090_2410v1'
needle="base=Path(v['root']);assert base.resolve()"
check="old=Path("+repr(oldroot)+");prior=json.loads((old/'OWN_RETURNED_ACTUAL.json').read_bytes());assert prior['actual_child_waited'] and prior['actual_returncode']==1 and prior['own_eval_lock_released'];identity=prior['identity'];assert not psutil.pid_exists(identity['pid']) or psutil.Process(identity['pid']).create_time()!=identity['creation'];\nbase=Path(v['root']);assert base.resolve()"
assert s.count(needle)==1;s=s.replace(needle,check)
write(D/'deploy_small_curb_contact_V2_4090_unused_once.py',s)
wrapper=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v17.py';s=wrapper.read_text('utf8');needle="        'deploy_small_curb_contact_4090_unused_once.py',";assert s.count(needle)==1;write(wrapper.with_name('same_authorized_session_compressed_transport_v18.py'),s.replace(needle,needle+"\n        'deploy_small_curb_contact_V2_4090_unused_once.py',"))
with (R/'V1_IMPORT_ERROR_AND_NEW_V2_EXPLICIT_DEPENDENCY_PATH_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),V1_actual_returncode=1,V1_no_FINAL=True,V1_before_model_or_GPU_policy_or_rollout=True,original_error="ModuleNotFoundError: No module named 'onnxruntime'",isolated_pip_install_returncode=0,old_root=str(oldroot),old_worker_waited_out=True,precise_import_path_failure_cause_not_isolated=True,repair='New root V2 and explicit sys.path inserted before import; package versions and file locations asserted; reuse already-installed isolated deps without reinstall.',new_worker_SHA=hashlib.sha256((D/'small_curb_actual_contact_worker_v2.py').read_bytes()).hexdigest(),new_deployer_SHA=hashlib.sha256((D/'deploy_small_curb_contact_V2_4090_unused_once.py').read_bytes()).hexdigest(),no_old_once_or_root_rerun=True,no_training_or_budget_write=True),f,indent=2)
print('New V2 source AST passed; V1 error and root retained')
