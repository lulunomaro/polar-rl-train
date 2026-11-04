"""PH11 finite paths and prior metadata only; original recorder/adapters never imported or executed."""
from pathlib import Path
import json,hashlib,subprocess,os,collections,datetime
D=Path(__file__).resolve().parent;W=D.parents[2];R=Path(r'F:\RMPOLAR-RL\mod4v1_lqr_mpc_robust_20261102');P10=W/'history/experiments/mod4v1_robust_traditional_phase10_SOURCE_PREPARATION'
S=R/'ARCHIVE_PHASE11_V5_FIRST_LINK_V17_CUTOFF_FINAL.json';H='e176d2a6401fafb9d618a042acba8190023c3273';BR='mod4v1-lqr-mpc-robust'
GLOB=Path(r'C:\Users\lulu\AppData\Local\Temp\dsh-spill-N99Hsy\session-de481967f16c\b1f11068aea6-glob-results.txt')
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def save(n,v):
 with(D/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def load(p):return json.loads(p.read_bytes())
def git(label,*args):
 env=dict(os.environ);env['GIT_OPTIONAL_LOCKS']='0';out=D/(label+'.stdout.txt');err=D/(label+'.stderr.txt')
 with(D/'GIT_READONLY_LEDGER.jsonl').open('a',encoding='utf-8')as f:f.write(json.dumps(dict(event='reserved',label=label,argv=['git','-C',str(W),*args],allowed_readonly=True,index_mutations=False))+'\n')
 with out.open('xb')as o,err.open('xb')as e:q=subprocess.run(['git','-C',str(W),*args],stdin=subprocess.DEVNULL,stdout=o,stderr=e,env=env)
 with(D/'GIT_READONLY_LEDGER.jsonl').open('a',encoding='utf-8')as f:f.write(json.dumps(dict(event='returned',label=label,rc=q.returncode,stdout=rec(out),stderr=rec(err)))+'\n')
 assert q.returncode==0,(label,q.returncode);return out.read_bytes()
def main():
 assert not(D/'FILESET_ALLOWLIST.json').exists();scope=load(S)
 top=git('git01_toplevel','rev-parse','--show-toplevel').decode().strip();branch=git('git02_branch','rev-parse','--abbrev-ref','HEAD').decode().strip();head=git('git03_head','rev-parse','HEAD').decode().strip()
 assert top.replace('\\','/').casefold()==str(W).replace('\\','/').casefold()and branch==BR and head==H,'STOP_UNEXPECTED_OWN_PARENT_OR_BRANCH_DRIFT'
 assert len(scope['closed_roots_under_task'])==14 and Path(scope['source_preparation_destination']).resolve()==D
 lines=GLOB.read_text(encoding='utf-8').splitlines();assert len(lines)==len(set(lines))==925
 roots=scope['closed_roots_under_task'];paths=[];missing=[]
 for line in lines:
  rel=Path(line);assert not rel.is_absolute()and rel.parts[0]in roots and 'STARTUP_STAND_V6'not in rel.parts
  p=R/rel;assert p.is_file()and p.resolve().is_relative_to((R/rel.parts[0]).resolve());paths.append(dict(path=str(p),relative=rel.as_posix(),reason='finite14root_HOSTglob'))
 assert set(Path(x['relative']).parts[0]for x in paths)==set(roots)
 for rel in scope['root_file_allowlist']:
  p=R/rel
  if p.is_file():paths.append(dict(path=str(p),relative=rel,reason='FINAL_explicitroot'))
  else:missing.append(dict(path=str(p),reason='exact_declared_root_lookup_missing_no_substitute'))
 for case in scope['new_physical_registry']['ids']:
  for n in ['config.json','SOURCE_MANIFEST.json','result.json','trace.jsonl','physics.jsonl']:paths.append(dict(path=str(R/'results'/case/n),relative='results/'+case+'/'+n,reason='parent_two_closedcase_result_metadata_or_raw_metadataonly'))
  for n in ['PROTOCOL.json',case+'.json',case+'.log','BATCH_RESULT.json']:paths.append(dict(path=str(R/'batches'/case/n),relative='batches/'+case+'/'+n,reason='parent_exact_two_closedbatch_addendum'))
 post=Path(scope['previous_postreceipt']);paths.append(dict(path=str(post),relative='@repo/'+post.relative_to(W).as_posix(),reason='exact_PH10_postreceipt'))
 seen=set();rows=[]
 for x in paths:
  p=Path(x['path']);k=str(p.resolve()).casefold();assert k not in seen;seen.add(k)
  if not p.is_file():missing.append(dict(path=str(p),reason=x['reason']+'_missing'));continue
  assert not p.is_symlink();s=p.stat();x.update(bytes=s.st_size,mtime_ns=s.st_mtime_ns,suffix=p.suffix.lower());rows.append(x)
 record=W/'history/experiments/20261104-mod4v1-robust-traditional-phase10.json';oldrecord=load(record);oldidx=P10/'REVIEW_INDEX.json';manifest=P10/'FINAL_SOURCE_MANIFEST.json';postdata=load(post)
 assert rec(oldidx)['SHA']==postdata['review_index_unchanged_SHA']=='d8c45a30c8b31e2b9cef8f8d0fe09bb58d8f340ef56b8751626a0ec1cdccd0bb'
 assert rec(manifest)['SHA']==oldrecord['source_and_evidence_sha256'][manifest.relative_to(W).as_posix()]=='89c6267fc703e23b04e293898fe3b6a64d3214f7e775ad0f1fffa52ee1c34ee6'
 helper=W/'archive_tools/record_experiment.py';assert rec(helper)['SHA']=='b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e'
 pm=load(manifest);kinds=collections.Counter(x.get('kind','MISSING')for x in pm['entries']);examples={}
 for e in pm['entries']:
  kind=e.get('kind','MISSING')
  if kind not in examples:examples[kind]={k:v for k,v in e.items()if k not in ['producers','expected_SHA','selection_reasons']}
 git('git04_ph10_tree','ls-tree','-r','-l','-z',H,'--',P10.relative_to(W).as_posix())
 refs=['refs/heads/'+BR]+[n for n in postdata['remote_post_push']if n.startswith('refs/tags/')and not n.endswith('^{}')]
 rt=git('git05_ownedrefs','for-each-ref','--format=%(refname) %(objectname) %(*objectname)',*refs).decode('utf-8');observed={}
 for line in rt.splitlines():
  q=line.split();observed[q[0]]=q[1]
  if len(q)==3:observed[q[0]+'^{}']=q[2]
 assert all(observed.get(n)==postdata['remote_post_push'][n]for n in refs)
 for n in refs:
  if n.startswith('refs/tags/'):assert observed.get(n+'^{}')==postdata['remote_post_push'][n+'^{}']
 save('FILESET_ALLOWLIST.json',dict(status='FINITE14ROOT_AND_EXPLICIT_FINAL_PATHS_FROZEN_BEFORE_TEXT_CAPTURE',scope=rec(S),root=str(R),ownrepo=str(W),branch=branch,parent=head,root_glob_source=rec(GLOB),closedroots=roots,root_files_declared=scope['root_file_allowlist'],files=rows,missing_declared=missing,parent_two_cases_batches_addendum=True,ALL_activeV6_excluded=True,ARM_or_model_or_PHY_or_QA_or_helper_or_Gitmutation_calls=0))
 save('PRIOR_CONTEXT_PINS.json',dict(PH10_record=rec(record),PH10_index=rec(oldidx),PH10_manifest=rec(manifest),PH10_postreceipt=rec(post),original_helper_readonly=rec(helper),prior_summary=postdata['source_preparation_historical_summary'],actual_local_owned_refs=observed,remote_not_queried=True,read_only_git_calls=5,old_PH10_preparer_or_adapter_calls=0))
 save('PRIOR_SCHEMA_INSPECTION.json',dict(entry_count=len(pm['entries']),kinds=dict(kinds),examples=examples,version_claims_count=len(pm['source_version_claims_resolved']),prior_refs=pm['prior_references']))
 save('PREPARATION_MINIMUM_INITIAL.json',dict(status='PATH_AND_PARENT_PREFLIGHT_COMPLETE_NO_TEXT_PAYLOAD_CAPTURE_YET',parent=head,branch=branch,source_files=len(rows),bytes_by_extension=dict(collections.Counter(x['suffix']for x in rows)),closedroot_files=925,explicit_root_declared=len(scope['root_file_allowlist']),missing_declared=missing,prior_entries=len(pm['entries']),prior_kinds=dict(kinds),source_snapshot_files=0,raw_payload_opens=0,raw_payload_hashes=0,Git_mutations=0,helper_exec=0,ARM_native_model_PHY_QA_agents_Goal=0,ALL_V6_excluded=True))
 print(json.dumps(dict(status='FINITE_PATH_PREFLIGHT_PASS',files=len(rows),roots=14,explicit_root_declared=len(scope['root_file_allowlist']),missing_declared=missing,extensions=dict(collections.Counter(x['suffix']for x in rows)),prior_kinds=dict(kinds),prior_examples=examples,old_helper_verified_only=True),ensure_ascii=False))
if __name__=='__main__':main()
