"""Ordinary capture of the app's one-terminal-LF prompt normalization audit."""
from pathlib import Path
import hashlib,json,subprocess,tomllib,time
N=Path(__file__).resolve().parent;R=N/'reports';W=N.parents[1];G=W/'polar-rl-train'
def H(b):return hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(G),*a],stderr=subprocess.STDOUT).decode().strip()
def main():
 assert git('rev-parse','HEAD')=='1d3d9376f33b278cd3d50eefaef30a2bac948ee1' and not git('status','--porcelain')
 tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags');assert len(tags.splitlines())==1461
 p=R/'CURRENT_CLOSED88C_FULLSTATE_ZERO_STEP_NEXT_FROZEN_DIAGNOSTIC_MONITOR_SOURCE.txt';raw=p.read_bytes();text=raw.decode('utf8')
 a=tomllib.loads(Path(r'C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 assert a['id']=='mod4-10' and a['status']=='ACTIVE' and a['rrule']=='FREQ=HOURLY;INTERVAL=1' and a['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 assert text.endswith('\n') and a['prompt']==text[:-1],'only the app-trimmed final LF accepted; no other prompt difference'
 report=dict(epoch=time.time(),original_local_verifier_assertion_failed=True,original_error='AssertionError at x["prompt"]==source_text exact comparison before the rest of the status assertion',classification='local verification reader assumed terminal LF preserved; app strips exactly one terminal LF',actual_automation_update_succeeded=True,persisted_status=a['status'],persisted_rrule=a['rrule'],target=a['target_thread_id'],source_prompt_path=str(p),source_prompt_SHA=H(raw),persisted_prompt_SHA=H(a['prompt'].encode()),source_length=len(text),actual_length=len(a['prompt']),only_one_terminal_LF_removed=True,no_automation_or_training_action_for_this_audit=True,no_new_Goal_or_automation=True,pending_ordinary_helper_after_freeze=str(N.parent/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native88C_frozen_single_attempt_source_preparation_v1'))
 rp=R/'CLOSED88C_SAME_HOURLY_PROMPT_TERMINAL_LF_LOCAL_READER_FALSE_AND_CORRECTED_ACTUAL.json'
 with rp.open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 D=G/'versions/20261027_mod4-native88-gas400-own-wheel-objective-continuation/ordinary_closed88C_hourly_terminal_LF_reader_audit';D.mkdir()
 files=[];entries=[]
 for path in [Path(__file__).resolve(),rp]:
  b=path.read_bytes();dest=D/'files'/path.relative_to(W);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
  rel=dest.relative_to(G).as_posix();files.append(rel);entries.append(dict(path=str(path),bytes=len(b),SHA=H(b),archive=rel,archive_SHA=H(b),mode='full',original_retained=True))
 index=D/'ORDINARY_CAPTURE_INDEX.json';index.write_text(json.dumps(dict(entries=entries,no_new_trial_or_tag=True,no_model_raw_GPU_or_host_read_for_Git=True),indent=2),encoding='utf8');files.append(index.relative_to(G).as_posix())
 git('add','--',*files);git('commit','-m','Preserve hourly prompt terminal-newline reader correction');git('push','origin','HEAD:main')
 head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==head
 assert git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags')==tags
 for row in entries:assert H(subprocess.check_output(['git','-C',str(G),'show',head+':'+row['archive']]))==row['archive_SHA']
 assert not git('status','--porcelain')
 print(json.dumps(dict(remote_main=head,all1461tag_objects_peels_unchanged=True,fulltext_blobs_verified=True,workingtree_clean=True,no_new_tag=True,helper_explicit_pending_after_freeze=report['pending_ordinary_helper_after_freeze'])))
if __name__=='__main__':main()
