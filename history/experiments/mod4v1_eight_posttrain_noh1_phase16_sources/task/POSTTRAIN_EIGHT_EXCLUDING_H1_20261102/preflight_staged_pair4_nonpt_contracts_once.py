"""Onlyactualstagedsource verify andW35dedicatedindex binding; nomain/SDK/PT/locks/Cbytes."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
out=D/'reports/PAIR4_NONPT_SOURCE_PREFLIGHT_V2.json';assert not out.exists();stage=json.loads((D/'reports/PAIR4_GENERIC_V2_NONPT_STAGE_RESULT.json').read_bytes());assert stage['actual_stage_passed']and not stage['owner_launched'];root=stage['root'];code="""from pathlib import Path
import sys,json,hashlib,time
B=Path(%r);sys.path.insert(0,str(B));import eight_posttrain_original_owner_v1 as owner
p=json.loads((B/'OWNER_PLAN.json').read_bytes());assert not(B/'OWNER_STARTED.json').exists();owner.verify_sources(p);w=next(e for e in p['entries']if e['role']=='W35');J=Path(w['job_root']);sys.path.insert(0,str(J));import mod4v1_w35_posttrain_protocol_v2 as q
T=w['task_template'];M=json.loads((J/w['manifest_file']).read_bytes());assert T['kind']==q.KIND and T['source_SHA']==q.SOURCE_SHA and T['source_bytes']==q.SOURCE_BYTES and T['source_iteration']==32643 and T['source_Adam_step']==654500 and T['source_LR']==1.0000000000000004e-05
idx=J/'MOD4V1_W35_POSTTRAIN_DERIVATION_INDEX.json';h=hashlib.sha256(idx.read_bytes()).hexdigest();r=next(x for x in M['files']if x['relative']==idx.name);assert r['SHA']==h and T['derivation_index_SHA']==h;assert M['kind']=='MOD4V1_W35_POSTTRAIN_INSTALL_ACTUAL_V1'
for e in p['entries']:
 A=Path(e['job_root']);assert e['native0pt_evidence_file']=='evidence/NEW_ASSET_NATIVE_ACTUAL.json'and not(A/'GO_PRODUCTION.json').exists()and not(A/'TASK.json').exists()and not(A/'ROOT_ADMISSION_ACTUAL.json').exists()
v={'kind':'PAIR4_STAGED_ORIGINAL_OWNER_SOURCE_VERIFY_ONLY_NOT_READY','epoch':time.time(),'root':str(B),'roles':[e['role']for e in p['entries']],'W35_actualsource8d_constants_and_dedicated_index_binding_verified':True,'all_prior_full20k_closed_history_proofs_bound':True,'owner_main_locks_Cbytes_PT_SDK_GO_operations':0};f=B/'SOURCE_ONLY_PREFLIGHT_VERIFIED.json';assert not f.exists();f.write_text(json.dumps(v,indent=2));print(json.dumps(v))
"""%root;c=connect72();report=dict(root=root)
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=180);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();report.update(returncode=rc,stderr=err,actual_preflight=json.loads(txt)if rc==0 else txt);assert rc==0,(rc,err)
finally:c.close();out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(out);print(json.dumps(report,indent=2))
