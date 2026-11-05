"""Continue SAME precommit prepared snapshot after original redactor stopped; no source/model replay."""
from pathlib import Path
import sys,json,hashlib,subprocess,time
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel=Path('history/experiments/e3_fudan_resume55_low80_holdout_20261105');dest=repo/rel;trial='e3-fudan-resume55-low80-holdout-closed';tag='trial-20261105-'+trial

def G(*args):
 p=subprocess.run(['git','-C',str(repo),*args],text=True,capture_output=True,encoding='utf8')
 if p.returncode:print(p.stdout);print(p.stderr,file=sys.stderr);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and G('rev-parse','HEAD')=='af7639f66ed2677c905318c2cd79e102e06a35a4'and not G('diff','--cached','--name-only')and not G('tag','--list',tag)
assert G('status','--porcelain').splitlines()==['?? '+rel.as_posix()+'/']and not(repo/'history/experiments'/('20261105-'+trial+'.json')).exists()
sys.path.insert(0,str(repo/'archive_tools'));import record_experiment
from capture_history import redact
index_path=dest/'INDEX.json';index=json.loads(index_path.read_bytes());rows=index['rows']
for name in('FDN_RESUME55_HOLDOUT_ARCHIVE_REDACTION_PREFLIGHT_FAILURE.md',Path(__file__).name):
 source=D/name;raw=source.read_bytes();target=dest/'files'/name;assert not target.exists();target.write_bytes(raw);rows.append(dict(source_path=str(source),status='complete_text_point_in_time',bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest(),archive_path=target.relative_to(repo).as_posix()))
changed=[]
for row in rows:
 if 'archive_path'not in row:continue
 target=repo/row['archive_path'];raw=target.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['SHA256']
 text=raw.decode('utf8');filtered,count=redact(text)
 if filtered!=text:
  out=filtered.encode('utf8');target.write_bytes(out);row.update(status='redacted_text_original_preserved_workspace',original_bytes=len(raw),original_SHA256=row['SHA256'],archive_bytes=len(out),archive_SHA256=hashlib.sha256(out).hexdigest(),redactions=count,reason='Original recorder redactor applied to archive copy only; no matched values emitted; source preserved');changed.append(dict(path=row['archive_path'],redactions=count,original_SHA256=row['SHA256'],archive_SHA256=row['archive_SHA256']))
 assert redact(target.read_text(encoding='utf8'))[0]==target.read_text(encoding='utf8')
assert changed
index['archive_copy_redaction_continuation']=dict(original_validator_unchanged=True,changed=changed,record_was_not_previously_written=True,no_old_entrypoint_model_or_physics_replay=True);index_path.write_text(json.dumps(index,indent=2),encoding='utf8')
note=dest/'NOTE.md';text=note.read_text(encoding='utf8');note.write_text(text+'\n\n## Same prepared archive precommit continuation\nOriginal recorder stopped before metadata/staging/commit on archive-copy source placeholder detection. Original capture_history.redact now applied to archive copies; original/source SHA and archive SHA/count/reason indexed, no matched values emitted and workspace originals untouched. All original validation/redaction/hash checks retained; same unique trial, no physics/model/old record-source replay. Failure and continuation included.\n',encoding='utf8')
files=[row['archive_path']for row in rows if 'archive_path'in row]+[(rel/name).as_posix()for name in('INDEX.json','.gitattributes','NOTE.md')];assert len(files)==len(set(files))
a=json.loads((D/'FDN_RESUME55_LOW80_HOLDOUT_ANALYSIS_V1.json').read_bytes());ag=a['aggregate'];assert a['execution_qualified']is True and ag['denominator']==240 and a['source_IO_group_actual']==3 and a['optimizer_updates']==0 and a['goal_complete']is False
original_git=record_experiment.git

def scoped_git(*args):
 if args[:2]==('add','--'):
  rp=args[2];assert rp=='history/experiments/20261105-'+trial+'.json'and set(args[3:])==set(files);answer=original_git('add','--',rel.as_posix(),rp);assert set(original_git('diff','--cached','--name-only').splitlines())==set(files)|{rp};return answer
 return original_git(*args)

record_experiment.git=scoped_git
sys.argv=['record_experiment.py','--id',trial,'--title',f'E3 frozen8e27 native holdout firstcredit={ag["first_episode_continuous25_credit"]}of240 strictTerminal25={ag["strict_terminal_continuous25_good_count"]}of240; Registry fixed','--kind','evaluation','--note-file',str(note),'--validation','actualRoot8-three-fresh-seeds20261002-03-04-N80-five16-400ctrl-fullD0D7;strict-current-terminal-streak-separate-loose;wholeN20000CPU-one-physicalhashdecode-percase-group3-zerooptimizer;originalprivateEX-finiteEX-resource-reserve-SDKclose-actual-innerouterwait-release;firstzero-start-and-release-newpurpose-preserved;original74-and-mothers-fixed;original-recorder-validation-redaction-hashes-unchanged-archivecopy-redaction-indexed-shortexact-stagedset;feature-only-mainreadonly-no-modelraw-or-physics-replay','--files',*files]
record_experiment.main();head=G('rev-parse','HEAD');obj=G('rev-parse','refs/tags/'+tag);assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())};assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,source_entries=len(rows),archive_copies_redacted=len(changed),original_recorder_validation_redaction_hashes_retained=True,staged_set_verified=True,physical_model_or_old_record_entrypoint_replay=False,main_push_or_reset=False),indent=2))
