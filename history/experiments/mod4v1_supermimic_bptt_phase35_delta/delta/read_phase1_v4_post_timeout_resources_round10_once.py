"""One NEW readonly original-gate resource observation after actual zero-GO close."""
from pathlib import Path
import ast,json,hashlib,sys,time,shlex
R=Path(__file__).resolve().parent;out=R/'reports/PHASE1_V4_POST_TIMEOUT_RESOURCES_ROUND10_SNAPSHOT_V1.json';assert not out.exists();v=json.loads((R/'reports/PHASE1_V4_ZERO_ADMISSION_CLOSED_TRUTH_V1.json').read_bytes());assert v['actual_group_admission']is None and v['actual_children']is None and v['actual_GO']is None and not v['SDK_selected_model_opened'];e=v['parent_exit_scope'];assert e['all_own_children_waited']and e['original_single_GPU_private_EX_released']and e['original_global_finite_EX_released']and e['child_waits']==[]
source=R/'observe_bound_probe_resources_after_zero_admission_timeout_once.py';raw=source.read_bytes();tree=ast.parse(raw);node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='code'for t in n.targets));code=ast.literal_eval(node.value);assert type(code)is str and 'lock_acquisitions_Cwrites_models_raw_SDK_GPU_parent_or_signals=0'in code;ast.parse(code)
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72()
try:
 i,o,err=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();stdout=o.read().decode('utf-8','replace');stderr=err.read().decode('utf-8','replace');rc=o.channel.recv_exit_status();result=dict(kind='NEW_V4_POST_ZERO_GO_READONLY_RESOURCE_SNAPSHOT_ROUND10_NOT_ADMISSION',epoch=time.time(),old_root=v['root'],old_closed_epoch=e['epoch'],old_closed_metadata_SHA=v['closed_result']['SHA256'],read_only_code_source=source.name,read_only_code_source_SHA256=hashlib.sha256(raw).hexdigest(),only_entire_existing_readonly_code_literal_reused_old_observer_main_not_run=True,returncode=rc,stdout=stdout,stderr=stderr,original_wait_not_extended=True)
 if rc==0:result['actual']=json.loads(stdout);assert result['actual']['epoch']>e['epoch']
 with out.open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
 assert rc==0,stderr
 print(json.dumps(dict(report=str(out),actual=result['actual']),indent=2))
finally:c.close()
