"""One actual200 eval/display phase; include197 closing and all original refusals."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
B=Path(__file__).resolve().parent;T=B.parent;G=T.parent/'polar-rl-train';R=B/'reports'
N=T/'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031'
OLD=T/'JUMP197_FINAL5367_USER_MUJOCO_V200_20261031'
ID='mod4-jump197-final5367-user-mujoco-plane200';TAG='trial-20261031-'+ID
V=G/'versions'/('20261031_'+ID)
def read(p):return json.loads(Path(p).read_bytes())
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return {x.split()[1]:x.split()[0] for x in s.splitlines() if x.strip()}
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
assert not git('status','--porcelain') and not git('tag','--list','*'+ID+'*') and not V.exists()
case=read(R/'ROOT200V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json')
assert case['passed_execution'] and case['result']['model_iteration']==5367 and case['result']['original_Fudan_JUMP_reward_and_plane']
assert read(R/'ROOT200V2_ALL_SSH_CLOSED_SESSION_RESTORED_LEASE_FREE.json')['global_serial_lease']=='FREE'
visible=read(R/'ROOT200_NATIVE_WINDOW_VISUAL_VERIFIED_ACTUAL.json');assert visible['native_vision_verified']
assert read(B/'VISIBLE_MUJOCO200_ACTUAL_V2/DISPLAY200_WINDOW_STARTED_ACTUAL.json')['model_iteration']==5367
closed=read(N/'reports/ROOT197_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')
cpu=read(N/'reports/ROOT197_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')
assert closed['passed_collection'] and closed['owner_closed']['canonical_None'] and cpu['roles']['h1_210']['passed']
req=read(R/'AUTOMATION200_CLOSED197_AND_PRIMARY_WINDOW_UPDATE_REQUEST.json')
a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert a['id']=='mod4-10' and a['status']=='ACTIVE' and a['prompt']==req['prompt'].rstrip('\n') and a['rrule']==req['rrule'] and a['target_thread_id']==req['targetThreadId']
assert not read(R/'AUTOMATION200_CLOSED197_AND_PRIMARY_WINDOW_UPDATE_RECEIPT.json').get('isError')
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert len([k for k in old if not k.endswith('^{}')])==1501 and all(remote.get(k)==v for k,v in old.items())
put('AUTOMATION200_PERSISTED_EXACT_SAME_HOURLY_THREAD_VERIFIED.json',dict(epoch=time.time(),passed=True,no_new_automation_Goal=True))
put('ARCHIVE200_ACTUAL_EVAL_DISPLAY_ONCE_CONSUMED.json',dict(epoch=time.time(),ID=ID,TAG=TAG,protected1501_old_objects_peels=True,no_binary_model_raw_GPU_access_for_Git=True))
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for index in (G/'versions').rglob('CAPTURE_INDEX.json'):
    try:v=read(index)
    except (UnicodeDecodeError,json.JSONDecodeError):continue
    for row in v.get('files',[]):
        sha=row.get('SHA') or row.get('sha256');gp=row.get('Git_path') or row.get('git_path')
        if sha and gp and row.get('capture')=='full_UTF8_byte_exact' and (G/gp).is_file():known.setdefault(sha,gp)
binary={}
for root,name in ((N,'PRIMARY197_COMPLETE_MANIFEST.json'),):
    for row in read(root/name)['files']:
        if row.get('local_relative'):binary[str((root/row['local_relative']).resolve()).lower()]=(row['SHA'],str(root/name))
for key,row in closed['formals'].items():binary[str(Path(row['path']).resolve()).lower()]=(row['SHA'],'Original197 terminal transfer receipt')
row=read(N/'reports/ROOT197_HANDOFF_SOURCE194_COMPLETE_SAVED_PREFIX_RETURNED_ACTUAL.json')['formal']
binary[str(Path(row['path']).resolve()).lower()]=(row['SHA'],'Original197 saved194 transfer receipt')
row=read(R/'ROOT200_ONE_NEW_CAPTURE_TRANSFER_TWO_HOST_SHA_ACTUAL.json')
binary[str(Path(row['path']).resolve()).lower()]=(row['SHA'],'Original200 one-transfer two-host receipt')
binary_suffix={'.pt','.pth','.onnx','.npz','.npy','.usd','.usda','.usdc','.stl','.obj','.mtl','.zip','.tar','.gz','.7z','.png','.jpg','.jpeg','.mp4','.avi','.mat','.slx','.jsonl','.bin','.pyc','.pyd','.dll','.hf'}
text_suffix={'.py','.json','.txt','.md','.log','.xml','.yaml','.yml','.toml','.sh','.ps1','.cfg','.ini','.csv','.tsv','.m','.urdf','.diff','.sha256'}
V.mkdir();rows=[];selected=[]
for root in (N,OLD,B):
    for source in sorted(root.rglob('*')):
        if not source.is_file() or '__pycache__' in source.parts:continue
        size=source.stat().st_size;rel=source.relative_to(root)
        if source.suffix.lower() in binary_suffix or source.name.startswith('events.out.tfevents'):
            sha,producer=binary.get(str(source.resolve()).lower(),('unknown','No content read for archival; use associated producer receipts'))
            rows.append(dict(path=str(source.resolve()),bytes=size,SHA=sha,producer=producer,capture='metadata_only_no_content_read_for_Git'));continue
        assert source.suffix.lower() in text_suffix or any(s in source.name.lower() for s in ('.py.','.py_','.json.','.sh.','.m.','.xml.')),str(source)
        raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
        if sha in known:
            rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=known[sha],capture='full_same_SHA_reference'));continue
        try:text=raw.decode('utf8')
        except UnicodeDecodeError:
            dest=V/root.name/(rel.as_posix()+'.bytes.b64.txt');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(base64.b64encode(raw).decode('ascii')+'\n',encoding='ascii')
            rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=dest.relative_to(G).as_posix(),capture='byte_exact_base64_nonUTF8_source',decode='Base64 decode excluding final newline'));selected.append(dest.relative_to(G).as_posix());continue
        safe,count=redact(text);dest=V/root.name/rel;dest.parent.mkdir(parents=True,exist_ok=True);out=raw if count==0 else safe.encode('utf8');dest.write_bytes(out)
        rows.append(dict(path=str(source),bytes=len(raw),SHA=sha,Git_path=dest.relative_to(G).as_posix(),archive_SHA=hashlib.sha256(out).hexdigest(),redactions=count,capture='full_UTF8_byte_exact' if count==0 else 'full_UTF8_credential_pattern_redacted'))
        selected.append(dest.relative_to(G).as_posix())
        if count==0:known[sha]=dest.relative_to(G).as_posix()
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,
    source_control_once_entries_never_replayed=True,no_model_raw_NPZ_USD_media_or_host_GPU_reads_for_Git=True,
    pending_excluded=['Future original200 viewer console/exit after current capture: later ordinary append, no auto reopen/kill',
        'Background expert190/RM70/E2/E3 unchanged; no new selected source in this phase']),ensure_ascii=False,indent=2),encoding='utf8');selected.append(index.relative_to(G).as_posix())
note=V/'EXPERIMENT_NOTE.md'
note.write_text('''The user freshly requested MuJoCo playback and explicitly clarified the primary, not E0 branch. This200 purpose binds only the primary final5367 model SHA f286110a39a1062f96fd21038c05b772da5f5a72ebdab8421c403f73e5cc3afe and its original Fudan JUMP plane/unchanged19methods+full config16scales, own nominal400N/k2000,50Hz policy/100Hz feedback/2.5msTGS32-4F32/D0-D7/per-env2mm/mimic.01. No STAIRS3, E0 weights, old case replay, teacher states, forces, reset injection, reward change or relaxed guard. The separate E0 branch is not shown.

The original197 normal900 collector was executed once after its original latest signed eligibility. Complete original owner/node/worker waits, locks, canonicalCNone, exactGO owner segment, independent original fees and new formal transfer integrity are preserved. Two NEW formal initialCPU qualifications read only those new outputs; old194/E0/native/normal86 are not reloaded. Primary's original194 plus197 learning window was completed with368new updates/176640000transitions/iteration5367/17Adam107380. E0 actual qualification remains as its original closing reports; training state does not prove jump skills. No budget writing, grant, refund, clamp, clearactive or extra writer for collection or evaluation.

New200 uses one targetGPU checkpoint read/decode and only a deterministic actor mean forward, no WM/Critic forward, optimizer or learner. A fresh originalN1 first episode runs up to1000controls/20s or original physical termination. Cached current31body poses are recorded before automatic reset; contact z/flight flags reuse the reward's already-read tensor, no extra raw contact view or extra reward call. Original50Hz action/100Hz feedback/400Hz physics counts and all failures are kept. Root statuses and contact-only flight/absolute root height are not jumping clearance or stable-landing certification. This one visual case is not a population success rate or270mm acceptance.

The user-visible MuJoCo uses the original277 meshes/31bodies and the original flat plane. It renders the newly captured actualPhysX endpoints, with final model/source/commands/termination and contact scope labelled. It is recorded evaluation after training, not live learning, localMuJoCo physics, local neuralCUDA or invented PPO WM predictions. Native window vision verifies the actual image. One newNPZ transfer/two-host integrity and one local visual byte pass/each member read are admitted; old raw/reference/model reads0. Existing user windows are preserved, new viewer bounded2h; no auto reopen/kill.

The V1 source-preparation query lookup AssertionError occurred before any remote/model/SDK action. Its full original source and partial outputs remain; V2 fixes only the already-renamed caller query lookup and separate unused namespace. Actual remote errors/results and GUI errors/repairs, if any, remain in the full capture. All originals, source, leases/CIM, stdout/UTF8, exact receipts and same-hourly-automation update are indexed. Binary models/NPZ/USD/media are metadata-only, existing producer hashes or unknown, with no content/hash/GPU access for Git. Original197 tag is consumed; this is one real200 evaluation/display phase and protects all1501 old tag objects/peels. Future viewer logs/exits are ordinary supplements, never a new200 tag. Genuine270mm jump and stable recovery remains subject to actual evidence, not inferred from this picture.
''',encoding='utf8');selected.append(note.relative_to(G).as_posix())
import record_experiment as recorder
original_git=recorder.git
def batched(*args):
    if args[:2]==('add','--'):
        for i in range(2,len(args),24):original_git('add','--',*args[i:i+24])
        return ''
    return original_git(*args)
recorder.git=batched
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Show primary final5367 literal Fudan JUMP PhysX case in trueMOD4 MuJoCo200','--kind','evaluation','--note-file',str(note),'--validation','Original197 close and NEWformalCPU; one final5367 actor-only original-plant case; exact body pose display and native window vision; original errors retained','--files',*selected,'--push']
recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head and git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,protected1501_objects_peels=True,indexed_files=len(rows),tag_count=1502,clean=True)))
