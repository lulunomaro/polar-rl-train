"""Upload small pinned V5 inputs and run ONLY read-only source preflight.
NEW native destination remains absent; no owner/SDK/selected PT/C or locks.
"""
from pathlib import Path
import json,sys,time,datetime,hashlib,shlex
R=Path(__file__).resolve().parent;P=R/'payload_a1_v5_small_source';S=R/'source_stage_a1_native_v5';marker=R/'A1_NATIVE_V5_SOURCE_INPUT_ONCE.json';out=R/'reports/A1_NATIVE_V5_ACTUAL_SOURCE_PREFLIGHT_V1.json';assert not marker.exists()and not out.exists()
software=json.loads((R/'reports/LEGACY_A0_A1_FULL_RESUME_CPU_V2.json').read_bytes());assert software['returncode']==0 and software['receipt']['passed']and software['native_expert_BPTT_steps']==0
indexraw=(P/'SEALED_A1_SOURCE_INDEX_V5.json').read_bytes();assert hashlib.sha256(indexraw).hexdigest()=='ef4174c9955fa6a5f28fbff2550b1922ebfedacbd09efb1de0b33b990f7dc467';index=json.loads(indexraw);files={}
for row in index['files']:
 raw=(P/'source'/row['source_relative']).read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['SHA'];files['source/'+row['source_relative']]=raw
for name,sha in [('stage_a1_native_v5.py','2f8bc706744b2efa7f7bd4b4b960125baad833b02f6afdc376814c8c071b05eb'),('dispatch_a1_native_v5_once.py','7178d8abfb4cf06d943bb2a4a7ea7cdf8e34102ffa9b1bba0d003385cb257319')]:
 raw=(S/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha;files[name]=raw
files['SEALED_A1_SOURCE_INDEX_V5.json']=indexraw
native=json.loads((R/'SCHEDULE_CONFIG_REPAIRED_OWNER_DISPATCH_ONCE.json').read_bytes())['root'];run='MOD4V1_A1_RAW35_V5_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root='/home/lc01/Zonglin Li/zonglin2/tasks/'+run;inputroot=root+'_SOURCE_INPUT'
args=[inputroot+'/stage_a1_native_v5.py','--source-plan',native+'/SOURCE_PLAN.json','--source-dir',inputroot+'/source','--source-index',inputroot+'/SEALED_A1_SOURCE_INDEX_V5.json','--vendor-dir',native+'/roles/E0/worker_sources/supermimic_vendor_v2','--deps-dir',native+'/roles/E0/worker_sources/sm_deps','--assets-dir',native+'/software/pinned_assets','--new-root',root,'--run-id',run,'--target-bptt-steps','3000']
value=dict(kind='NEW_A1_V5_SEPARATE_SOURCE_INPUT_READONLY_PREFLIGHT_PURPOSE',root=root,run_id=run,input_root=inputroot,preflight_argv=args,uploaded_source_pins={k:dict(bytes=len(v),SHA=hashlib.sha256(v).hexdigest())for k,v in files.items()},source_index_SHA=hashlib.sha256(indexraw).hexdigest(),new_native_root_created=False,owner_SDK_selected_PT_C_GO_locks_operations=0)
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
