"""Originalowner.verify_sources only aftersoftwarestage; noowner.main/leases/SDK/PT/Cbytes, noTask/GO/Ready. Provesplan/filecontractnotactualGPUadmission."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
out=D/'reports/PAIR2_PAIR3_NONPT_SOURCE_PREFLIGHT_V2.json';assert not out.exists();index=json.loads((D/'parent_source/GENERIC_PAIR2_PAIR3_LOCAL_PAYLOAD_INDEX_V2.json').read_bytes());c=connect72();rows=[]
try:
 for g in index['groups']:
  previous=json.loads((D/'reports'/('PAIR'+str(g['pair'])+'_GENERIC_V2_NONPT_STAGE_RESULT.json')).read_bytes());assert previous['actual_stage_passed']and previous['owner_launched']is False;root=g['root'];code="""from pathlib import Path
import sys,json,time
B=Path(%r);sys.path.insert(0,str(B));import eight_posttrain_original_owner_v1 as o
p=json.loads((B/'OWNER_PLAN.json').read_bytes());assert not(B/'OWNER_STARTED.json').exists();o.verify_sources(p)
for e in p['entries']:
 assert e['native0pt_evidence_file']=='evidence/NEW_ASSET_NATIVE_ACTUAL.json'and not any(k.startswith(('native2pt','native3pt'))for k in e)
 assert e['max_additional_updates']==20 and e['source_family']in('e0_e2_e3','e1')
 J=Path(e['job_root']);assert not(J/'TASK.json').exists()and not(J/'GO_PRODUCTION.json').exists()and not(J/'ROOT_ADMISSION_ACTUAL.json').exists()
r={'kind':'ORIGINAL_OWNER_SOURCE_VERIFY_ONLY_NOT_READY_OR_ADMISSION','epoch':time.time(),'root':str(B),'roles':[e['role']for e in p['entries']],'actual_nonPT_source_manifest_and_historical_proof_binding_verified':True,'models_stat_read_hash_decode_SDK_Cbytes_or_lock_ops':0,'owner_main_not_called':True};f=B/'SOURCE_ONLY_PREFLIGHT_VERIFIED.json';assert not f.exists();f.write_text(json.dumps(r,indent=2));print(json.dumps(r))
"""%root;i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=180);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();row={'pair':g['pair'],'root':root,'returncode':rc,'stderr':err};row.update(actual_preflight=json.loads(txt)if rc==0 else txt);rows.append(row);assert rc==0,(rc,err)
finally:
 c.close();out.write_text(json.dumps({'kind':'NONPT_SOURCE_PREFLIGHT_NOT_TRAINING','rows':rows},indent=2),encoding='utf-8');print(out);print(json.dumps(rows,indent=2))
