"""One NEW non-PT stage after the independent read-only source preflight.
No owner launch, SDK, model or canonical access. Preserve failure, never replay.
"""
from pathlib import Path
import json,sys,hashlib,shlex,time
R=Path(__file__).resolve().parent;out=R/'reports/A1_NATIVE_V5_ACTUAL_NONPT_STAGE_V1.json';marker=R/'A1_NATIVE_V5_NONPT_STAGE_ONCE.json';assert not out.exists()and not marker.exists();previous=json.loads((R/'reports/A1_NATIVE_V5_ACTUAL_SOURCE_PREFLIGHT_V1.json').read_bytes());assert previous['returncode']==0 and previous['preflight']['passed']and previous['preflight']['stage_writes']==0 and previous['preflight']['owner_launches']==0
value=dict(kind='NEW_A1_V5_ACTUAL_NONPT_STAGE_PURPOSE',root=previous['root'],run_id=previous['run_id'],input_root=previous['input_root'],prior_read_only_preflight=str(R/'reports/A1_NATIVE_V5_ACTUAL_SOURCE_PREFLIGHT_V1.json'),selected_PT_SDK_C_GO_owner_launch_operations=0,epoch=time.time());marker.write_text(json.dumps(value,indent=2),encoding='utf-8');args=previous['preflight_argv']+['--stage'];sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 cmd="CUDA_VISIBLE_DEVICES='' "+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+' '.join(shlex.quote(x)for x in args)
 i,o,e=c.exec_command(cmd,timeout=600);i.close();txt=o.read().decode(errors='replace');err=e.read().decode(errors='replace');rc=o.channel.recv_exit_status();value.update(returncode=rc,stdout=txt,stderr=err)
 if rc==0:
  with s.open(previous['root']+'/STAGE_COMPLETE_V5.json','rb')as f:raw=f.read()
  value.update(stage_complete=json.loads(raw),stage_complete_SHA=hashlib.sha256(raw).hexdigest());assert value['stage_complete']['staged']and value['stage_complete']['owner_launches']==0
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2));assert rc==0,(rc,err)
finally:s.close();c.close()
