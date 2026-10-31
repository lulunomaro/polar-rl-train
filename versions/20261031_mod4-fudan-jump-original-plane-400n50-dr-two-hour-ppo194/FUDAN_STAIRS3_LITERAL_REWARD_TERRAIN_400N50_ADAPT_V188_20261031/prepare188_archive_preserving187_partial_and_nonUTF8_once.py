from pathlib import Path
import ast,json,time
N=Path(__file__).resolve().parent;T=N.parent
old=T/'archive_ACTUAL187_delivered4999_totalplan40050_DR_270_ONCE.py';s=old.read_text(encoding='utf8')
s=s.replace('import hashlib,json,subprocess,sys,time,traceback','import base64,hashlib,json,subprocess,sys,time,traceback')
s=s.replace("N=T/'DELIVERED_JUMP4999_TOTAL_PLAN_400N50_DR_270_CHECK_V187_20261031'","N=T/'FUDAN_STAIRS3_LITERAL_REWARD_TERRAIN_400N50_ADAPT_V188_20261031'")
s=s.replace("ID='mod4-delivered-fudan4999-totalplan400n50-dr-step270-evaluation187'","ID='mod4-fudan-stairs3-literal-reward-terrain-400n50-ppo188'")
s=s.replace("and not git('status','--porcelain=v1') and not D.exists()","and not git('diff','--cached','--name-only') and not D.exists()")
start=s.index(' current=json.loads(');end=s.index(' scope=json.loads(',start)
block=""" current=json.loads((R/'CURRENT_ACTUAL188_LITERAL_STAIRS3_ORIGINAL_REWARD_TERRAIN_400N50_DR_FIRST_PASS_AND_NORMAL_WORK_ORDER.json').read_bytes())
 assert current['first_actual_new_PPO_updates']==1 and current['first_17Adam']==100040
 first=json.loads((R/'ROOT188_FIRSTV2_ACTUAL_NEW_PPO_OR_ORIGINAL_ERROR_RETURNED.json').read_bytes());assert first['passed']
 auto=json.loads((R/'AUTOMATION188_ACTUAL_FIRST_AND_ORIGINAL_NORMAL_UPDATE_RECEIPT.json').read_bytes());assert not auto['tool_receipt'].get('isError',False)
 prior_partial=G/'versions/20261031_mod4-delivered-fudan4999-totalplan400n50-dr-step270-evaluation187'
 allowed='?? '+prior_partial.relative_to(G).as_posix()+'/'
 assert all(line==allowed for line in git('status','--porcelain=v1').splitlines())
 assert not git('tag','--list','trial-20261031-mod4-delivered-fudan4999-totalplan400n50-dr-step270-evaluation187')
"""
s=s[:start]+block+s[end:]
s=s.replace('CAPTURE_ACTUAL187_COMPLETE_SOURCE_ERRORS_AND_EVALUATION_SCOPE.json','CAPTURE_ACTUAL188_FROZEN_COMPLETE_SOURCE_FIRST_AND_PRIOR_ERRORS_SCOPE.json')
s=s.replace("sources.update(Path(p) for p in scope['additional_files']);sources.add(Path(__file__).resolve())", "sources.update(Path(p) for p in scope['additional_files']);sources.add(Path(__file__).resolve())\n sources.update(p for p in prior_partial.rglob('*') if p.is_file())")
s=s.replace('ACTUAL187_RECORD_EXPERIMENT_CONSUMED_BEFORE_GIT.json','ACTUAL188_RECORD_EXPERIMENT_CONSUMED_BEFORE_GIT.json')
s=s.replace('actual_V2_32env_target_evaluation=True,skill_success=False','actual_188_new_PPO_first_update=True,prior_187_all_errors_retained=True,skill_success=False')
start=s.index(' for root in (N,N/');end=s.index(' reuse={}',start)
block=""" for root,manifest_name in [(T/'DELIVERED_JUMP4999_TOTAL_PLAN_400N50_DR_270_CHECK_V187_20261031','FROZEN_EVAL187_COMPLETE_MANIFEST.json'),(T/'DELIVERED_JUMP4999_TOTAL_PLAN_400N50_DR_270_CHECK_V187_20261031/V2_EXISTING_NORMALIZED_CLOCK_AND_FEEDBACK_SOURCE','FROZEN_EVAL187_COMPLETE_MANIFEST.json'),(N,'TRAIN188_COMPLETE_MANIFEST.json')]:
  m=json.loads((root/manifest_name).read_bytes())
  for row in m['files']:
   known[str((root/row['local_relative']).resolve()).casefold()]=dict(bytes=row['bytes'],SHA=row['SHA'])
"""
s=s[:start]+block+s[end:]
s=s.replace("if not row.get('status','').startswith('complete_UTF8')", "if not row.get('status','').startswith(('complete_UTF8','complete_source_'))")
olddecode="  filtered,count=redact(data.decode('utf-8-sig'));archived=filtered.encode('utf8') if count else data\n  row=dict(origin=str(p),original_bytes=len(data),original_SHA=sha,archived_bytes=len(archived),archived_SHA=H(archived),redactions=count,status='complete_UTF8_new_redacted' if count else 'complete_UTF8_new_exact',segments=[])"
newdecode="""  encoding='utf-8-sig'
  try:decoded=data.decode(encoding)
  except UnicodeDecodeError:
   encoding='gb18030'
   try:decoded=data.decode(encoding)
   except UnicodeDecodeError:encoding='latin1';decoded=data.decode(encoding)
  filtered,count=redact(decoded)
  if encoding=='utf-8-sig':
   archived=filtered.encode('utf8') if count else data
   status='complete_UTF8_new_redacted' if count else 'complete_UTF8_new_exact'
  else:
   safe_source=filtered.encode(encoding) if count else data
   envelope=dict(archive_kind='nonUTF8_source_byte_exact_base64_plus_readable_text',encoding_guess=encoding,original_SHA=sha,redactions=count,safe_source_bytes=len(safe_source),safe_source_SHA=H(safe_source),base64_source_bytes=base64.b64encode(safe_source).decode('ascii'),readable_source=filtered,original_secret_bytes_not_included_if_redacted=bool(count))
   archived=json.dumps(envelope,ensure_ascii=False,indent=2).encode('utf8');status='complete_source_nonUTF8_base64_new'
  row=dict(origin=str(p),original_bytes=len(data),original_SHA=sha,archived_bytes=len(archived),archived_SHA=H(archived),redactions=count,original_encoding=encoding,status=status,segments=[])
"""
assert olddecode in s;s=s.replace(olddecode,newdecode)
s=s.replace("new_learning=False,actual32env_target400N50D0_D7_evaluation=True,skill270success=False", "new_learning=True,actual20k_env_first_PPO_update_and64env_admission=True,old187_32env_target_eval_also_captured=True,skill270success=False")
s=s.replace("external_selected_model_metadata=model,", "external_selected_model_metadata=model,external188_first_model_metadata=scope['existing_remote_model_metadata'],")
s=s.replace('ACTUAL187_FINAL_EXPERIMENT_NOTE.md','ACTUAL188_FINAL_EXPERIMENT_NOTE.md')
s=s.replace("selected=sorted(p.relative_to(G).as_posix() for p in D.rglob('*') if p.is_file());expected=", "selected=sorted({p.relative_to(G).as_posix() for root in (D,prior_partial) for p in root.rglob('*') if p.is_file()});expected=")
s=s.replace("row['status'].startswith('complete_UTF8')", "row['status'].startswith(('complete_UTF8','complete_source_'))")
s=s.replace("'Evaluate delivered Fudan4999 under total-plan400N50 DR and genuine270mm goal187'", "'Train MOD4 with literal Fudan STAIRS3 reward and terrain at400N50 DR188'")
s=s.replace("'--kind','evaluation'", "'--kind','training'")
s=s.replace("'Exact delivered4999 CPU185 and literal GPU187;32 first episodes,1000controls8000callbacks,400N50Hz/D0-D7/TGS32/4,2mm retained;0same-flight270cross/landing/stable successes. V1pre-model clock failure and V2existing-clock repair/fullUTF8 retained. No training/ledgerwrites.'", "'Actual20k-env PPO FIRST1,480000own transitions,17Adam100020to100040,full18137745B save; exact31 originalSTAIRS3 method texts/16weights,original200tile stairs,400N50D0-D7/TGS32/4/2mm. SourceCPU6groups and64env0PT native8 passed. Sole72 original3900/3600/300 writer. No270skill claim. All183-188errors/source/UTF8 and nonUTF8 exact-byte envelopes retained.'")
s=s.replace('ACTUAL187_ARCHIVE_ORIGINAL_ERROR_','ACTUAL188_ARCHIVE_ORIGINAL_ERROR_')
s=s.replace("binary_metadata_only=sum", "nonUTF8_source_envelopes=sum(x['status'].startswith('complete_source_') for x in rows),binary_metadata_only=sum")
ast.parse(s);out=T/'archive_ACTUAL188_literal_STAIRS3_40050_FIRST_all_pending_ONCE.py'
with out.open('x',encoding='utf8') as f:f.write(s)
with (N/'reports/ROOT188_PRIOR187_ARCHIVE_NONUTF8_FAILURE_BEFORE_RECORD_REPAIR_SCOPE.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),old187_archive='archive_ACTUAL187_delivered4999_totalplan40050_DR_270_ONCE.py',original_error="UnicodeDecodeError UTF8 byte0xb4 at1068 while capturing original nonUTF8 text source",record_experiment187_was_not_called=True,old187_partial_packs_preserved=True,new_actual188_archive=str(out),repair='NonUTF8 source bytes retained as credential-scanned base64 envelope plus readable decoding and separate original/archiveSHA. No experiment/model/raw/host rerun.',new_tag_only_after_actual188PPO=True),f,indent=2)
print(json.dumps(dict(new_archive=str(out),original187_not_rerun=True,preserves_nonUTF8_source_bytes=True)))
