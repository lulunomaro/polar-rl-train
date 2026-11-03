"""New zero-update bound-only probe SOURCE upload/preflight, never native dispatch.
Full seventeen maps, actual closed A1 producer, same learned pi with .05*tanh residual; no optimizer updates.
"""
from pathlib import Path
import json,sys,time,hashlib,shlex
R=Path(__file__).resolve().parent;

def prior_zero_admission():
 p=json.loads((R/'BOUND_ONLY_E3_W35_V1_LATEST_CLOSED_RESULT_PATH.json').read_bytes());raw=Path(p['path']).read_bytes();v=json.loads(raw);t=v['top'];end=t['PARENT_EXIT_SCOPE.json'];assert v['closed']and v['actual_external_parent_wait_bound']and not v['early_controller_dead_without_wait_proof'];assert t['ACTUAL_GROUP_ADMISSION.json']is None and t['CHILDREN.json']is None and t['GROUP_EVAL_START.json']is None and t['FINAL.json']is None;assert end['all_own_children_waited']and end['child_waits']==[]and end['original_single_GPU_private_EX_released']and end['original_global_finite_EX_released']and end['canonical_writes']==0;assert 'Originalresourcewait1800sexpired'in str(t['PARENT_ORIGINAL_ERROR.json']);assert all(x['status']=='NOT_ADMITTED'and x['FINAL']is None and x['WORKER_SCENE_READY']is None for x in v['rows']);w=t['BOUND_PROBE_PARENT_WAITED_ACTUAL_V1.json'];assert w['actual_parent_p_wait_returned']and w['returncode']==1 and not w['controller_errors'];return v,end,hashlib.sha256(raw).hexdigest()
prior,prior_end,prior_closed_SHA=prior_zero_admission()

P=R/'payload_bound_only_native_v1';marker=R/'BOUND_ONLY_E3_W35_V1_ADMISSION2_SOURCE_INPUT_ONCE.json';out=R/'reports/BOUND_ONLY_E3_W35_V1_ADMISSION2_SOURCE_PREFLIGHT_V1.json';assert not marker.exists()and not out.exists();closed=json.loads((R/'reports/A1_ADMISSION2_QUALITY_BOUNDARY_CLOSED_TRUTH_V1.json').read_bytes());assert closed['all8_original_actual_wait_fullsave_semantic_success'];native=closed['root'];old='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700';stager=R/'source_bound_only_native_integration_v1/stage_bound_only_native_v1.py';b=stager.read_bytes();assert len(b)==34960 and hashlib.sha256(b).hexdigest()=='74f52b47c54e742f2a60a8459b7fa013dd52793b2adc970d02149474eb21eb40';idx=(P/'BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json').read_bytes();assert len(idx)==6085 and hashlib.sha256(idx).hexdigest()=='d0519c7a351513a61f4c0c5c055b74bc7df41ac0300ce964207dd9508254f19a';manifest=json.loads((R/'reports/BOUND_ONLY_NATIVE17_LOCAL_SOURCE_PAYLOAD_V1.json').read_bytes());assert len(manifest['files'])==17
run='MOD4V1_BOUND_ONLY_E3_W35_PROBE_V1_ADMISSION2_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root='/home/lc01/Zonglin Li/zonglin2/tasks/'+run;input_root=root+'_SOURCE_INPUT';gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842';value=dict(kind='NEW_EMBEDDED_ORIGINAL_TEACHER_BOUND_PROBE_SOURCE_PREFLIGHT_NOT_ADMISSION',root=root,group_id=run,input_root=input_root,native_source_root=native,original_group_root=old,GPU_UUID=gpu,epoch=time.time(),not_yet_staged_or_dispatched=True);marker.write_text(json.dumps(value,indent=2),encoding='utf-8')
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
 upload(input_root+'/BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json',idx);upload(input_root+'/stage_bound_only_native_v1.py',b)
 argv=[input_root+'/stage_bound_only_native_v1.py','--original-group-root',old,'--source-dir',input_root+'/source','--source-index',input_root+'/BOUND_ONLY_NATIVE_STAGE_INDEX_V1.json','--native-root',native,'--new-root',root,'--group-id',run,'--gpu-uuid',gpu,'--preflight-only'];value.update(argv=argv,uploaded_sources=pins,stager_SHA=hashlib.sha256(b).hexdigest(),source_index_SHA=hashlib.sha256(idx).hexdigest());i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B '+' '.join(map(shlex.quote,argv)),timeout=240);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();value.update(returncode=rc,stdout=text,stderr=err);out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0,err;v=json.loads(text);assert v['passed']is True and v['staged']is False and v['parent_launches']==0 and v['model_stat_hash_open_decode']==0;value['preflight']=v;out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(dict(report=str(out),root=root,passed=True,source_files=v['files'],staged=False,parent_SDK_model_C_locks=0,policy_variant='A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1'),indent=2))
finally:s.close();c.close()
