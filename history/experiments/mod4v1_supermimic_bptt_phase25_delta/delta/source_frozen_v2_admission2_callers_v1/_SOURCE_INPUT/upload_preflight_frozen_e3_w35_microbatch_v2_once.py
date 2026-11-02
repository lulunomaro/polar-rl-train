# NEW V2 dependency-complete evaluation purpose; do not replay consumed failedV1.
"""Upload pinned source ONLY and preflight new candidate-quality eval purpose.
No native parent/SDK/model/C/lock operations; native_root is already fully closed.
"""
from pathlib import Path
import json,sys,time,hashlib,shlex,posixpath
R=Path(__file__).resolve().parent;P=R/'payload_frozen_microbatch_v2';marker=R/'FROZEN_E3_W35_BATCH_V2_SOURCE_INPUT_ONCE.json';out=R/'reports/FROZEN_E3_W35_BATCH_V2_SOURCE_PREFLIGHT_V1.json';assert not marker.exists()and not out.exists();closed=json.loads((R/'reports/A1_ADMISSION2_QUALITY_BOUNDARY_CLOSED_TRUTH_V1.json').read_bytes());assert closed['all8_original_actual_wait_fullsave_semantic_success']and closed['actual_trained_roles']==['E3','W35'];native=closed['root'];old='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700';stager=R/'source_stage_a1_microbatch_eval_v2/stage_a1_microbatch_eval_v2.py';b=stager.read_bytes();assert len(b)==32953 and hashlib.sha256(b).hexdigest()=='9c788fc5435dcbe2af25d13390c2fb008be77c23fbe83104b170d8091cb72952';idx=(P/'MICROBATCH_STAGE_INDEX_V2.json').read_bytes();assert len(idx)==4886 and hashlib.sha256(idx).hexdigest()=='69688e86528e400f188de3f147614cde5c66f86985adaceed805af800819dc50';manifest=json.loads((R/'reports/FROZEN_MICROBATCH14_LOCAL_SOURCE_PAYLOAD_V2.json').read_bytes());assert len(manifest['files'])==14

# Previous physical V1 is consumed and fully waited; V2 changes one missing source dependency.
prior_pointer=json.loads((R/'FROZEN_E3_W35_BATCH_V1_LATEST_CLOSED_RESULT_PATH.json').read_bytes());prior=json.loads(Path(prior_pointer['path']).read_bytes());prior_exit=prior['top']['PARENT_EXIT_SCOPE.json'];assert all(prior_exit[k]is True for k in('all_own_children_waited','original_single_GPU_private_EX_released','original_global_finite_EX_released'));assert len(prior['rows'])==2 and all('resume_runtime_contracts_v3'in x['WORKER_ERROR']['error']for x in prior['rows'])

run='MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root='/home/lc01/Zonglin Li/zonglin2/tasks/'+run;input_root=root+'_SOURCE_INPUT';gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842';value=dict(kind='NEW_FROZEN_MICROBATCH_SOURCE_PREFLIGHT_NOT_ADMISSION',root=root,group_id=run,input_root=input_root,native_source_root=native,original_group_root=old,GPU_UUID=gpu,epoch=time.time(),not_yet_staged_or_dispatched=True);marker.write_text(json.dumps(value,indent=2),encoding='utf-8')
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
 upload(input_root+'/MICROBATCH_STAGE_INDEX_V2.json',idx);upload(input_root+'/stage_a1_microbatch_eval_v2.py',b)
 argv=[input_root+'/stage_a1_microbatch_eval_v2.py','--original-group-root',old,'--source-dir',input_root+'/source','--source-index',input_root+'/MICROBATCH_STAGE_INDEX_V2.json','--native-root',native,'--new-root',root,'--group-id',run,'--gpu-uuid',gpu,'--preflight-only'];value.update(argv=argv,uploaded_sources=pins,stager_SHA=hashlib.sha256(b).hexdigest(),source_index_SHA=hashlib.sha256(idx).hexdigest());i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -u -B '+' '.join(map(shlex.quote,argv)),timeout=240);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();value.update(returncode=rc,stdout=text,stderr=err);out.write_text(json.dumps(value,indent=2),encoding='utf-8');assert rc==0,err;v=json.loads(text);assert v['passed']is True and v['staged']is False and v['parent_launches']==0 and v['model_stat_hash_open_decode']==0;value['preflight']=v;out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(dict(report=str(out),root=root,GPU_UUID=gpu,passed=True,source_files=v['files'],staged=False,parent_SDK_model_C_locks=0,native_closed_producer_steps={k:v['native_boundary']['producer_evidence'][k]['actual_BPTT_policy_steps']for k in('E3','W35')}),indent=2))
finally:s.close();c.close()
