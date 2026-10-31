"""Archive this actual expert-port phase once, without model/raw/host-GPU reads."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib

T=Path(__file__).resolve().parent;W=T.parent;G=W/'polar-rl-train'
B=T/'FROZEN_EXPERTS_400N50_SKILL_SUPERMIMIC_CONTINUATION_V189_20261031';R=B/'reports'
ID='mod4-frozen-experts-400n50-skill-supermimic-teacher-port189'
TAG='trial-20261031-'+ID
V=G/'versions'/('20261031_'+ID)

def git(*args):
    return subprocess.run(['git','-C',str(G),*args],check=True,capture_output=True,text=True,encoding='utf8').stdout.strip()
def parse_refs(text):return dict(line.split()[::-1] for line in text.splitlines() if line.strip())
assert not git('status','--porcelain') and not git('tag','--list','*port189*'), 'Existing phase or unrelated changes; never replay recorder'
before_local=parse_refs(git('show-ref','--tags','-d'))
before_remote=parse_refs(git('ls-remote','--tags','origin'))
assert len([key for key in before_local if not key.endswith('^{}')])==1498
assert all(before_remote.get(key)==value for key,value in before_local.items())

request=json.loads((R/'AUTOMATION189_BACKGROUND_UPDATE_REQUEST.json').read_bytes())
actual=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert actual['id']==request['id'] and actual['kind']=='heartbeat' and actual['status']=='ACTIVE'
assert actual['target_thread_id']==request['targetThreadId'] and actual['rrule']==request['rrule'] and actual['prompt']==request['prompt']
with (R/'AUTOMATION189_PERSISTED_EXACT_BACKGROUND_BINDING_VERIFIED.json').open('x',encoding='utf8') as f:
    json.dump(dict(epoch=time.time(),passed=True,id=actual['id'],kind=actual['kind'],status=actual['status'],
                   original_thread_retained=True,original_hourly_retained=True,prepared_prompt_exact=True,
                   no_new_Goal_or_automation=True),f,indent=2)
with (R/'ARCHIVE189_ONCE_CONSUMED_BEFORE_RECORD.json').open('x',encoding='utf8') as f:
    json.dump(dict(epoch=time.time(),phase=ID,tag=TAG,old_tag_count=1498,
                   old_local_remote_objects_and_peels_equal=True,
                   no_model_raw_binary_or_host_GPU_for_Git=True),f,indent=2)

sys.path.insert(0,str(G/'archive_tools'))
from capture_history import redact
V.mkdir(parents=True,exist_ok=False)
rows=[]
selected=[]
for source in sorted(B.rglob('*')):
    if not source.is_file():continue
    assert source.suffix.lower() in ('.json','.md','.py','.txt'),source
    raw=source.read_bytes();text=raw.decode('utf8')
    assert redact(text)[0]==text, 'Credential redaction required before archive: '+str(source)
    dest=V/source.relative_to(B);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
    rows.append(dict(path=str(source),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),
                     Git_path=dest.relative_to(G).as_posix(),capture='full_UTF8_byte_exact'))
    selected.append(dest.relative_to(G).as_posix())
source=Path(__file__).resolve();raw=source.read_bytes();dest=V/'ROOT_ARCHIVE_DRIVER.py';dest.write_bytes(raw)
rows.append(dict(path=str(source),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),Git_path=dest.relative_to(G).as_posix(),capture='full_UTF8_byte_exact'))
selected.append(dest.relative_to(G).as_posix())
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,
    binary_content_reads_for_Git=0,model_and_raw_only_existing_producer_metadata=True,
    later_unbuilt_E0_SDK_native_training_caller_explicit_pending=True),indent=2),encoding='utf8')
selected.append(index.relative_to(G).as_posix())
note=V/'EXPERIMENT_NOTE.md'
note.write_text('''Human explicitly resumed background completion of old-expert400N50 normalization, full skill acceptance and SuperMimic conversion. The current188 literal Fudan stairs3 PPO stays unchanged.

Saved receipts identify E0/W35/E2/E3 qualified400N50 formals; none is silently relabelled fully graduated. New E0 teacher-to-native supervision component used one declared CPU source checkpoint byte read/decode and72 deterministic scaled-coordinate probes. Seven groups and10 necessary refusal cases passed, with teacher/STD/RNG unchanged, zero optimizer/SDK/GPU/remote work. A separate natural-boundary transition collector passed two groups/seven refusals; actual E0 runtime integration and native training remain pending. Original35 observations are inputs, not guessed from packed127; student raw output supervision retains gradients outside clip6.

New W35 acceptance purpose read its exact original5039-row/2618543B saved cycle JSONL once on86, after fresh72 exact active188 read-only authority and closing72. No raw download/local reopen, model or SDK/GPU call. All SSH finally closed and original SESSION restored. Full1229 cycles/945 unique envs have event MAE0.02172158885234929m/s;1113 within original along0.05m/s and116 outside. Nonterminal1214 cycles/936unique have MAE0.0218204217157411. All15 terminal events/3810partials remain. Full world acceptance remains UNKNOWN because producer lacks cross displacement and commanded signed-yaw error; next new rollout specification requests these exact fields, without adding aggregate success thresholds.

Actual source/CPU/remote small-result/false/refusal/reader-error reports and same-automation update are retained. No new expert GPU learning, no new training grant, no ledger writes or skill graduation claim. Existing raw/model indexes retain real paths/bytes/producer SHA only; no such content was read for Git. The next complete E0 SDK collector/typed native learner caller is explicitly unbuilt and is not deployed by this archive. Original188 normal900 remains scheduled on its original signed window. No previous trial is retagged.
''',encoding='utf8')
selected.append(note.relative_to(G).as_posix())
for row in rows:
    target=G/row['Git_path'];assert target.stat().st_size==row['bytes'] and hashlib.sha256(target.read_bytes()).hexdigest()==row['SHA']
call=[sys.executable,str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title',
      'Resume frozen expert400N50 skill acceptance and E0 SuperMimic teacher port189',
      '--kind','diagnostic','--note-file',str(note),'--validation',
      'Actual E0 CPU7+10 refusals; collector2+7; W35 one-pass1229 cycles,116 along residuals retained; native GPU port pending',
      '--files',*selected,'--push']
p=subprocess.run(call,capture_output=True,text=True,encoding='utf8')
print(p.stdout,end='');print(p.stderr,end='',file=sys.stderr)
if p.returncode:raise SystemExit(p.returncode)
after_local=parse_refs(git('show-ref','--tags','-d'));after_remote=parse_refs(git('ls-remote','--tags','origin'))
assert all(after_local.get(key)==value and after_remote.get(key)==value for key,value in before_local.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG);peel=git('rev-parse','refs/tags/'+TAG+'^{}')
assert peel==head and after_remote['refs/tags/'+TAG]==obj and after_remote['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head
assert not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,
                      tag_count=len([key for key in after_local if not key.endswith('^{}')]),
                      protected_old1498_objects_peels=True,full_UTF8_files=len(rows),
                      same_background_automation_persisted=True,clean=True)))
