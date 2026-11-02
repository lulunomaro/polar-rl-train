# NEW V2 dependency-complete evaluation purpose; do not replay consumed failedV1.
"""Dispatch exactly one fresh original-gated E3/W35 frozen-quality parent.
Original privateEX/finiteEX/canonical-readiness gates remain in pinned parent.
This dispatcher does not read/write C, acquire locks, open models or import SDK.
"""
from pathlib import Path
import json,sys,shlex,time
R=Path(__file__).resolve().parent;marker=R/'FROZEN_E3_W35_BATCH_V2_PARENT_DISPATCH_ONCE.json';out=R/'reports/FROZEN_E3_W35_BATCH_V2_ACTUAL_PARENT_DISPATCH_V1.json';assert not marker.exists()and not out.exists();stage=json.loads((R/'reports/FROZEN_E3_W35_BATCH_V2_ACTUAL_SOURCE_STAGE_RECEIPT_CORRECTED_V2.json').read_bytes());assert stage['returncode']==0 and stage['stage']['staged']and stage['stage']['parent_launches']==0;root=stage['root'];gid=stage['group_id'];expected=stage['stage_complete_SHA'];assert root.endswith('/'+gid)and gid.startswith('MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_')
code='''from pathlib import Path
import json,time,os,subprocess,hashlib
root=Path(ROOT);expected=EXPECTED;assert root.name==__GROUP_ID__ and root.parent==Path('/home/lc01/Zonglin Li/zonglin2/tasks');raw=(root/'STAGE_COMPLETE_MICROBATCH_V2.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==expected;stage=json.loads(raw);assert stage['staged']and stage['parent_launches']==0
for name in('PARENT_STARTED.json','PARENT_EXIT_SCOPE.json','PARENT_ORIGINAL_ERROR.json','FINAL.json','PARENT_FROZEN_MICROBATCH_DISPATCH_ONCE.json'):assert not(root/name).exists(),name
plan=json.loads((root/'GROUP_PLAN.json').read_bytes());assert plan['group_id']==root.name and plan['requested_roles']==['E3','W35']and plan['kind']=='A1_FROZEN_EVAL_MICROBATCH_GROUP_PLAN_V1'and plan['comparison']is None and plan['overall_eight_pass_rate']is None
parent=root/'single_gpu_e3_w35_a1_frozen_parent_v1.py';rawparent=parent.read_bytes();assert len(rawparent)==8991 and hashlib.sha256(rawparent).hexdigest()=='9a943e730f66bfb1a68af35ddfa8118d6da605dc83f442e3c0b51c9c7ad8da7b'
# Standard original resources belong to supervisor, never this dispatcher.
request=dict(kind='NEW_FROZEN_MICROBATCH_DISPATCH_NOT_RESOURCE_OR_SKILL_ADMISSION',epoch=time.time(),group_id=root.name,requested_roles=['E3','W35'],stage_complete_SHA=expected,source_parent_SHA=hashlib.sha256(rawparent).hexdigest(),original_single_GPU_private_EX_global_finite_EX_C_readonly_gates_unchanged=True,controller_C_locks_model_SDK_operations=0)
p=root/'PARENT_FROZEN_MICROBATCH_DISPATCH_ONCE.json'
with p.open('x')as f:json.dump(request,f,indent=2);f.flush();os.fsync(f.fileno())
log=(root/'PARENT_FROZEN_MICROBATCH_STDOUT_STDERR.log').open('xb');child=subprocess.Popen(['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-u','-B',str(parent)],cwd=str(root),stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();stat=Path('/proc')/str(child.pid)/'stat';text=stat.read_text();f=text[text.rfind(')')+2:].split();request.update(actual_Popen_calls=1,parent=dict(pid=child.pid,linux_start_ticks=f[19],state=f[0],observed_epoch=time.time()),not_yet_scene_ready_or_actual_frozen_result=True);(root/'PARENT_FROZEN_MICROBATCH_DISPATCH_RECEIPT.json').write_text(json.dumps(request,indent=2));print(json.dumps(request))
'''.replace('ROOT',repr(root)).replace('EXPECTED',repr(expected)).replace('__GROUP_ID__',repr(gid))
import ast
ast.parse(code)
marker.write_text(json.dumps(dict(root=root,group_id=gid,epoch=time.time(),purpose='Once original frozen supervisor, not resource gate bypass'),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B -c '+shlex.quote(code),timeout=45);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();value=dict(root=root,group_id=gid,epoch=time.time(),returncode=rc,stdout=text,stderr=err);out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0,err;value['receipt']=json.loads(text);out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2))
finally:c.close()
