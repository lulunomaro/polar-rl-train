"""Ordinary supplement only: future70 source/metadata fixtures and saved-text68 baseline."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;G=W/'polar-rl-train';R=D/'reports'
N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V4_RESOURCE_V70_20261025'
def git(*args):
 p=subprocess.run(['git','-C',str(G),*args],capture_output=True);assert p.returncode==0,p.stderr.decode('utf8','replace');return p.stdout.decode('utf8').strip()
assert git('rev-parse','HEAD')=='08a676828d8cd668b351f32ec8c9995adff4657c' and not git('status','--porcelain')
tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(tags.splitlines())==1441
assert not any((N/x).exists() for x in ('payloads','controllers','current_pair_closed_models'))
mon=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert mon['prompt']==(R/'CURRENT69D_WITH_SOURCE70_AND_BASELINE_MONITOR_SOURCE_ACTUAL.txt').read_text('utf8') and mon['status']=='ACTIVE' and mon['rrule']=='FREQ=HOURLY;INTERVAL=1' and mon['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
sources=[N/'same_optimized_source_contract_metadata_candidate_v1.py',N/'prepare70_source_only_metadata_candidate_CPU_once.py',N/'SOURCE_ONLY_CONTINUATION_CONFIG.json',N/'reports/SOURCE_ONLY70_METADATA_AND_INVENTORY_CANDIDATE_CPU_ACTUAL.json',D/'closed_window_throughput_text_cpu_reader_v1.py',D/'read_closed68_saved_text_throughput_baseline_once.py',R/'CLOSED68_SAVED_LOG_FP32_THROUGHPUT_BASELINE_CPU_ACTUAL.json',R/'CURRENT69D_WITH_SOURCE70_AND_BASELINE_MONITOR_SOURCE_ACTUAL.txt',Path(__file__)]
target=G/'versions/20261025_mod4-step270-closed68-handoff-combined69-forwarded-control/ordinary_source70_metadata_closed68_log_baseline';target.mkdir()
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
entries=[];saved=[]
for p in sources:
 raw=p.read_bytes();clean,n=redact(raw.decode('utf8'));data=clean.encode();dest=target/p.name
 with dest.open('xb') as f:f.write(data)
 saved.append(dest);entries.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),archive=dest.relative_to(G).as_posix(),archive_SHA=hashlib.sha256(data).hexdigest(),redaction_count=n,original_retained=True))
index=target/'ORDINARY_CAPTURE_INDEX.json'
with index.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),kind='ordinary_source_only70_metadata_and_existing_saved_log68_baseline_no_new_trial',entries=entries,synthetic70_tests_not_source_or_installed_admission=True,no_payload_Task_GO_or_training_fee=True,no_remote_GPU_model_or_raw_read=True,monitor_same_ACTIVE_hourly_target=True),f,ensure_ascii=False,indent=2)
saved.append(index);git('add','--',*[p.relative_to(G).as_posix() for p in saved]);git('commit','-m','Prepare source-only70 metadata contracts and closed68 saved-log throughput baseline');git('push','origin','HEAD:main')
head=git('rev-parse','HEAD');remote={x.split()[1]:x.split()[0] for x in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()};assert remote['refs/heads/main']==head
for line in tags.splitlines():
 x=line.split();assert remote[x[0]]==x[1]
 if len(x)>2:assert remote[x[0]+'^{}']==x[2]
for p in saved:assert subprocess.check_output(['git','-C',str(G),'show',head+':'+p.relative_to(G).as_posix()])==p.read_bytes()
assert not git('status','--porcelain')
print(json.dumps(dict(remote_main=head,ordinary_text_entries=len(entries),all1441_tag_objects_and_peels_unchanged=True,new_trial_or_tag=False,all_committed_blobs_verified=True,workingtree_clean=True)))
