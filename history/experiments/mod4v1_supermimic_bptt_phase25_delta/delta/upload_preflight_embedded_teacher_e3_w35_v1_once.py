"""New original-teacher reference SOURCE upload/preflight, never native dispatch.
Full sixteen maps, actual closed A1 producer, cached pi.teacher reference.
"""
from pathlib import Path
import json,sys,time,hashlib,shlex
R=Path(__file__).resolve().parent;P=R/'payload_embedded_teacher_native_v1';marker=R/'EMBEDDED_TEACHER_E3_W35_V1_SOURCE_INPUT_ONCE.json';out=R/'reports/EMBEDDED_TEACHER_E3_W35_V1_SOURCE_PREFLIGHT_V1.json';assert not marker.exists()and not out.exists();closed=json.loads((R/'reports/A1_ADMISSION2_QUALITY_BOUNDARY_CLOSED_TRUTH_V1.json').read_bytes());assert closed['all8_original_actual_wait_fullsave_semantic_success'];native=closed['root'];old='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700';stager=R/'source_frozen_embedded_teacher_native_v1/stage_embedded_teacher_native_v1.py';b=stager.read_bytes();assert len(b)==34156 and hashlib.sha256(b).hexdigest()=='e9051dfeb2fd3f08437c4985d2e2f4a6d3229ed75eff870fc3216a7a810e4783';idx=(P/'EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json').read_bytes();assert len(idx)==5685 and hashlib.sha256(idx).hexdigest()=='cfedd40d5c70d61a5a32e10861c3af3b6da16cab86c23306053eeccb650c5205';manifest=json.loads((R/'reports/EMBEDDED_TEACHER_NATIVE16_LOCAL_SOURCE_PAYLOAD_V1.json').read_bytes());assert len(manifest['files'])==16
run='MOD4V1_EMBEDDED_TEACHER_E3_W35_REF_V1_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root='/home/lc01/Zonglin Li/zonglin2/tasks/'+run;input_root=root+'_SOURCE_INPUT';gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842';value=dict(kind='NEW_EMBEDDED_ORIGINAL_TEACHER_REFERENCE_SOURCE_PREFLIGHT_NOT_ADMISSION',root=root,group_id=run,input_root=input_root,native_source_root=native,original_group_root=old,GPU_UUID=gpu,epoch=time.time(),not_yet_staged_or_dispatched=True);marker.write_text(json.dumps(value,indent=2),encoding='utf-8')
sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
def absent(p):
 try:s.lstat(p)
 except FileNotFoundError:return
 raise AssertionError('Fresh source/native path already exists: '+p)
def upload(p,raw):
 absent(p)
 with s.open(p,'wb')as f:f.write(raw)
try:
 absent(root);absent(input_root);s.mkdir(input_root);s.mkdir(input_root+'/source');pins=[]
 for e in manifest['files']:
  p=P/e['file'];raw=p.read_bytes();assert len(raw)==e['bytes']and hashlib.sha256(raw).hexdigest()==e['SHA'];name=p.name;assert'/'not in name and'\\'not in name;upload(input_root+'/source/'+name,raw);pins.append(dict(file='source/'+name,bytes=len(raw),SHA=e['SHA']))
 upload(input_root+'/EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json',idx);upload(input_root+'/stage_embedded_teacher_native_v1.py',b)
 argv=[input_root+'/stage_embedded_teacher_native_v1.py','--original-group-root',old,'--source-dir',input_root+'/source','--source-index',input_root+'/EMBEDDED_TEACHER_NATIVE_STAGE_INDEX_V1.json','--native-root',native,'--new-root',root,'--group-id',run,'--gpu-uuid',gpu,'--preflight-only'];value.update(argv=argv,uploaded_sources=pins,stager_SHA=hashlib.sha256(b).hexdigest(),source_index_SHA=hashlib.sha256(idx).hexdigest());i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B '+' '.join(map(shlex.quote,argv)),timeout=240);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();value.update(returncode=rc,stdout=text,stderr=err);out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0,err;v=json.loads(text);assert v['passed']is True and v['staged']is False and v['parent_launches']==0 and v['model_stat_hash_open_decode']==0;value['preflight']=v;out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(dict(report=str(out),root=root,passed=True,source_files=v['files'],staged=False,parent_SDK_model_C_locks=0,policy_variant='EMBEDDED_ORIGINAL_TEACHER_REFERENCE'),indent=2))
finally:s.close();c.close()
