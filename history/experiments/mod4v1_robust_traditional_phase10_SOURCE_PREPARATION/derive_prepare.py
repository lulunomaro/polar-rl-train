"""Derive NEW finite PH10 source-only collector; never execute/edit the old collector."""
from pathlib import Path
import ast,hashlib,traceback
P=Path(__file__).resolve().parent;WT=P.parents[2]
def main():
 old=WT/'history/experiments/mod4v1_robust_traditional_phase9_SOURCE_PREPARATION/prepare_source.py';raw=old.read_bytes();text=raw.decode('utf-8');changes=[]
 def change(a,b):
  nonlocal text
  assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b);changes.append(a)
 prior=next(ast.literal_eval(n.value)for n in ast.parse(text).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PRIOR'for t in n.targets))
 prior.append(('mod4v1_robust_traditional_phase9_SOURCE_PREPARATION/FINAL_SOURCE_MANIFEST.json','7b7d2633a25dad356809a56ddfa2d546f1cded10'))
 change(next(x for x in text.splitlines()if x.startswith('PRIOR=')),'PRIOR='+repr(prior))
 change('PH9 bounded source snapshot only.','PH10 bounded source snapshot only.')
 change("TEXT={", "TEXT={'.uvprojx','.uvoptx','.ioc','.sct','.inc','.ld','.cfg','.dbgconf',")
 start=text.index('def forbidden(p):');end=text.index('def main():',start)
 text=text[:start]+'''def forbidden(p):
 low=str(p).replace('\\\\','/').lower()
 if any(t.lower()in('__pycache__','.git','.venv','node_modules')for t in p.parts)or any(t.startswith('.dsh-office-')for t in p.parts):return 'runtime_git_or_private_preview_cache'
 if p.is_relative_to(PROJECT/'repo-lqr'):return 'other_expert_worktree_not_read'
 if p.name.lower().startswith(('.env','id_rsa','id_ed25519'))or p.suffix.lower()in('.pem','.key','.kdbx'):return 'credential_path'
 if any(int(x)>=64 for x in ROUND.findall(low)):return 'R64plus_future_excluded'
 if any(x in low for x in ('startup_support_geometry_v1','mod4_deployment_abi_scope_static_v7','takeoff_momentum_capture_method_v1','phase11_pending')):return 'explicit_active_postcut_not_read'
 if re.search(r'startup_stand_v(?:[4-9]|[1-9][0-9])(?:[/_\\\\]|$)',low):return 'future_startup_V4plus_not_read'
 if re.search(r'mod4_deployment_(?:target_compile|abi_scope_static|dependency_static)_v(?:[7-9]|[1-9][0-9])',low):return 'future_target_V7plus_not_read'
 if re.fullmatch(r'run_startup_stand_case_v(?:[6-9]|[1-9][0-9])\\.py',p.name.lower()):return 'future_startup_entry_not_read'
 if p.is_relative_to(WT):
  parts=p.relative_to(WT).parts
  if len(parts)>2 and parts[0]=='history'and parts[1]=='experiments'and parts[2].endswith('_PENDING')and p!=WT/'history/experiments/mod4v1_robust_traditional_phase10_PENDING/ARCHIVE_PHASE9_RECEIPT.json':return 'old_pending_root_not_admitted'
 if p.name.startswith(('~$','.tmp'))or p.suffix.lower()in('.tmp','.temp','.lock'):return 'temporary'
 return None

'''+text[end:];changes.append('replace whole exclusion function with PH10 exclusions')
 change("started=NOW();authority_path=S/'PH9_ARCHIVE_CUTOFF_R63.json';authority=load(authority_path);authority_sha=sh(authority_path.read_bytes());assert authority['status']=='CLOSED_R63_SOURCE_SNAPSHOT_ONLY_NOT_GIT_APPROVAL' and authority['git_commit_tag_push_authorized_by_this_cutoff']is False", "started=NOW();authority_path=S/'ARCHIVE_PHASE10_STARTUP_V3B_TARGET_V6_CUTOFF_FINAL.json';authority=load(authority_path);authority_sha=sh(authority_path.read_bytes());assert authority['status']=='PARENT_ACCEPTS_CLOSED_STARTUP_THROUGH_V3B_AND_TARGET_THROUGH_V6_FOR_SOURCE_PREPARATION_ONLY'")
 change("closed_batches=[(S/x).resolve()for x in authority['actual_closed_batch_dirs']];assert len(closed_batches)==4 and all(p.is_dir()and p.is_relative_to(S/'batches')for p in closed_batches)", """closed_batches=[];wanted=set(authority['physical_registry_required']['controlled_ids'])
 for b in sorted((S/'batches').iterdir()):
  if not b.is_dir()or not b.name.startswith('startup_'):continue
  pr=b/'PROTOCOL.json'
  if not pr.is_file():continue
  names=load(pr).get('case_names',[])
  if set(names)&wanted:
   assert set(names)<=wanted,(b,'unadmitted case in batch');closed_batches.append(b)
 assert len(closed_batches)==4,'Require actual four closed startup protocols'""")
 change("modules=[(S/x).resolve()for x in authority['included_closed_dirs']];root_names={Path(x).name for x in authority['root_files_if_existing']if Path(x).parent==Path('.')}|{authority_path.name}", """modules=[(S/x).resolve()for x in authority['closed_roots_under_task']];assert len(modules)==13
 patterns=('prepare_startup_*.py','run_startup_stand_case_v[1-5].py','launch_startup_*.py','analyze_startup_*saved*.py','derive_startup_v3b_admission.py','CONTINUATION_STARTUP*.md','ARCHIVE_PHASE10_*.json')
 root_names={p.name for pat in patterns for p in S.glob(pat)if p.is_file()and not forbidden(p)}|{authority_path.name}
 new(P/'ROOT_ROUTING_ALLOWLIST.json',{'patterns_for_discovery_only':patterns,'existing_explicit_files':sorted(root_names),'not_existence_or_execution_proof':True,'root_runtime_dependencies_require_actual_provenance_or_prior_SHA':True})""")
 change("if not p.is_relative_to(PROJECT):missing.append({'path':str(p),'reason':'outside_project_not_read','producer':producer,'expected_SHA':expected});return", "if not any(p.is_relative_to(a)for a in (S,WT,PROJECT/'traditional_control_20261101')):missing.append({'path':str(p),'reason':'outside_authorized_project_roots_not_read','producer':producer,'expected_SHA':expected});return")
 change("not_actual_closed_R63_PROTOCOL_case_no_result_sweep", "not_actual_closed_startup_PROTOCOL_case_no_result_sweep")
 oldline=next(x for x in text.splitlines(keepends=True)if "for name in [x for x in authority['root_files_if_existing']" in x);start=text.index(oldline);following=text.index("for b in closed_batches:",start);line_start=text.rfind('\n',0,following)+1;text=text[:start]+" # Additional root/build sources require observed named provenance, not blanket root admission.\n"+text[line_start:];changes.append('remove old report-only allowlist block structurally')
 change("prior_receipt=WT/'history/experiments/mod4v1_robust_traditional_phase9_PENDING/ARCHIVE_PHASE8_RECEIPT.json'", "prior_receipt=Path(authority['previous_postreceipt']).resolve()")
 change("prior_commit='662204600bf79ace36815db569a5d02f3b327981'", "prior_commit='7b7d2633a25dad356809a56ddfa2d546f1cded10'")
 # Bind raw/original-vs-readable textual encodings to their OWN recorded digest; no codec conversion.
 marker=next(x for x in text.splitlines(keepends=True)if 'h=next((obj[k].lower()for k in' in x)
 idx=text.index(marker);indent=marker[:len(marker)-len(marker.lstrip())]
 extra="""    for pathkey,hashkey,byteskey in (('original_path','raw_SHA','raw_bytes'),('readable_path','readable_SHA','readable_bytes'),('original_path','original_SHA','original_bytes'),('readable_path','readable_SHA256','readable_bytes')):
     value=obj.get(pathkey);digest=obj.get(hashkey)
     if isinstance(value,str)and isinstance(digest,str)and HEX.fullmatch(digest):
      target=resolve(value,p)
      if target is not None:
       claims[str(target).lower()].append({'SHA':digest.lower(),'producer':str(p),'location':loc+'.'+hashkey,'producer_bytes':obj.get(byteskey)})
       if context:add(target,'separate_original_or_readable_representation_SHA',digest.lower(),str(p))
"""
 extra='\n'.join(indent+x[4:]for x in extra.splitlines())+'\n'
 text=text[:idx]+extra+text[idx:];changes.append('typed original/readable digest association')
 change("'prior_PH1_to_PH8_saved_SHA'", "'prior_PH1_to_PH9_saved_SHA'")
 change("'expected6_results_4800controls_96000steps_are_sanity_only_not_evidence':True", "'expected4controlled_2101controls42020steps_3passive12000steps_are_sanity_only_not_evidence':True")
 change("'postcut_phase10_pending':True", "'postcut_phase11_pending':True")
 change("'LOCAL_PH9_SOURCE_PREPARED_ONLY_WAIT_PARENT_REVIEW'", "'LOCAL_PH10_SOURCE_PREPARED_ONLY_WAIT_PARENT_REVIEW'")
 # Source collector parse events are preservation data, not archived-program execution.
 ast.parse(text);dest=P/'prepare_source.py';assert not dest.exists();dest.write_text(text,encoding='utf-8')
 print('PH10_NEW_SOURCE_COLLECTOR_AST_OK',hashlib.sha256(raw).hexdigest(),hashlib.sha256(text.encode('utf-8')).hexdigest(),len(changes))
if __name__=='__main__':
 try:main()
 except BaseException:
  n=1
  while(P/f'GENERATOR_FAILURE_{n:03d}.txt').exists():n+=1
  (P/f'GENERATOR_FAILURE_{n:03d}.txt').write_text(traceback.format_exc(),encoding='utf-8');(P/f'GENERATOR_FAILURE_SOURCE_{n:03d}.py').write_bytes(Path(__file__).read_bytes());raise
