"""Parent-authorized new PH11 metadata/pathset-only adapter derivation. No original payload or Git write here."""
from pathlib import Path
import json,hashlib,ast,traceback
W=Path(r'F:\RMPOLAR-RL\repo-lqr-robust');R=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102');C=Path(__file__).resolve().parent;N=W/'history/experiments/mod4v1_robust_traditional_phase12_PENDING'
def sha(b):return hashlib.sha256(b).hexdigest()
def fresh(p,b):
 assert not p.exists(),str(p)
 with p.open('xb')as f:f.write(b)
def main():
 oldp=C/'record_phase11_adapter.py';raw=oldp.read_bytes();old=raw.decode('utf-8');s=old;edits=[];A=R/'ARCHIVE_PHASE11_PARENT_PATHSET_REPAIR_002.json';araw=A.read_bytes();a=json.loads(araw);ah=sha(araw)
 assert a['approved']is True and a['kind']=='NEW_PREHELPER_FINITE_PATHSET_ASSUMPTION_REPAIR_NOT_SOURCE_RECAPTURE_OR_HELPER_REPLAY'
 orig=C/'ARCHIVE_PHASE11_PARENT_RECORD_AUTHORIZATION.json';oa=load_original=json.loads(orig.read_bytes());assert sha(orig.read_bytes())==a['original_authorization_SHA']
 oldnames={Path(e['path']).name for e in oa['extra_operation_cover']}|{orig.name,'NOTE.md','record_phase11_adapter.py'};assert len(oldnames)==14
 assert {p.name for p in C.iterdir()if p.is_file()}==oldnames|{Path(__file__).name},'Unexpected pre-derivation cover file'
 oldpins={name:sha((C/name).read_bytes())for name in oldnames}
 assert oldp.read_bytes()==(N/'ARCHIVE_PHASE11_OPERATION_FAILURE_SOURCE_001.py').read_bytes()
 failure_names=['ARCHIVE_PHASE11_OPERATION_FAILURE_001.txt','ARCHIVE_PHASE11_OPERATION_FAILURE_SOURCE_001.py','ARCHIVE_PHASE11_PATHSET_DIFFERENCE_001.json'];lineage={name:dict(bytes=(N/name).stat().st_size,SHA=sha((N/name).read_bytes()))for name in failure_names}
 assert lineage['ARCHIVE_PHASE11_PATHSET_DIFFERENCE_001.json']['SHA']==a['first_failure_difference_SHA']
 difference=json.loads((N/failure_names[2]).read_bytes());assert difference['missing_expected_names']==[]and difference['extra_names_not_read_or_admitted']==[a['only_extra_excluded']]and difference['helper_calls']==0
 assert not(C/'PARENT_AUTHORITY_AND_FREEZE.json').exists()and not(C/'STAGING_PLAN.json').exists()and not(W/'history/experiments/20261104-mod4v1-robust-traditional-phase11.json').exists()and not(N/'ARCHIVE_PHASE11_RECEIPT.json').exists()
 def change(x,y):
  nonlocal s
  assert s.count(x)==1,(x,s.count(x));s=s.replace(x,y,1);edits.append(dict(before=x,after=y,occurrences=1))
 change("INITIAL_MAIN='b77112990fbcd1869f79031b170556f5ca39e5b7'",'REPAIR_SHA='+repr(ah)+';EXCLUDED_SOURCE_LOG='+repr(a['only_extra_excluded'])+';REPAIR_LINEAGE='+repr(lineage)+';ORIGINAL_FAILED_ADAPTER_SHA='+repr(sha(raw))+"\nINITIAL_MAIN='b77112990fbcd1869f79031b170556f5ca39e5b7'")
 change("assert actual==allowed,'SOURCE pathset changed; no recapture'","assert actual==allowed|{EXCLUDED_SOURCE_LOG},'SOURCE pathset changed; no recapture'")
 change("assert {x.relative_to(WT).as_posix()for x in P.rglob('*')if x.is_file()}==allowed","assert {x.relative_to(WT).as_posix()for x in P.rglob('*')if x.is_file()}==allowed|{EXCLUDED_SOURCE_LOG}")
 change('assert len(copied)==12',"assert len(copied)==12\n assert sha((C/'ARCHIVE_PHASE11_PARENT_PATHSET_REPAIR_002.json').read_bytes())==REPAIR_SHA\n repair=load(C/'ARCHIVE_PHASE11_PARENT_PATHSET_REPAIR_002.json');assert repair['approved']is True and repair['kind']=='NEW_PREHELPER_FINITE_PATHSET_ASSUMPTION_REPAIR_NOT_SOURCE_RECAPTURE_OR_HELPER_REPLAY'")
 change('def frozen_small():',"def frozen_small():\n  assert sha((C/'ARCHIVE_PHASE11_PARENT_PATHSET_REPAIR_002.json').read_bytes())==REPAIR_SHA")
 change('assert len(cover)==16',"assert len(cover)==23\n expected_cover_names=set(copied)|{'NOTE.md','record_phase11_adapter.py','PARENT_AUTHORITY_AND_FREEZE.json','STAGING_PLAN.json'}|set(repair['new_exact_formal_cover_names'])\n assert len(expected_cover_names)==23 and{Path(p).name for p in cover}==expected_cover_names and all(Path(p).parent.as_posix()==OWN for p in cover),'Unexpected finite cover names/count'")
 change("status='ONE_PARENT_AUTHORIZED_CAPTURED_VERSION_ONLY_ORIGINAL_LIVE_AFTER_UNKNOWN'","status='ONE_PARENT_AUTHORIZED_CAPTURED_VERSION_ONLY_ORIGINAL_LIVE_AFTER_UNKNOWN',repair_authorization_SHA=REPAIR_SHA,excluded_source_name_not_read_hashed_staged=EXCLUDED_SOURCE_LOG,first_prehelper_failure_lineage=REPAIR_LINEAGE,original_failed_adapter_SHA=ORIGINAL_FAILED_ADAPTER_SHA")
 change("status='FINITE_PATH_AND_FROZEN_HASH_PREREGISTRATION_NOT_WHOLE_HISTORY_OR_PENDING'","status='FINITE_PATH_AND_FROZEN_HASH_PREREGISTRATION_NOT_WHOLE_HISTORY_OR_PENDING',repair_authorization_SHA=REPAIR_SHA,excluded_source_name=EXCLUDED_SOURCE_LOG,first_prehelper_failure_lineage=REPAIR_LINEAGE")
 change("status='PH11_ONE_ORIGINAL_HELPER_RECORD_COMMIT_ANNOTATEDTAG_ATOMIC_OWNREFS_REMOTE_VERIFIED'","status='PH11_ONE_ORIGINAL_HELPER_RECORD_COMMIT_ANNOTATEDTAG_ATOMIC_OWNREFS_REMOTE_VERIFIED',repair_authorization_SHA=REPAIR_SHA,excluded_source_name_not_read_hashed_staged=EXCLUDED_SOURCE_LOG,first_prehelper_failure_lineage=REPAIR_LINEAGE,original_failed_adapter_SHA=ORIGINAL_FAILED_ADAPTER_SHA")
 inverse=s
 for e in reversed(edits):inverse=inverse.replace(e['after'],e['before'],1)
 assert inverse.encode('utf-8')==raw,'Exact byte inverse to failed metadata adapter'
 assert ast.dump(ast.parse(inverse),include_attributes=False)==ast.dump(ast.parse(old),include_attributes=False)
 ast.parse(s);dest=C/'record_phase11_adapter_v2.py';assert not dest.exists()
 copies={A.name:araw,**{name:(N/name).read_bytes()for name in failure_names}}
 assert set(a['new_exact_formal_cover_names'])=={dest.name,Path(__file__).name,'PATHSET_REPAIR_DERIVATION_002.json',*copies}
 for name,b in copies.items():fresh(C/name,b);assert sha((C/name).read_bytes())==sha(b)
 fresh(dest,s.encode('utf-8'))
 ledger=dict(status='PARENT_REPAIR002_EXACT_NEW_METADATA_ADAPTER_HUNKS_BEFORE_FIRST_HELPER',original_failed_source_SHA=sha(raw),new_adapter_SHA=sha(dest.read_bytes()),new_deriver_SHA=sha(Path(__file__).read_bytes()),parent_repair_SHA=ah,declared_hunks=edits,exact_byte_inverse=True,inverse_AST_equal=True,old_formal14_SHA_unchanged=oldpins,first_failure_lineage=lineage,source_allowed_count=856,source_extra_excluded_exact=a['only_extra_excluded'],extra_log_payload_read_hash_copy_stage_delete=False,cover_count_before_freezeplan=21,final_cover_count=23,expected_total_allA=881,original_helper_calls_so_far=0,no_SOURCE_or_original_adapter_changed=True,no_native_or_model_or_physics_or_Git_write=True)
 fresh(C/'PATHSET_REPAIR_DERIVATION_002.json',(json.dumps(ledger,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8'))
 assert all(sha((C/name).read_bytes())==h for name,h in oldpins.items())and len([p for p in C.iterdir()if p.is_file()])==21
 print(json.dumps(dict(status=ledger['status'],old_adapter_SHA=sha(raw),new_adapter_SHA=sha(dest.read_bytes()),repair_SHA=ah,hunks=len(edits),exact_inverse=True,cover_current=21,expected_total=881),ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except BaseException:
  N.mkdir(parents=True,exist_ok=True);i=1
  while(N/f'ARCHIVE_PHASE11_OPERATION_FAILURE_{i:03d}.txt').exists():i+=1
  fresh(N/f'ARCHIVE_PHASE11_OPERATION_FAILURE_{i:03d}.txt',(traceback.format_exc()+'\nNew metadata derivation failed; STOP. No automatic fix/replay/helper.\n').encode('utf-8'));fresh(N/f'ARCHIVE_PHASE11_OPERATION_FAILURE_SOURCE_{i:03d}.py',Path(__file__).read_bytes());raise
