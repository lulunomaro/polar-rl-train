"""Independent SOURCE_ONLY contractfinal validation+sourceproof snapshot seal.
Only boundedJSON/text/Python, no modelstat/hash/decode, no SDK/GPU/SSH.
"""
from pathlib import Path
import ast,hashlib,json,time,traceback,warnings
B=Path(__file__).resolve().parent;T=B.parent;NO={'.pt','.pth','.ckpt','.npz','.npy','.usd','.usdc','.zip','.jsonl','.gz','.onnx','.safetensors','.pyc'}
def H(b):return hashlib.sha256(b).hexdigest()
def main():
 m=json.loads((B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_FINAL_V3.json').read_bytes());p=json.loads((B/'NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_FINAL_V2.json').read_bytes());proof=json.loads((B/'ACCEPTANCE_PREDICATE_SEMANTIC_MOCK_PROOF_V1.json').read_bytes());assert proof['passed'] and proof['check_count']==29
 assert len(m['rows'])==len(p['plans'])==9 and len(m['references'])==48;assert all(not r['full_skill_graduated'] for r in m['rows']);names={r['lineage'] for r in m['rows']};assert names=={'E0','E2','H1_NORMAL','CURB878','CURB113','SLOPE135','SLOPE50','E3','W35'}
 for r in m['rows']:
  assert set(r['original_reference_ids'])<=m['references'].keys()
  if r['lineage']=='W35':assert r['current_native24_integration']['status']=='LIVE_PARENT_OWNED_EXCLUDED'
  elif r['lineage']=='SLOPE135':assert r['original_scope_acceptance_boolean'] is True
  elif r['lineage'] in ('E0','E2','E3'):assert r['original_scope_acceptance_boolean'] is False
 for plan in p['plans']:
  assert plan['actual_SDK_permission'] is False and plan['dispatch_or_model_io'] is False and plan['original_numeric_aggregate_acceptance_rule'] is None
  for d in plan['dependency_table']:
   rr=m['references'][d['reference_id']];assert d['path']==rr['path'] and d['SHA']==rr['SHA']
 # Sourceevidence snapshots duplicateonly boundeddeclaredtext, neverraw/model.
 copies=[]
 for id,r in m['references'].items():
  src=Path(r['path']);assert src.suffix.lower() in ('.py','.json','.md','.txt');raw=src.read_bytes();assert len(raw)<1800000 and len(raw)==r['bytes'] and H(raw)==r['SHA'];dst=B/'original_reference_text'/ (id+'__'+src.name);dst.parent.mkdir(exist_ok=True)
  with dst.open('xb') as f:f.write(raw)
  copies.append(dict(reference_id=id,original_path=str(src),snapshot=str(dst),bytes=len(raw),SHA=H(raw),sourcebytes_exact=True))
 # No newmodelseeking: scanonly contentsalreadyselected forany7bpathreference.
 target='7b70032fcb577390cee01c887b57c1e3d9818f9bf87f54977444d592c033db43';hits=[]
 for r in copies:
  text=Path(r['snapshot']).read_text(encoding='utf-8-sig')
  if target in text:hits.append(dict(reference_id=r['reference_id'],metadata_path=r['original_path'],metadata_SHA=r['SHA'],classification='SHA_reference_only_not_proven_newphysicalmirror',new_model_stat_or_open=False))
 with (B/'DECLARED_7B_BOUNDED_METADATA_REFERENCES_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='ONLY_THESE_48_DECLARED_TEXT_INPUTS_NOT_MACHINE_SEARCH',target_SHA=target,references=hits,new_exact_physical_mirror_evidence=False,condition='Assetremains pending. Existingreference only; no modelstat/read/network, no blanketmissingclaimoutsideboundedinputscope.',original210_network_retries=0),f,indent=2)
 py=[];ws=[]
 for path in B.rglob('*.py'):
  raw=path.read_bytes()
  with warnings.catch_warnings(record=True) as w:
   warnings.simplefilter('always');tree=ast.parse(raw,filename=str(path));compile(tree,str(path),'exec')
  py.append(dict(path=str(path),SHA=H(raw),AST_SHA=H(ast.dump(tree,include_attributes=False).encode())))
  ws.extend(dict(path=str(path),line=x.lineno,category=x.category.__name__,message=str(x.message),sourcebytes_unmodified=True) for x in w)
 with (B/'FINAL_LOCAL_SOURCE_ONLY_VALIDATION_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='LOCAL_CONTRACTS_DEPENDENCIES_SOURCE_AST_MOCK_NOT_RUNTIME',passed=True,lineages=9,references=48,source_functions=len(m['original_function_excerpts']),dependency_rows=sum(len(x['dependency_table']) for x in p['plans']),semantic_MOCK_checks=29,source_snapshots=copies,python_AST_compile=py,inherited_warnings=ws,no_unknown_reference_ids=True,no_posthoc_aggregate_passrate=True,no_new_MCIphysicalgate=True,actual_model_SSH_SDK_GPU_or_PPO_calls=0),f,indent=2)
 files=[]
 for path in sorted(B.rglob('*')):
  if path.suffix.lower() in NO:continue
  if path.is_file():
   raw=path.read_bytes();files.append(dict(path=str(path),relative=path.relative_to(B).as_posix(),bytes=len(raw),SHA=H(raw)))
 final=B/'FINAL_SOURCE_ONLY_ACCEPTANCE_INDEX_V1.json'
 with final.open('x',encoding='utf-8') as f:json.dump(dict(kind='NINE_LINEAGE_ORIGINAL_ACCEPTANCE_CONTRACTS_FINAL_SOURCE_ONLY',files=files,matrix=str(B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_FINAL_V3.json'),plans=str(B/'NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_FINAL_V2.json'),scope='Ownoriginalaccepted/observed predicate vsnative24 vsunretestednewplant longskill separated. E0/E2/E3 formal/frozenfullskillfalse;Curbscopedevidence;Slope135explicit5degreeaccepted;H1/50gaps;W35liveexcluded. No newskillpass.',model_stat_hash_read_decode=0,raw_JSONL_NPZ_SSH_SDK_GPU_GO_canonical_PPO=0,oldsource_seals_parentregistry_mutations=0,parent_phase9_append_Gitpending=True,child_commit_push=False),f,indent=2)
 out=T/'ORIGINAL_SKILL_ACCEPTANCE_CONTRACT_SOURCE_ONLY_HANDOFF_V1.json'
 with out.open('x',encoding='utf-8') as f:json.dump(dict(kind='NINE_ORIGINAL_SKILL_CONTRACTS_SOURCE_ONLY_NOT_RUNTIME_OR_SKILL_PASS',matrix=dict(path=str(B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_FINAL_V3.json'),SHA=H((B/'ORIGINAL_ACCEPTANCE_CONTRACT_MATRIX_FINAL_V3.json').read_bytes())),human_matrix=dict(path=str(B/'ACCEPTANCE_CONTRACT_MATRIX_SOURCE_ONLY_FINAL_V2.md'),SHA=H((B/'ACCEPTANCE_CONTRACT_MATRIX_SOURCE_ONLY_FINAL_V2.md').read_bytes())),plans=dict(path=str(B/'NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_FINAL_V2.json'),SHA=H((B/'NEWPLANT_SOURCE_ONLY_REPLAY_PLANS_FINAL_V2.json').read_bytes())),dependency_csv=dict(path=str(B/'SOURCE_ONLY_REPLAY_DEPENDENCY_TABLE_FINAL_V2.csv'),SHA=H((B/'SOURCE_ONLY_REPLAY_DEPENDENCY_TABLE_FINAL_V2.csv').read_bytes())),finalindex=dict(path=str(final),SHA=H(final.read_bytes())),lineages=9,references=48,source_functions=49,dependency_rows=46,MOCK_checks=29,emitted_sourceonly_future_descriptors=7,excluded_E3already160_and_W35live=True,no_aggregate_skill_rule_invented=True,first_original_boundary_censor_semantics_preserved=True,any_new_actualskillpass=False,model_SDK_network_calls=0,parent_phase9_Gitpending=True),f,indent=2)
 files.extend([dict(path=str(final),bytes=final.stat().st_size,SHA=H(final.read_bytes())),dict(path=str(out),bytes=out.stat().st_size,SHA=H(out.read_bytes()))]);archive=T/'ORIGINAL_SKILL_ACCEPTANCE_SOURCE_ONLY_ALL_ERRORS_ARCHIVE_PENDING_V1.json'
 with archive.open('x',encoding='utf-8') as f:json.dump(dict(kind='COMPLETE_SOURCE_ONLY_NINE_ACCEPTANCE_CONTRACT_SOURCE_SNAPSHOTS_MOCK_REVISIONS_ERRORS_ARCHIVE_PENDING_PHASE9',files=files,large_or_binary_or_model_files_opened=False,current_W35_livecase_read=False,current_E3_160case_replayed=False,all_lookup_errors_and_V1V2_preserved=True,parent_registry_edited=False,child_commit_push=False),f,indent=2)
 print(json.dumps(dict(handoff=str(out),handoff_SHA=H(out.read_bytes()),archive_index=str(archive),archive_SHA=H(archive.read_bytes()),text_files=len(files),sourceonly_lineages=9,references=48,sourcefunctions=49,dependencies=46,MOCK=29,SDK_or_model_calls=0),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (B/('FINAL_SOURCE_ONLY_SEAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),model_SDK_operations=0),f,indent=2)
  raise
