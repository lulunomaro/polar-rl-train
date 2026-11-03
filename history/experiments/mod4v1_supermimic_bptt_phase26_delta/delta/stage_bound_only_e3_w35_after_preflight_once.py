"""Once-only NEW reference static stage after genuine metadata/source preflight.
No native dispatch/SDK/model/raw/C or resource-lock operation.
"""
from pathlib import Path
import json,sys,time,shlex,hashlib
R=Path(__file__).resolve().parent;guard=R/'BOUND_ONLY_E3_W35_V1_STAGE_STARTED_ONCE.json';out=R/'reports/BOUND_ONLY_E3_W35_V1_ACTUAL_SOURCE_STAGE_V1.json';assert not guard.exists()and not out.exists();p=json.loads((R/'reports/BOUND_ONLY_E3_W35_V1_SOURCE_PREFLIGHT_V1.json').read_bytes());assert p['returncode']==0 and p['preflight']['passed']and p['preflight']['staged']is False and p['preflight']['parent_launches']==0;argv=p['argv'];assert argv[-1]=='--preflight-only';argv=argv[:-1]+['--stage'];guard.write_text(json.dumps(dict(root=p['root'],group_id=p['group_id'],epoch=time.time(),once_source_stage_not_native=True),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B '+' '.join(map(shlex.quote,argv)),timeout=300);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();v=dict(kind='ACTUAL_EMBEDDED_TEACHER_BOUND_PROBE_SOURCE_STAGE_NOT_ADMISSION',root=p['root'],group_id=p['group_id'],input_root=p['input_root'],argv=argv,stager_SHA=p['stager_SHA'],source_index_SHA=p['source_index_SHA'],returncode=rc,stdout=text,stderr=err);out.write_text(json.dumps(v,indent=2),encoding='utf-8');assert rc==0,err
 with s.open(p['root']+'/STAGE_COMPLETE_BOUND_ONLY_NATIVE_V1.json','rb')as f:raw=f.read()
 a=json.loads(raw);assert a==json.loads(text)and a['staged']and a['parent_launches']==0 and a['model_stat_hash_open_decode']==0;v.update(stage=a,stage_complete_bytes=len(raw),stage_complete_SHA=hashlib.sha256(raw).hexdigest());out.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(dict(report=str(out),root=p['root'],source_files=a['source_files'],stage_complete_SHA=v['stage_complete_SHA'],parent_SDK_models_C=0),indent=2))
finally:s.close();c.close()
