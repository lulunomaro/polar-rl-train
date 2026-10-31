from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;G=T.parent/'polar-rl-train';R=N/'reports'
D=G/'versions/20261031_mod4-fudan-jump-original-plane-400n50-dr-two-hour-ppo194/ordinary195_E0_start_source_20261031'
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return dict(line.split()[::-1] for line in s.splitlines() if line.strip())
assert not git('status','--porcelain') and not D.exists()
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert len([k for k in old if not k.endswith('^{}')])==1500 and all(remote.get(k)==v for k,v in old.items())
assert json.loads((R/'ROOT195_E0_START_LITERAL_REWARD_SOURCE_AND_TaskGO_CPU_ACTUAL.json').read_bytes())['passed']
req=json.loads((R/'AUTOMATION195_USER_E0_START_POST194_UPDATE_REQUEST.json').read_bytes())
actual=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert actual['prompt']==req['prompt'].rstrip('\n') and actual['target_thread_id']==req['targetThreadId'] and actual['rrule']==req['rrule'] and actual['status']=='ACTIVE'
with (R/'ARCHIVE195_SOURCE_ONLY_ORDINARY194_ONCE_CONSUMED.json').open('x') as f:json.dump(dict(epoch=time.time(),no195_GPU_or_training_tag=True,old1500_objects_peels_equal=True,source_and_saved_metadata_only=True),f,indent=2)
known={}
for index in (G/'versions').rglob('CAPTURE_INDEX.json'):
 try:v=json.loads(index.read_bytes())
 except (UnicodeDecodeError,json.JSONDecodeError):continue
 for row in v.get('files',[]):
  if row.get('capture')=='full_UTF8_byte_exact' and row.get('SHA') and row.get('Git_path'):known.setdefault(row['SHA'],row['Git_path'])
manifest=json.loads((N/'TRAIN195_COMPLETE_MANIFEST.json').read_bytes());producer={r['local_relative']:r for r in manifest['files']}
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
D.mkdir();rows=[];selected=[]
for p in sorted(N.rglob('*')):
 if not p.is_file() or '__pycache__' in p.parts:continue
 rel=p.relative_to(N).as_posix()
 if p.suffix.lower() in ('.usd','.usda','.npz','.npy','.pt','.pth','.stl','.png','.zip','.gz'):
  r=producer.get(rel,{});rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=r.get('SHA','unknown'),capture='metadata_only_no_content_read_for_Git'));continue
 assert p.suffix in ('.py','.json','.txt','.md','.xml','.sh'),str(p)
 raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
 if sha in known:
  rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,Git_path=known[sha],capture='previous_full_same_SHA_reference'));continue
 try:text=raw.decode('utf8')
 except UnicodeDecodeError:
  dest=D/(rel+'.bytes.b64.txt');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(base64.b64encode(raw).decode('ascii')+'\n',encoding='ascii')
  rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,Git_path=dest.relative_to(G).as_posix(),capture='byte_exact_base64_nonUTF8_source'));selected.append(dest.relative_to(G).as_posix());continue
 assert redact(text)[0]==text,str(p)
 dest=D/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,Git_path=dest.relative_to(G).as_posix(),capture='full_UTF8_byte_exact'));selected.append(dest.relative_to(G).as_posix());known[sha]=dest.relative_to(G).as_posix()
index=D/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),ordinary194_supplement=True,source195_not_deployed=True,files=rows,
 binary_model_or_old_raw_for_Git_reads=0,original_E0_and_active194_untouched=True,actual195_target_admission_CUDA_and_training_pending=True),indent=2),encoding='utf8');selected.append(index.relative_to(G).as_posix())
note=D/'SOURCE_SCOPE_NOTE.md';note.write_text('''Human asked for a small walking adaptation component or E0 as the jump-training start. Root selected the E0 option, preserving literal Fudan JUMP reward instead of inventing a walking mixture. The active194 two-hour window remains unchanged and must fully close/qualify before the separate195 installer can pass its first guards.

Saved E0_82 evidence already has400N/50Hz/D0-D7, actor35/critic38/action6, STD6,17Adam641200, RSL31984 and adaptive LR0.00038443359375000017. Saved20s/20k complete-command forward/reverse BODY velocity MAE0.039424/0.029619 with zero non-timeout terminations is evidence of useful ground behavior, not a universal skill graduation. Reuse actual SHAa92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a/14031973B, without new checkpoint reads for preparation or Git.

195 worker/Task/authority/node/installer/FIRST/normal/CPU readers are frozen. Original19 JUMP methods/config, original measured geometry and all physical payload bytes remain the194 source. Full actor/critic/STD/optimizer/counters/LR are required on actual target restore, with fresh task physics/DR/queue histories explicitly typed. New sourceCPU four groups/18 refusals passed. No source PT/raw/SDK/GPU/remote/GO or optimizer work occurred. Only exact source text and previously saved qualification metadata were read. The new source is not actual target qualification and not a running second learner. Original source31984 is E0, despite legacy DELIVERY31984 schema strings. Original E0 formal remains untouched.

The first future195 window retains original3900/save3600/exit300. Deferred E0 upload1/GPU read1 requires actual completed194 closure, original sole72 authority/resources/TaskGO and actual target0PT/CUDA fullstate receipts. No hotadd, second writer or new budget grant. E0 walking mode0 to original-JUMP mode1/command height domain is a new task, so warm starting does not prove retained walking. After training, separately freeze and evaluate standing/forward/reverse and actual jump/landing behavior. No actual195 training tag until new Pi exists. All new source/CPU/handoff/human choice/same-automation receipts are retained as ordinary194 supplement, no retag.
''',encoding='utf8');selected.append(note.relative_to(G).as_posix())
for i in range(0,len(selected),24):git('add','--',*selected[i:i+24])
git('commit','-m','Prepare user-selected E0 fullstate start for literal Fudan JUMP after194 closes')
git('push','origin','HEAD')
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,ordinary_append=True,no195_GPU_tag=True,protected1500_objects_peels=True,indexed_files=len(rows),clean=True)))
