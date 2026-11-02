"""Stage one fresh frozen quality batch, preserving original static dependencies.
No parent/SDK/model/C/lock operation; actual admission is a separate next step.
"""
from pathlib import Path
import json,sys,time,hashlib,shlex
R=Path(__file__).resolve().parent;out=R/'reports/FROZEN_E3_W35_BATCH_V1_ACTUAL_SOURCE_STAGE_V1.json';marker=R/'FROZEN_E3_W35_BATCH_V1_NONPT_STAGE_ONCE.json';assert not out.exists()and not marker.exists();p=json.loads((R/'reports/FROZEN_E3_W35_BATCH_V1_SOURCE_PREFLIGHT_V1.json').read_bytes());assert p['returncode']==0 and p['preflight']['passed']and p['preflight']['staged']is False and p['preflight']['parent_launches']==0;argv=list(p['argv']);assert argv[-1]=='--preflight-only';argv[-1]='--stage';v=dict(kind='ACTUAL_NEW_FROZEN_MICROBATCH_SOURCE_STAGE_NOT_ADMISSION',root=p['root'],group_id=p['group_id'],input_root=p['input_root'],argv=argv,epoch=time.time());marker.write_text(json.dumps(v,indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B '+' '.join(map(shlex.quote,argv)),timeout=240);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();v.update(returncode=rc,stdout=text,stderr=err);out.write_text(json.dumps(v,indent=2),encoding='utf-8');assert rc==0,err;stage=json.loads(text);assert stage['staged']is True and stage['parent_launches']==0 and stage['model_stat_hash_open_decode']==0 and stage['C_lock_SDK_GPU_GO_operations']==0
 with s.open(p['root']+'/STAGE_COMPLETE_MICROBATCH_V1.json','rb')as f:raw=f.read()
 assert json.loads(raw)==stage;v.update(stage=stage,stage_complete_bytes=len(raw),stage_complete_SHA=hashlib.sha256(raw).hexdigest());out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(dict(report=str(out),root=v['root'],group_id=v['group_id'],stage_complete_SHA=v['stage_complete_SHA'],source_files=stage['source_files'],SDK_PT_C_parent_operations=0,actual_frozen_evaluation=None),indent=2))
finally:s.close();c.close()
