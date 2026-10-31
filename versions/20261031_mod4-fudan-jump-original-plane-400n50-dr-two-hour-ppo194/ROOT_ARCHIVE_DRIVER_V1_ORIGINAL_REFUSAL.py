"""Actual194 learning plus closed188/191/193 evidence. No model/raw/media reads."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
T=Path(__file__).resolve().parent;W=T.parent;G=W/'polar-rl-train'
N=T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031';R=N/'reports'
ID='mod4-fudan-jump-original-plane-400n50-dr-two-hour-ppo194';TAG='trial-20261031-'+ID
V=G/'versions'/('20261031_'+ID)
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return dict(line.split()[::-1] for line in s.splitlines() if line.strip())
assert not git('status','--porcelain') and not git('tag','--list','*ppo194*')
first=json.loads((R/'ROOT194_FIRSTV2_ACTUAL_NEW_PPO_OR_ORIGINAL_ERROR_RETURNED.json').read_bytes())
assert first['passed'] and first['first']['actual_new_PPO_updates']==1
assert json.loads((R/'ROOT194_FIRSTV2_ALL_SSH_CLOSED_SESSION_RESTORED_LEASE_FREE.json').read_bytes())['global_serial_control_lease']=='FREE'
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert len([k for k in old if not k.endswith('^{}')])==1499 and all(remote.get(k)==v for k,v in old.items())
req=json.loads((R/'AUTOMATION194_TWO_HOUR_ACTUAL_UPDATE_REQUEST.json').read_bytes())
actual=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert actual['id']=='mod4-10' and actual['kind']=='heartbeat' and actual['status']=='ACTIVE'
assert actual['prompt']==req['prompt'] and actual['rrule']==req['rrule'] and actual['target_thread_id']==req['targetThreadId']
with (R/'AUTOMATION194_PERSISTED_EXACT_BINDING_VERIFIED.json').open('x') as f:json.dump(dict(epoch=time.time(),passed=True,same_hourly_same_original_thread=True,no_new_Goal_or_automation=True),f,indent=2)
with (R/'ARCHIVE194_ONCE_CONSUMED_BEFORE_RECORD.json').open('x') as f:json.dump(dict(epoch=time.time(),ID=ID,TAG=TAG,protected_old_tags=1499,no_model_raw_host_GPU_for_Git=True),f,indent=2)
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for index in (G/'versions').glob('*/CAPTURE_INDEX.json'):
 try:v=json.loads(index.read_bytes())
 except (UnicodeDecodeError,json.JSONDecodeError):continue
 for row in v.get('files',[]):
  sha=row.get('SHA') or row.get('sha256');gp=row.get('Git_path') or row.get('git_path')
  if sha and gp and row.get('capture')=='full_UTF8_byte_exact':known.setdefault(sha,gp)
V.mkdir(parents=True,exist_ok=False);rows=[];selected=[]
roots=[N,T/'FUDAN_STAIRS3_LITERAL_REWARD_TERRAIN_400N50_ADAPT_V188_20261031',T/'STAIRS188_QUALIFIED_FORMAL_TRUE270_ACCEPTANCE_V191_20261031',T/'STAIRS188_ORIGINAL_COURSE_USER_MUJOCO_V193_20261031']
binary_suffixes={'.pt','.pth','.onnx','.npz','.npy','.usd','.usda','.usdc','.stl','.zip','.gz','.png','.jpg','.jpeg','.mp4','.avi','.mat','.slx','.jsonl','.bin','.pyc','.pyd','.dll'}
for root in roots:
 for source in sorted(root.rglob('*')):
  if not source.is_file() or '__pycache__' in source.parts:continue
  rel=source.relative_to(root)
  if source.suffix.lower() in binary_suffixes:
   rows.append(dict(path=str(source),bytes=source.stat().st_size,SHA='unknown here; use associated existing producer receipt',capture='metadata_only_no_content_read_for_Git'))
   continue
  if source.suffix.lower() not in {'.py','.json','.txt','.md','.log','.xml','.yaml','.yml','.toml','.sh','.ps1'}:
   rows.append(dict(path=str(source),bytes=source.stat().st_size,SHA='unknown',capture='unclassified_external_metadata_only'));continue
  raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if sha in known:
   rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=known[sha],capture='previous_full_same_SHA_reference'));continue
  try:text=raw.decode('utf8')
  except UnicodeDecodeError:
   dest=V/root.name/(rel.as_posix()+'.bytes.b64.txt');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(base64.b64encode(raw).decode('ascii')+'\n',encoding='ascii')
   rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=dest.relative_to(G).as_posix(),capture='byte_exact_base64_nonUTF8_source',decode='Base64 decode ASCII text excluding trailing newline to recover original bytes'));selected.append(dest.relative_to(G).as_posix());continue
  assert redact(text)[0]==text,'Credential redaction required '+str(source)
  dest=V/root.name/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
  rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=dest.relative_to(G).as_posix(),capture='full_UTF8_byte_exact'));selected.append(dest.relative_to(G).as_posix());known[sha]=dest.relative_to(G).as_posix()
source=Path(__file__).resolve();dest=V/'ROOT_ARCHIVE_DRIVER.py';dest.write_bytes(source.read_bytes());selected.append(dest.relative_to(G).as_posix())
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,binary_content_reads_for_Git=0,
 explicit_pending_excluded=[dict(path=str(T/'EXPERTS_RM70_SUPERMIMIC_READY_QUEUE_V190_20261031'),status='Unfrozen incomplete WM50-only source; no learner/GO yet'),dict(scope='current193 GUI future console/exit and194 future normal/formal/fees',status='Later ordinary append, never retag194')]),indent=2),encoding='utf8');selected.append(index.relative_to(G).as_posix())
note=V/'EXPERIMENT_NOTE.md';note.write_text('''Human redirected the main task to two hours of flat-ground jumping adaptation with the unmodified pinned Fudan JUMP reward, approved MOD4 nominal400N/50Hz/D0-D7. Retain the other AI delivered4999 actor35/critic38/learned STD6 and all17 Adam states. This is not a continuation of STAIRS3, native SuperMimic, MATLAB or LQR. User explicitly repeated not to invent reward adaptations.

The19 extracted method texts and entire original reward config are byte-identical to commit8204e853dfd2ed06d85a322e1a998c3d20a3be2c jump source. Five new source-CPU groups passed, including50Hz literal dt/clipping/stateful comparisons, original flight memory retention across resets, own hip-axis geometry and RNG preservation. Eighteen TaskGO/controller negative cases passed. Actual target0PT64env eight controls/64physics16feedback/original reward calls passed with waitedRC0/Appclosed/privateEXfree. The runtime maps actual MOD4 body/contact/motor measurements outside the unchanged reward source; no claim that foreign dynamics, actor architecture or physical termination conditions are identical. Original JUMP plane, commands20s vx+-2.1/yaw+-2/height.12..15 and collision-equivalent named nonwheel forces are explicit. No extra jumping bonus, weight change, force/state injection or relaxed MOD4guard. No local neuralCUDA.

Actual new194 on the original forwarded4090 restored full state before control and produced its first new PPO update,480000 own transitions,17Adam100020 to100040,iteration5000 and a complete new checkpoint. The user-authorized two-hour save deadline is7200s plus300s exit; source cap readiness alone changed to7500s without increasing canonical budget. Original sole72 two fcntls/HMAC and elapsed fee arithmetic remain literal, no other writer or refund. FIRST is a snapshot; not final, continued liveness or jumping skill. All root finite SSH finally closed and SESSION restored.

Also preserve ordinary closed188 supplements and new191/193 evaluations. Closed188 made66updates to5065/Adam101340,31680000transitions, with qualified full-state formal and rawfee3671.391360282898 once. Its 32first-episode270mm acceptance had zero continuous-flight crossings/top landings/stable success. The largest common wheel-bottom height.2705730199813843m ended by closure and did not cross. Original191V1 Kit-root refusal occurred before App/model; newV2 fixed only its namespace and completed with all owned processes out. New193 user-requested original-STAIRS3 view captured273controls/2184physics5.46s ending bad_orientation, no other physical term. GUIV1 parse error before artifact read is retained; newV2 used one admitted pose/terrain read and showed true277 meshes/actual PhysX. It is closed-training evaluation, not live. The user's spinning/jump-stop complaint is retained; source yaw command range is nonzero, and no unique cause or repaired STAIRS3 policy is claimed. Preserve the visible user window. No viewer replay, model/raw/media content or GPU query was performed for Git.

All frozen source, originals, false/errors, local/remote receipts, complete captured UTF8, metadata and same-automation handoff are indexed. Incomplete190 expert-native source is explicitly excluded until frozen; fullRM70/E2/E3/SuperMimic work remains authorized and incomplete. New194 normal/final/formalCPU/cost and future GUI exit require ordinary supplements, not a second trial tag. Ultimate270mm jump and stable recovery is still unachieved.
''',encoding='utf8');selected.append(note.relative_to(G).as_posix())
import record_experiment as recorder
# Invoke the unchanged recorder in-process to avoid Windows argv length limits.
# Only staging transport is batched; record metadata/commit/tag/push are original.
record_git=recorder.git
def batch_git(*args):
 if args[:2]==('add','--'):
  for i in range(2,len(args),32):record_git('add','--',*args[i:i+32])
  return ''
 return record_git(*args)
recorder.git=batch_git
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Train literal Fudan JUMP on own400N50DR plane for human-authorized two hours194','--kind','training','--note-file',str(note),'--validation','Original19methods/config text identity; sourceCPU5groups;18GO refusals; actual64env0PT; new20kPPO FIRST fullstate; closed188 and191/193 all failures retained','--files',*selected,'--push']
recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head and git('ls-remote','origin','refs/heads/main').split()[0]==head
assert not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,protected_old1499_objects_peels=True,tag_count=len([k for k in after if not k.endswith('^{}')]),indexed_files=len(rows),clean=True)))
