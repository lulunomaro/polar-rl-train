"""Dispatch the new staged A1 V5 original owner after source/terminal review.
Does not preclaim original canonical/GPU/finite locks or imply actual admission.
"""
from pathlib import Path
import json,sys,hashlib,shlex,time,uuid
R=Path(__file__).resolve().parent;out=R/'reports/A1_NATIVE_V5_ORIGINAL_OWNER_DISPATCH_V1.json';marker=R/'A1_NATIVE_V5_ORIGINAL_OWNER_DISPATCH_ONCE.json';preout=R/'reports/A1_NATIVE_V5_DISPATCH_READONLY_PREFLIGHT_V1.json';assert not out.exists()and not marker.exists()and not preout.exists()
stage=json.loads((R/'reports/A1_NATIVE_V5_ACTUAL_NONPT_STAGE_V1.json').read_bytes());pre=json.loads((R/'reports/A1_NATIVE_V5_ACTUAL_SOURCE_PREFLIGHT_V1.json').read_bytes());assert stage['returncode']==0 and stage['stage_complete']['staged']and stage['stage_complete']['owner_launches']==0;assert stage['stage_complete']['observed_static_trees']==pre['preflight']['observed_static_trees'];root,run,inputroot,sha=stage['root'],stage['run_id'],stage['input_root'],stage['stage_complete_SHA'];assert root==pre['root']and run==pre['run_id'];owner='supermimic_original_owner_shared_app_close_candidate_v5.py'
request=dict(kind='PARENT_APPROVED_NEW_A1_NATIVE_V5_DISPATCH_ONCE',run_id=run,root=root,stage_complete_SHA=sha,owner_relative=owner,dispatch_token=uuid.uuid4().hex,actual_native_launch_requested=True,original_authority_gates_required=True,no_foreign_owner_signal_or_C_steal=True,A1_fresh_native_start=0,no_A0_update_weight_Adam_splice=True)
parentpath=inputroot+'/PARENT_A1_V5_DISPATCH_MARKER.json';args=[inputroot+'/dispatch_a1_native_v5_once.py','--stage-root',root,'--run-id',run,'--stage-complete-sha',sha,'--parent-marker',parentpath,'--python-runner','/home/lc01/Zonglin Li/zonglin2/run-python.sh'];sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
def runcli(values):
 cmd=shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+' '.join(shlex.quote(x)for x in values);i,o,e=c.exec_command(cmd,timeout=600);i.close();txt=o.read().decode(errors='replace');err=e.read().decode(errors='replace');rc=o.channel.recv_exit_status();return dict(returncode=rc,stdout=txt,stderr=err,receipt=json.loads(txt)if rc==0 else None)
try:
 try:s.stat(parentpath)
 except OSError as error:assert error.errno==2,error
 else:raise AssertionError('Parent purpose marker already exists; do not replay')
 with s.open(parentpath,'wb')as f:f.write(json.dumps(request,indent=2).encode())
 checked=runcli(args);preout.write_text(json.dumps(checked,indent=2),encoding='utf-8');assert checked['returncode']==0 and checked['receipt']['passed'],checked
 pending=dict(kind='NEW_A1_V5_ORIGINAL_OWNER_DISPATCH_REQUESTED_ONCE',root=root,run_id=run,input_root=inputroot,stage_complete_SHA=sha,source_contract='A1_RAW35_FRESH_or_original_full_resume_only;no_oldA0_splice',epoch=time.time(),not_yet_GO_or_model_BPTT_or_skill_proof=True);marker.write_text(json.dumps(pending,indent=2),encoding='utf-8')
 result=runcli(args+['--dispatch']);value=dict(**pending,**result);out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert result['returncode']==0,result
 final=dict(**pending,parent=result['receipt']['parent'],owner_relative=owner,actual_Popen_calls=result['receipt']['actual_Popen_calls'],dispatched_not_yet_actualGO=True);marker.write_text(json.dumps(final,indent=2),encoding='utf-8');print(json.dumps(value,indent=2))
finally:s.close();c.close()
