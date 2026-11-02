"""New V6 pinned source upload and source-only preflight; no native owner yet."""
from pathlib import Path
import json,sys,time,datetime,hashlib,shlex
R=Path(__file__).resolve().parent;P=R/'payload_a1_v6_small_source';S=R/'source_native_v6_runtime_compat';marker=R/'A1_NATIVE_V6_SOURCE_INPUT_ONCE.json';out=R/'reports/A1_NATIVE_V6_ACTUAL_SOURCE_PREFLIGHT_V1.json';assert not marker.exists()and not out.exists()
closed=json.loads((R/'reports/A1_NATIVE_V5_CLOSED_TRUTH_V1.json').read_bytes());assert all(closed['parent_exit'][k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))
software=json.loads((R/'reports/LEGACY_A0_A1_FULL_RESUME_CPU_V2.json').read_bytes());assert software['returncode']==0 and software['receipt']['passed']and software['native_expert_BPTT_steps']==0
mean=json.loads((R/'reports/A1_FROZEN_MEAN_POLICY_CPU_V1.json').read_bytes());assert mean['returncode']==0 and mean['receipt']['passed']and mean['receipt']['max_reference_error']==0.0
indexraw=(P/'SEALED_A1_SOURCE_INDEX_V6.json').read_bytes();assert hashlib.sha256(indexraw).hexdigest()=='f12617c45596c752de12050e17132d9dfab0aea8ed1336abe23d8e0ce256fa90';index=json.loads(indexraw);files={}
for row in index['files']:
 raw=(P/'source'/row['source_relative']).read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['SHA'];files['source/'+row['source_relative']]=raw
for name,sha in [('stage_a1_native_v6.py','9c68f5f7c59a5fc0d2ea9cc8d7dcc5eacd3577f795c9f0bdad28bed5ce8aeef0'),('dispatch_a1_native_v6_once.py','7ecab0e372064c0c5ceaccc8f02a79350e9c7a538e3fb158a5426a04dfce38ae')]:
 raw=(S/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha;files[name]=raw
files['SEALED_A1_SOURCE_INDEX_V6.json']=indexraw
native=json.loads((R/'SCHEDULE_CONFIG_REPAIRED_OWNER_DISPATCH_ONCE.json').read_bytes())['root'];run='MOD4V1_A1_RAW35_V6_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root='/home/lc01/Zonglin Li/zonglin2/tasks/'+run;inputroot=root+'_SOURCE_INPUT'
args=[inputroot+'/stage_a1_native_v6.py','--source-plan',native+'/SOURCE_PLAN.json','--source-dir',inputroot+'/source','--source-index',inputroot+'/SEALED_A1_SOURCE_INDEX_V6.json','--vendor-dir',native+'/roles/E0/worker_sources/supermimic_vendor_v2','--deps-dir',native+'/roles/E0/worker_sources/sm_deps','--assets-dir',native+'/software/pinned_assets','--new-root',root,'--run-id',run,'--target-bptt-steps','3000']
value=dict(kind='NEW_A1_V6_SEPARATE_SOURCE_INPUT_READONLY_PREFLIGHT_PURPOSE',root=root,run_id=run,input_root=inputroot,preflight_argv=args,uploaded_source_pins={k:dict(bytes=len(v),SHA=hashlib.sha256(v).hexdigest())for k,v in files.items()},source_index_SHA=hashlib.sha256(indexraw).hexdigest(),prior_V5_closed_and_all_cost_wait_leases_settled=True,only_pose_stale_sentinel_and_published_app_alias_compatibility_changed=True,new_native_root_created=False,owner_SDK_selected_PT_C_GO_locks_operations=0)
marker.write_text(json.dumps(value,indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 s.mkdir(inputroot);s.mkdir(inputroot+'/source')
 for name,raw in files.items():
  with s.open(inputroot+'/'+name,'wb')as f:f.write(raw)
 cmd="CUDA_VISIBLE_DEVICES='' "+shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B '+' '.join(shlex.quote(x)for x in args)
 i,o,e=c.exec_command(cmd,timeout=600);i.close();txt=o.read().decode(errors='replace');err=e.read().decode(errors='replace');rc=o.channel.recv_exit_status();value.update(returncode=rc,stdout=txt,stderr=err)
 if rc==0:value['preflight']=json.loads(txt)
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2));assert rc==0,(rc,err)
finally:s.close();c.close()
