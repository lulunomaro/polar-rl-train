"""One ordinary supplement, no new trial/tag; retain original CRLF reader error."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
Q=Path(__file__).resolve().parent;T=Q.parent;G=T.parent/'polar-rl-train';R=Q/'reports'
source=R/'POST_ARCHIVE_IMMUTABLE_TRIAL_MONITOR_SOURCE_ACTUAL.txt'
prompt=source.read_text('utf8');a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert a['prompt']==prompt and a['status']=='ACTIVE' and a['rrule']=='FREQ=HOURLY;INTERVAL=1' and a['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
def git(*args):
 p=subprocess.run(['git','-C',str(G),*args],capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode().strip()
assert git('rev-parse','HEAD')=='522e2e1834c4f1cddd4ed9ef210fa86da060ea16' and not git('status','--porcelain')
tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(tags.splitlines())==1440
D=G/'versions/20261025_mod4-single4090-quantized-wan5b-preparation/ordinary_immutable_trial_monitor_supplement';D.mkdir()
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
entries=[];saved=[]
for p in [source,R/'POST_ARCHIVE_MONITOR_ORIGINAL_CRLF_BYTE_READER_ERROR_ACTUAL.json',Path(__file__)]:
 raw=p.read_bytes();clean,n=redact(raw.decode('utf8'));data=clean.encode();target=D/p.name;target.write_bytes(data);saved.append(target)
 entries.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),archive=target.relative_to(G).as_posix(),archive_SHA=hashlib.sha256(data).hexdigest(),redaction_count=n,original_retained=True))
index=D/'ORDINARY_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),kind='ordinary_monitor_source_and_CRLF_reader_error_supplement_no_new_trial_tag',immutable_quantized_trial_commit='522e2e1834c4f1cddd4ed9ef210fa86da060ea16',actual_automation_full_prompt_string_and_original_status_hourly_target_match=True,actual_prompt_LF_SHA=hashlib.sha256(prompt.encode()).hexdigest(),Windows_source_raw_CRLF_retained=True,entries=entries,no_model_PT_raw_hash_or_host_query_for_Git=True),ensure_ascii=False,indent=2),encoding='utf8');saved.append(index)
git('add','--',*[p.relative_to(G).as_posix() for p in saved]);git('commit','-m','Record immutable quantized trial monitor and original CRLF reader correction');git('push','origin','HEAD:main')
head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head
for line in tags.splitlines():
 b=line.split();assert remote[b[0]]==b[1]
 if len(b)>2:assert remote[b[0]+'^{}']==b[2]
for p in saved:assert subprocess.check_output(['git','-C',str(G),'show',head+':'+p.relative_to(G).as_posix()])==p.read_bytes()
assert not git('status','--porcelain')
print(json.dumps(dict(remote_main=head,total_tags=1440,all_tag_objects_and_peels_unchanged=True,ordinary_monitor_files_committed=len(saved),exact_original_monitor_string_and_schedule_preserved=True,original_CRLF_reader_failure_preserved=True,no_new_trial_record_or_tag=True,workingtree_clean=True)))
