"""Seal4childSOURCE_ONLY package forparentreview; noPT/raw/SDK/runtime run."""
from pathlib import Path
import ast,hashlib,json,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;H=lambda x:hashlib.sha256(x).hexdigest()
def info(p):
 raw=p.read_bytes();return dict(path=str(p),bytes=len(raw),SHA=H(raw))
def put(p,v):
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 return info(p)
def main():
 contracts=json.loads((B/'ROLE_CONTRACTS.json').read_bytes());proof=json.loads((B/'FOUR_E1_SOURCE_ONLY_MOCK_PROOF_FINAL_V3.json').read_bytes());assert proof['passed'] and proof['check_count']==60
 for name,sha in proof['source_file_SHA'].items():assert H((B/name).read_bytes())==sha,name
 deps=json.loads((B/'FULL_FRESH_N80_D0_D7_SOURCE_DEPENDENCY_GRAPH_V1.json').read_bytes());copies=[]
 for j,x in enumerate(deps['files']):
  p=Path(x['path']);assert p.suffix in ('.py','.json');raw=p.read_bytes();assert H(raw)==x['SHA'];q=B/'dependency_source_text'/ (x['role']+'__'+p.name)
  with q.open('xb') as f:f.write(raw)
  copies.append(dict(original=x['path'],copy=str(q),SHA=H(raw),role=x['role']))
 compile_rows=[]
 for p in B.rglob('*.py'):
  raw=p.read_bytes();parse=raw.replace(b'\r\r\n',b'\r\n') if b'\r\r\n' in raw else raw;tree=ast.parse(parse,filename=str(p));compile(tree,str(p),'exec');compile_rows.append(dict(**info(p),AST_SHA=H(ast.dump(tree,include_attributes=False).encode())))
 interface=json.loads((B/'FOUR_E1_WORKER_PARENT_INTERFACE_SOURCE_V1.json').read_bytes());interface['parent_added_task_metadata_fields']=['source_iteration','source_Adam17','source_LR','asset_SHA','contract_SHA'];interface['compatibility']='Strictvaluechecks added inchildvalidator; descriptorFINAL_V2 containsparentfieldnames. No physicalruntimeedit.'
 current=put(B/'FOUR_E1_WORKER_PARENT_INTERFACE_FINAL_V2.json',interface)
 # PreserveunusedstandaloneSLOPE draft afterdirectparenttask changed to4childgroup.
 legacy=T/'SLOPE135_N80_FRESH_FULLDR_SKILL15S_NOT_FULL20K_RESUME_SOURCE_V1';legacy_files=[]
 for p in sorted(legacy.glob('*')):
  if p.is_file() and p.suffix in ('.py','.json','.md'):legacy_files.append(info(p))
 put(B/'SUPERSEDED_STANDALONE_SLOPE135_SOURCE_ONLY_DRAFT_INDEX_V1.json',dict(kind='NEVER_MODEL_OR_SDK_EXECUTED_SUPERSEDED_BY_DIRECT_GROUP_TASK',files=legacy_files,no_standalone_task_dispatched=True,allsourceversions_preserved=True))
 validation=put(B/'FINAL_FOUR_E1_SOURCE_VALIDATION_V1.json',dict(kind='SOURCE_AST_SYNTHETIC_MOCK_NOT_ACTUAL_PASS',passed=True,workers=4,MOCK_checks=60,MOCK_proof=info(B/'FOUR_E1_SOURCE_ONLY_MOCK_PROOF_FINAL_V3.json'),AST=compile_rows,dependency_copies=copies,exact_original80_factory_prefix_reverse_AST_proof=info(B/'FOUR_E1_ORIGINAL_FACTORY_AST_DIFF_PROOF_V1.json'),actual_N80_API_or_parent_resource_admission=False,source_PT_stat_read_hash_decode_raw_SSH_SDK_GPU_GO_canonical_PPO=0,parent_registry_other5workers_or_supervisor_edits=0))
 files=[]
 for p in sorted(B.rglob('*')):
  if p.is_file() and p.suffix in ('.py','.json','.md','.patch','.txt'):files.append(dict(**info(p),relative=p.relative_to(B).as_posix()))
 index=put(B/'FINAL_FOUR_E1_PARALLEL_N80_SOURCE_INDEX_V1.json',dict(kind='FOUR_E1_N80_FRESH_FULLDR_SINGLE_GPU_PARALLEL_CHILD_WORKER_SOURCE_ONLY',files=files,current_interface=current,worker_basenames={r:c['worker_basename'] for r,c in contracts.items()},validation=validation,no_model_orSDK_execution=True,no_standalonecase_dispatched=True,live_actor_STD_STRICT_and_critic17AdamLRiter_cached_identity=True,saved20k_DR_physically_applied=False,original_scope_only_no_new_passrate=True,parentowns5workers_group_supervisor_freshactualadmission_waitRC0_andall9results=True,parentphase9_archivepending=True,childGit=False))
 runtime_files=[info(p) for p in B.glob('*.py') if not (p.name.startswith(('test_','build_','seal_','finalize_','emit_')))] + [info(B/'ROLE_CONTRACTS.json')]
 handoff=put(T/'E1_N80_FRESH_FULLDR_PARALLEL_FOUR_WORKERS_SOURCE_HANDOFF_V1.json',dict(kind='FOUR_E1_CHILD_WORKER_SOURCE_ONLY_READY_FOR_PARENT_REVIEW_NOT_GPU_PERMISSION',source_root=str(B),final_index=index,current_interface=current,runtime_files_to_stage_same_directory=runtime_files,worker_basenames={r:c['worker_basename'] for r,c in contracts.items()},stable_roles=list(contracts),CLI='python -B WORKER --task CASE/task.json --group-root GROUP_ROOT',parent_task_metadata_compatible=['source_iteration','source_Adam17','source_LR','asset_SHA','contract_SHA'],private_and_globalfinite_EX='Onlyparentholds groupEX, passedfd validatedwithoutchildflock/query',barrier='WORKER_SCENE_READY.json before0step/actor; GROUP_EVAL_START.json afterall9ready, wait900s/originaldeadline; abortwholegroupscopeonstartupERROR',outputs=['FINAL.json','PRE_CLOSE.json','WORKER_ERROR.json','OWN_NEW_SKILL_RAW.npz','OWN_PARTIAL_SKILL_RAW.npz'],scope='EachN80freshownD0-D7, fulltypedPTonecacheliveA0STD/corecacheidentity, NO20kDRhistoryprojection/resume. 3x15soriginalpredicate;SLOPE50own20sdescriptiveaxis.',MOCK_checks=60,dependency_source_files=len(deps['files']),new_admission_or_runtime=False,source_PT_stat_hash_decode_raw_SSH_SDK_GPU_PPO_GO_canonical=0,childcommitpush=False))
 archive=put(T/'E1_N80_PARALLEL_FOUR_WORKERS_SOURCE_ALL_ERRORS_ARCHIVE_PENDING_V1.json',dict(kind='COMPLETE_FOUR_E1_SOURCEONLY_ALL_ERRORS_REVISIONS_SUPERSEDED_DRAFTS_PHASE9_DELTA',files=files+[index,handoff],superseded_neverrun_standalone_files=legacy_files,oldseals_unchanged=True,models_USD_NPZ_raw_notopened=True,actualgroupGPUpermission=False,parentarchivepending=True))
 print(json.dumps(dict(handoff=handoff,archive=archive,source_index=index,sourcefiles=len(files)+2,runtime_stage_files=len(runtime_files),MOCK60=True,PT_SDK_calls=0),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('SEAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_calls=0),f,indent=2)
  raise
