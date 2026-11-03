"""One readonly original-gate observation; this neither admits nor launches."""
from pathlib import Path
import ast,json,hashlib,sys,time,shlex
R=Path(__file__).resolve().parent;out=R/'reports/GOOD_HOLDOUT_D6_SEED20260929_RESOURCE_PRELAUNCH_SNAPSHOT_V1.json';assert not out.exists();stage=json.loads((R/'reports/GOOD_HOLDOUT_D6_SEED20260929_ACTUAL_STAGE_V1.json').read_bytes());assert stage['returncode']==0 and stage['receipt']['materialized']and stage['receipt']['parent_launches']==0 and stage['receipt']['metadata_validation']['passed']and stage['stage_receipt_SHA256']=='9265df408211b018543b27265ace04ff1a74d6af5e29c9ab44a4146f73acbb82'
source=R/'observe_bound_probe_resources_after_zero_admission_timeout_once.py';raw=source.read_bytes();tree=ast.parse(raw);node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='code'for x in n.targets));code=ast.literal_eval(node.value);assert type(code)is str and 'lock_acquisitions_Cwrites_models_raw_SDK_GPU_parent_or_signals=0'in code;ast.parse(code)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();stdout=o.read().decode('utf8','replace');stderr=e.read().decode('utf8','replace');rc=o.channel.recv_exit_status();v=dict(kind='GOOD_HOLDOUT_D6_SEED29_ORIGINAL_RESOURCE_READONLY_SNAPSHOT_NOT_ADMISSION',epoch=time.time(),root=stage['root'],stage_receipt_SHA256=stage['stage_receipt_SHA256'],read_only_code_source=source.name,read_only_code_source_SHA256=hashlib.sha256(raw).hexdigest(),entire_existing_code_literal_reused=True,old_observer_main_or_wait_not_replayed=True,returncode=rc,stderr=stderr,source_snapshot_not_lease=True,actual_parent_Cwrite_lock_model_raw_SDK_or_signal_operations=0)
 if rc==0:v['actual']=json.loads(stdout)
 with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
 print(json.dumps(v,indent=2));assert rc==0,stderr
finally:c.close()
