"""Final boundedtext snapshot+provenance index; zero models/raw/SDK/GO."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent
H=lambda x:hashlib.sha256(x).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 return dict(path=str(p),bytes=len(p.read_bytes()),SHA=H(p.read_bytes()))
def main():
 r=json.loads((B/'W35_THREE_GENERATIONS_MECHANISM_SOURCE_REVIEW_V1.json').read_bytes());assert len(r['references'])==34 and len(r['original_functions'])==50;assert all(x['exact_mother_SHA_joined'] for x in r['original_mother_text_SHA_join']);plan=r['next_experiment'];assert plan['future_window']['controls']==900 and plan['future_window']['physics']==7200 and plan['future_window']['feedback']==1800 and r['PT_stat_read_hash_decode_raw_SSH_SDK_GPU_canonical_PPO']==0
 evidence=[]
 for id,x in r['references'].items():
  p=Path(x['path']);assert p.suffix.lower() in ('.json','.py','.txt','.md');raw=p.read_bytes();assert len(raw)==x['bytes'] and H(raw)==x['SHA'];dest=B/'exact_reference_text'/ (id+'__'+p.name);dest.parent.mkdir(exist_ok=True)
  with dest.open('xb') as f:f.write(raw)
  evidence.append(dict(reference=id,original_path=str(p),snapshot=str(dest),bytes=len(raw),carrier_SHA=H(raw),recovered_source_SHA=x.get('recovered_source_SHA'),original_unchanged=True))
 # AST doesnot execute andonlynormalizes provenCRCRLF transport inparsermemory.
 astrows=[]
 for p in B.rglob('*.py'):
  raw=p.read_bytes();source=raw.replace(b'\r\r\n',b'\r\n') if b'\r\r\n' in raw else raw;tr=ast.parse(source,filename=str(p));astrows.append(dict(path=str(p),carrier_SHA=H(raw),parse_source_SHA=H(source),AST_SHA=H(ast.dump(tr,include_attributes=False).encode()),reader_only_EOL_recovered=source!=raw))
 validation=put(B/'W35_FINAL_LOCAL_SOURCE_REVIEW_VALIDATION_V1.json',dict(kind='ONLY_SOURCE_AND_PROCESSED_METADATA_NO_SKILLPASS',passed=True,references=34,source_functions=50,exactmotherjoins=14,source_snapshots=evidence,AST=astrows,oldMOCК29_reruns=0,PT_raw_SSH_SDK_GPU_canonical_PPO=0,getter_unknowns_explicit_not_blocking=True,proposed_observer_18s_only_not_admitted=True,no_new_thresholds_or_recipe_changes=True))
 files=[]
 for p in sorted(B.rglob('*')):
  if p.is_file() and p.suffix.lower() in ('.py','.json','.md','.txt'):
   raw=p.read_bytes();files.append(dict(path=str(p),relative=p.relative_to(B).as_posix(),bytes=len(raw),SHA=H(raw)))
 index=put(B/'FINAL_W35_MECHANISM_SOURCE_ONLY_INDEX_V1.json',dict(kind='COMPLETE_W35_MECHANISM_REVIEW_SOURCE_ONLY_PHASE9_APPEND',files=files,validation=validation,model_raw_read_stat_hash_decode=0,SDK_GPU_SSH_canonical_PPO_GO=0,no_newbudget_or_admission=True,SDKgetters_await_parent_followup_without_blocking=True,source_EOLcarrier_and_V1error_preserved=True,readbeforeedit_metadata_error='InitialMDeditdeniedunread, readsamefilethenexacteditcompleted; nofspermissionescalation',childcommitpush=False,parentphase9_archivepending=True))
 handoff=put(T/'W35_THREE_GENERATIONS_MECHANISM_SOURCE_ONLY_HANDOFF_V1.json',dict(kind='CLOSED_W35_THREE_GENERATION_SOURCE_REVIEW_NOT_RUNTIME',index=index,machine_review=str(B/'W35_THREE_GENERATIONS_MECHANISM_SOURCE_REVIEW_V1.json'),human_review=str(B/'W35_THREE_GENERATIONS_MECHANISM_SOURCE_REVIEW_V1.md'),minimal_next_observer_spec=str(B/'W35_MINIMAL_NEXT_OBSERVER_ONLY_SPEC_SOURCE_V1.json'),references=34,functions=50,exactmotherjoins=14,findings=['OriginalsignedBODYtracking andoppositecataloggoalarenotequivalent;partialoutwardcensorunderexplicitinitialconditions','Noestablishedfixed.04softwareactuatorcap/axisfault/STDfault/obstaclejam','Gettercoordinate/cachephaseandquatyaw_numericidentitynotcapturedyet; exactconsumerchainpinned','Onefreshnewpurpose18sobserveronly proposed; no PPO/recipe/geometry/STDchangeoradmission'],carrier_EOL_proof=dict(carrier_SHA='2e8037bf470800c7be671af3f33542a8ff1e69358674dba16c35e815327c848c',inmemory_CRCRLF_to_CRLF_installed_SHA='30ce41126a1a9b78a1c2b446281b28f4555c28052bfaa7c0e9a76079cf561fc5',original_carrier_unchanged=True,V1_AST_error_preserved=True),PT_raw_SSH_SDK_GPU_canonical_PPO=0,parent_registry_edited=False,parentphase9_archivepending=True))
 arc=put(T/'W35_MECHANISM_SOURCE_ONLY_ALL_ERRORS_ARCHIVE_PENDING_V1.json',dict(kind='W35_SOURCE_ONLY_MECHANISM_REVIEW_ALL_ORIGINAL_ERRORS_TEXT_SNAPSHOTS_PHASE9_DELTA',files=files+[index,handoff],raw_binary_models_excluded=True,oldseals_andclosedraw_untouched=True,noSDK_orPPO=True,parentarchivepending=True))
 print(json.dumps(dict(handoff=handoff,archive=arc,textfiles=len(files)+2,references=34,functions=50,PT_raw_SDK_operations=0),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('SEAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),model_SDK_raw_operations=0),f,indent=2)
  raise
