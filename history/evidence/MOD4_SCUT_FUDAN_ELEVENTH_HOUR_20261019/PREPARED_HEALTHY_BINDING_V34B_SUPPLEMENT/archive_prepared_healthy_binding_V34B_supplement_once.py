"""Ordinary supplement to the already-recorded eleventh-hour stage, no new trial tag."""
from pathlib import Path
import hashlib,json,subprocess,time,tomllib,sys
B=Path(__file__).resolve().parent;R=B/'reports';REPO=B.parent/'polar-rl-train';BASE='7b536f8eb347f501a1a83c9a07ccde7094f1de35';DEST=REPO/'history/evidence'/B.name/'PREPARED_HEALTHY_BINDING_V34B_SUPPLEMENT'
H=lambda data:hashlib.sha256(data).hexdigest()
def git(*args):
 p=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
assert git('rev-parse','HEAD')==BASE and not git('status','--porcelain') and not DEST.exists()
args=json.loads((B/'AUTOMATION_PREPARED_HEALTHY_BINDING_V34B_ARGS.json').read_bytes());actual=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
for name in ('name','kind','prompt','status','rrule'):assert args[name]==actual[name]
assert args['targetThreadId']==actual['target_thread_id'] and actual['status']=='ACTIVE'
with (R/'AUTOMATION_V34B_ACTUAL_READBACK_CPU.json').open('x',encoding='utf8') as stream:json.dump(dict(epoch=time.time(),actual_name_kind_prompt_status_rrule_target_exact=True,actual_training_still_two_GO_H1_preGO_failure=True,new_template_binding_only_prepared=True),stream,indent=2)
prior=json.loads((REPO/'history/evidence'/B.name/'REPORT_CAPTURE_INDEX.json').read_bytes())['entries'];known={x['source_SHA']:dict(Git_path=x['Git_path'],archived_SHA=x['archived_SHA']) for x in prior if x.get('source_SHA') and x.get('Git_path') and x.get('archived_SHA')}
paths=[B/'prepare_healthy_H1_runtime_binding_repair_templates_V2_CPU_once.py',R/'PREPARED_H1_HEALTHY_RUNTIME_BINDING_MISMATCH_AND_V2_CPU_ACTUAL.json',B/'prepare_current_monitor_healthy_binding_V34B_once.py',B/'AUTOMATION_PREPARED_HEALTHY_BINDING_V34B_ARGS.json',R/'AUTOMATION_V34B_PREPARED_HEALTHY_BINDING_APP_RECEIPT.json',R/'AUTOMATION_V34B_ACTUAL_READBACK_CPU.json',*sorted((B/'future_partial_hour_repair_templates_V2').glob('*.py')),Path(__file__).resolve()]
note=B/'PREPARED_HEALTHY_BINDING_V34B_SUPPLEMENT_NOTE_UTF8.txt';assert not note.exists();note.write_text('Prepared-only CPU review found that retained H1 hour10 source must normalize against the actual healthy hour10 runtime worker bindings, rather than the failed hour11 admission payload. Old unused templates and the mismatch are preserved; separate V2 templates use the healthy runtime reference. Actual CPU AST regression passed. No remote/GPU/Task/native/PT or accounting action; current original owner318576 continues E2/E3. Existing hourly monitor now references the corrected unused V2 templates.\n','utf8');paths.append(note)
old={}
for line in git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
 p=line.split();old[p[0]]=p[1:]
assert len(old)==1399;DEST.mkdir(parents=True);sys.path.insert(0,str(REPO/'archive_tools'));from capture_history import redact
entries=[];files=[]
for path in paths:
 raw=path.read_bytes();sha=H(raw)
 if sha in known:entries.append(dict(source_path=str(path),bytes=len(raw),source_SHA=sha,capture='existing_complete_Git_SHA_reference',**known[sha],original_retained=True));continue
 clean,n=redact(raw.decode('utf8'));data=clean.encode('utf8') if n else raw;assert len(data)<49_000_000;q=DEST/path.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data);rel=q.relative_to(REPO).as_posix();files.append(rel);entries.append(dict(source_path=str(path),bytes=len(raw),source_SHA=sha,Git_path=rel,archived_SHA=H(data),capture='complete_credential_redacted' if n else 'complete_exact_bytes',redactions=n,original_retained=True))
for name,value in [('REPORT_CAPTURE_INDEX.json',dict(epoch=time.time(),supplement_of_stage_commit=BASE,entries=entries,deferred=[])),('PREEXISTING_TAG_OBJECTS_AND_PEELS.json',old)]:
 q=DEST/name;q.write_text(json.dumps(value,indent=2),'utf8');files.append(q.relative_to(REPO).as_posix())
git('add','--',*files);git('commit','-F',str(note));git('push','origin','HEAD:main');head=git('rev-parse','HEAD');remote={p[1]:p[0] for line in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines() if (p:=line.split())};assert remote['refs/heads/main']==head
for ref,objects in old.items():
 assert remote[ref]==objects[0]
 if len(objects)>1:assert remote[ref+'^{}']==objects[1]
assert not git('status','--porcelain') and len(git('tag','--list').splitlines())==1399
for row in entries:
 raw=subprocess.run(['git','-C',str(REPO),'show',head+':'+row['Git_path']],capture_output=True,check=True).stdout;assert H(raw)==row['archived_SHA']
print(json.dumps(dict(status='REMOTE_VERIFIED_ORDINARY_SUPPLEMENT',commit=head,no_new_trial_tag=True,total_tags=1399,all1399tag_objects_peels_unchanged=True,text_entries=len(entries),deferred=[])))
