"""Finish the existing precommit record after WinError206; never call record again."""
from pathlib import Path
import json,hashlib,subprocess,sys
D=Path(__file__).resolve().parent;repo=D.parent/'repo-lqr';rel='history/experiments/e3_fudan_n20000_timeout8_native_fullresume_20261104';dest=repo/rel;rr='history/experiments/20261104-e3-fudan-n20000-timeout8-real-fullresume-native.json';rp=repo/rr

def G(*a):
 p=subprocess.run(['git','-C',str(repo),*a],capture_output=True,text=True,encoding='utf8')
 if p.returncode:
  print(p.stdout,flush=True);print(p.stderr,file=sys.stderr,flush=True);p.check_returncode()
 return p.stdout.strip()

assert G('branch','--show-current')=='mod4v1-experts-fulldr-rm70'and G('rev-parse','HEAD')=='21763dd0c4ca97cb009913c1075caa6ca09160e6'
assert not G('diff','--cached','--name-only')
record=json.loads(rp.read_bytes());tag=record['tag'];assert tag=='trial-20261104-e3-fudan-n20000-timeout8-real-fullresume-native'and not G('tag','--list',tag)
assert all(line.startswith('?? ')and line[3:]in(rr,rel+'/')for line in G('status','--porcelain','--untracked-files=normal').splitlines())
index=dest/'INDEX.json';iv=json.loads(index.read_bytes())
for name in('FDN_TIMEOUT8_ARCHIVE_PRECOMMIT_WINDOWS_ARGV_FAILURE.md',Path(__file__).name):
 source=D/name;raw=source.read_bytes();target=dest/'files'/name;assert not target.exists();target.write_bytes(raw);ar=target.relative_to(repo).as_posix();digest=hashlib.sha256(raw).hexdigest();record['source_and_evidence_sha256'][ar]=digest
 iv['rows'].append(dict(source_path=str(source),status='complete_text_precommit_failure_and_same_record_continuation',bytes=len(raw),SHA256=digest,archive_path=ar))
iv['precommit_git_add_WinError206_preserved']=True;iv['same_prepared_record_continuation_no_record_replay']=True
index.write_text(json.dumps(iv,indent=2),encoding='utf8');record['source_and_evidence_sha256'][index.relative_to(repo).as_posix()]=hashlib.sha256(index.read_bytes()).hexdigest()
append='\n\nPrecommit archive failure: original record_experiment git add exceeded Windows argv limit (WinError206) before commit/tag. Continue exactly this already-created experiment record using two scoped pathspecs; no record, native, model or raw replay.'
record['repair_or_experiment_note']+=append;record['validation']+=';precommit-WinError206-preserved-same-record-short-directory-pathspec-continuation'
rp.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# The existing recorder already validated every original text file before its add call.
# Stage only this exact prepared snapshot and its exact unique experiment metadata.
G('add','--',rel,rr)
actual=set(G('diff','--cached','--name-only').splitlines());expected=set(record['source_and_evidence_sha256'])|{rr};assert actual==expected,(len(actual),len(expected),actual-expected,expected-actual)
G('commit','-m',record['title']+'\n\nExperiment: '+tag+'\nValidation: '+record['validation'])
head=G('rev-parse','HEAD');G('tag','-a',tag,'-m',record['title']+'\n\n'+record['repair_or_experiment_note']);obj=G('rev-parse','refs/tags/'+tag)
assert G('cat-file','-t','refs/tags/'+tag)=='tag'and G('rev-parse','refs/tags/'+tag+'^{}')==head
G('push','--atomic','origin','HEAD:refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag+':refs/tags/'+tag)
remote={ref:sha for sha,ref in(line.split()for line in G('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+tag,'refs/tags/'+tag+'^{}','refs/heads/main').splitlines())}
assert remote['refs/heads/mod4v1-experts-fulldr-rm70']==head and remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']==head and not G('status','--porcelain')
print(json.dumps(dict(commit=head,tag=tag,annotated_tag_object=obj,remote=remote,staged_paths_verified=len(expected),same_prepared_record_continued=True,record_or_physical_replay=False,main_push_or_reset=False),indent=2))
