"""Record one assessment stage with every original trial and user-view receipt."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
B=Path(__file__).resolve().parent;T=B.parent;G=T.parent/'polar-rl-train';R=B/'reports'
ID='mod4-e0-jump201-and-zero-yaw207-comparison';TAG='trial-20261031-'+ID;V=G/'versions'/('20261031_'+ID)
roots=[T/'JUMP_E0_FINAL32066_HEADLESS_SAME_PLANE_V201_20261031',T/'JUMP_E0_FINAL32066_HEADLESS_SAME_PLANE_V201_20261031_V2',
    T/'E0_FROZEN_BASE_MIXED_GROUND_JUMP_TASK_V202_20261031',T/'E0_FINAL32066_USER_MUJOCO_V203_20261031',
    T/'E0_FINAL32066_FRESH_REOPEN_V205_20261031',T/'FORWARDED210_TRAIN_HISTORY_COMPARISON_V206_20261031',B]
def read(p):return json.loads(Path(p).read_bytes())
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return {x.split()[1]:x.split()[0] for x in s.splitlines() if x.strip()}
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
assert not git('status','--porcelain') and not V.exists()
assert not git('tag','--list','*'+ID+'*') and not git('tag','--list','*headless201*'),'Any existing selected phase is consumed; do not record again'
actual=read(R/'ROOT207_TWO_ORIGINAL_ZERO_YAW_CASES_RETURNED_ACTUAL.json')
assert actual['passed_execution'] and all(x['passed'] for x in actual['cases'].values())
assert read(R/'ROOT207_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_client_lease']=='FREE'
assert read(roots[1]/'reports/ROOT201V2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json')['passed_execution']
assert read(roots[4]/'reports/CURRENT_ACTUAL205_FRESH_E0_USER_WINDOW_NATIVE_VERIFIED.json')['native_vision_verified']
assert read(roots[3]/'reports/ACTUAL204_E0_BRANCH_LITERAL_JUMP_REWARD_SOURCE_AND_RUNTIME_AUDIT.json')['source_19_methods_and_entire_reward_config_literal']
req=read(R/'AUTOMATION207_ACTUAL_COMPARISON_AND_FROZEN_E0_MIX202_UPDATE_REQUEST.json')
app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert app['prompt']==req['prompt'].rstrip('\n') and app['status']=='ACTIVE' and app['rrule']==req['rrule'] and app['target_thread_id']==req['targetThreadId']
assert not read(R/'AUTOMATION207_ACTUAL_COMPARISON_AND_FROZEN_E0_MIX202_UPDATE_RECEIPT.json').get('isError')
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert len([k for k in old if not k.endswith('^{}')])==1502 and all(remote.get(k)==v for k,v in old.items())
put('AUTOMATION207_PERSISTED_EXACT_SAME_HOURLY_ORIGINAL_THREAD_VERIFIED.json',dict(epoch=time.time(),passed=True,same_id_kind_name_schedule_target=True,no_new_Goal_or_automation=True))
put('ARCHIVE207_COMPARISON_ONCE_CONSUMED_BEFORE_RECORD.json',dict(epoch=time.time(),ID=ID,TAG=TAG,protected1502_old_tag_objects_peels=True,
    original201_archive_plan_unused_merged=True,all_original_trial_ids_preserved=True,no_model_raw_binary_or_host_GPU_reads_for_Git=True))
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={}
for index in (G/'versions').rglob('CAPTURE_INDEX.json'):
    try:v=read(index)
    except (UnicodeDecodeError,json.JSONDecodeError):continue
    for row in v.get('files',[]):
        sha=row.get('SHA') or row.get('sha256');gp=row.get('Git_path') or row.get('git_path')
        if sha and gp and row.get('capture')=='full_UTF8_byte_exact' and (G/gp).is_file():known.setdefault(sha,gp)
known_binary={}
transfer=read(roots[1]/'reports/ROOT201_ONE_NEW_CAPTURE_TRANSFER_TWO_HOST_SHA_ACTUAL.json')
known_binary[str(Path(transfer['path']).resolve()).lower()]=(transfer['SHA'],'Original201 new artifact transfer/two-host SHA receipt')
binary={'.pt','.pth','.onnx','.npz','.npy','.usd','.usda','.usdc','.stl','.obj','.mtl','.zip','.tar','.gz','.7z','.png','.jpg','.jpeg','.mp4','.avi','.mat','.slx','.jsonl','.bin','.pyc','.pyd','.dll','.hf'}
text_types={'.py','.json','.txt','.md','.log','.xml','.yaml','.yml','.toml','.sh','.ps1','.cfg','.ini','.csv','.tsv','.m','.urdf','.diff','.sha256'}
V.mkdir();rows=[];selected=[]
for root in roots:
    for source in sorted(root.rglob('*')):
        if not source.is_file() or '__pycache__' in source.parts:continue
        rel=source.relative_to(root);size=source.stat().st_size
        if source.suffix.lower() in binary or source.name.startswith('events.out.tfevents'):
            sha,producer=known_binary.get(str(source.resolve()).lower(),('unknown','Existing producer metadata only; no content/hash read for archival'))
            rows.append(dict(path=str(source.resolve()),bytes=size,SHA=sha,producer=producer,capture='metadata_only_no_content_read_for_Git'));continue
        assert source.suffix.lower() in text_types or any(x in source.name.lower() for x in ('.py.','.py_','.json.','.sh.','.m.','.xml.')),str(source)
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
remote_artifacts=[dict(role=k,artifact=v['case']['artifact'],model_SHA=v['case']['model_SHA'],model_iteration=v['case']['model_iteration'],raw_transferred=False,raw_opened_for_Git=False) for k,v in actual['cases'].items()]
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,remote_artifacts_metadata_only=remote_artifacts,
    trials=['201 original premodel source failure','201V2 E0 same-plane case','202 frozen-base mixed task SPEC_ONLY',
            '203 first user E0 view and actual exit','204 source/runtime literal reward audit','205 fresh requested reopen/native vision',
            '206 fresh unread historical log prefix review','207 primary/E0 eval-only zero-yaw cases'],
    pending_excluded=['Actual202 mixed SDK/runtime/GO/learning still not implemented, never claim started',
        'Future205 console/exit after current capture: ordinary append only, no autoreopen',
        'Background190/RM70/E2/E3 unchanged source, no new actual phase in this capture'],
    model_raw_NPZ_binary_or_host_GPU_reads_for_Git=0),ensure_ascii=False,indent=2),encoding='utf8');selected.append(index.relative_to(G).as_posix())
note=V/'EXPERIMENT_NOTE.md'
note.write_text('''The user requested assessment and playback of the separate E0-start jumping branch, then required original E0 to remain frozen with a small ground-retention subset in future jump training. The immutable source E0_82 a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a remains separate; trained32066 is a copy, with82 new jump PPO updates. The already-completed198 window contained100%JUMP environments, not a hidden mixed curriculum. New202 is a frozen requirement/spec only: root default90%JUMP/10%originalE0 ground, separate original reward kernels and task modes, on-policy trainable-copy actions. Exact E0 flat profile/source join and complete source/CPU/actual mixed SDK admission/fullstate/TaskGO/solewriter/freshresources are pending; no new mixed learning is claimed.

201V1 preserved an avoidable source-generation failure: unrestricted version-number substitution200 to201 changed physical numeric2000 to2010 and20ms queue20000 to20100. The premodel assertion refused before checkpoint read/decode or policy controls; original Kit processRC0 did not make functionERROR a pass. Original source/partial outputs/fullUTF8 remain intact. A distinct201V2 namespace rebuilt from the successful200 source with digit-bounded substitutions and proved the numeric AST unchanged except model iteration. It reused the already-uploaded new E0 formal, loaded it once on GPU and produced a fresh deterministic20s first episode in original400N50D0-D7 MOD4 PhysX.1000controls/8000physics/2000feedback completed with time_out only; all physical non-timeout terms false. Wheel-center maximaL/R.077221/.097425m were low compared with primary5367 .452922/.452137m; these are independent center maxima, not wheel-bottom clearance or stable-jump certification. New201 artifact830515B SHA4c1b4cf5bf659a0114c2bbbd8e8a5558585c4872c3374e7bc10b5290f2241fb9 transferred once/two-host SHA, with no numerical statistics reopen.

Fresh203 user display used the original277 meshes/31mocap bodies and one admitted first local visual pass of201. Its own window40848 exited after20.2423713s; root retained the sky-session initialization error and empty-target result without fabricating a live native screenshot or reopening. Root inspected the original renderframe. Fresh user205 reopen was a separate new admitted visual purpose and launcher, no old once replay: window9800 and returnedHWND2300422 were natively checked with the correct E0branch32066/title/20s source. Primary window was preserved. Original rewards and16weights are still byte-literal:204 compared method8959B SHA514822b6d86c02bb7501d04a2c63c04b46e3b0aac07e1de204111b70b42ac244 and config3456B SHA8d3403cfeff086966e736332e42db54c13124761a96b6d23fbdca8caf7b8ccd7 against the pinned source package and both actual20k training/N1 runtime readbacks. The19methods/fullconfig/clip2.5/no totalpositiveclip/contact-flight memory remain unchanged; real MOD4 geometry/state/400N50DR/SDK dt mapping remains explicit outside the reward. Do not claim the entire foreign Fudan environment is unchanged.

206 addressed the user's forwarded4090 history request with one read-only serial control purpose: fresh72CNone then strict210. It read only the previously unread log prefix[0,10448251), reusing the already-captured185 tail[10448251,10558251), with no checkpoint content/hash/SDK/GPU access. The original run logs4700 updates from300 through4999,2256000000 environment steps,06:07:17 elapsed. E0 had82 new jump updates/39360000transitions, not32066 jump updates. Original source also used100Hz/k3500 engineering branch/TGS32-16/no targetDR, versus approved400N50/k2000/TGS32-4/DR. The primary still jumped in current200; E0 is a different warmstart/history, not evidence that primary was overwritten or destroyed. Training insufficiency is a plausible leading hypothesis, not a unique causal conclusion.

Original displayed cases used fixedseed27 with aboutvx-.3947m/s and yaw+1.66rad/s. Literal tracking_ang_vel rewards matching yaw; gravity orientation does not constrain absolute heading.207 therefore performed one new controlled eval-only factor, yaw command range0, for each qualified same model, retaining original rewards/weights/plant/reset/DR/vx/height/50Hz/guards. Each fresh N1 completed1000controls/8000physics/2000feedback/20s with time_out only and measured yaw command exactly0. Primary5367 final net heading change was-18.7433degrees, maximumcommonwheel-center height.4454257m. E0branch32066 net heading change was275.5631degrees, maximumcommonwheel-center height.0716888m. Thus original nonzero commands do not fully explain E0 rotation: it still has substantial yaw tracking error at0. Primary retained strong lift without repeated full-circle turning in this one case. These center-height and heading diagnostics are not wheel-clearance/stable-landing or270mm acceptance and are not population success rates. No training/optimizer/budget writes or viewer switch occurred;207 artifacts remain remote producer-indexed, not transferred/opened locally. Both new GPU model reads/decodes were admitted once, original inputs/old raw were not replayed. All owned worker waits/app closes/privateEX release/SSH finally/session restoration are original receipts.

This one related assessment phase preserves every201-207 trial purpose, originals, false/error/fullUTF8, source, parameter/IO contracts, exact CPI/worker identities, actual results and same-hourly automation update. The unused standalone201 archive plan is explicitly merged here, with no duplicate201 tag. Source/spec-only202 and display/audit-only203-206 receive no false GPU-learning tags. Models/raw/NPZ/USD/media are metadata-only with existing producer hashes or unknown; no binary/model/raw/GPU activity for Git. Protect all1502 older tag objects/peels. Future viewer logs/exits are ordinary supplements. Original E0 remains frozen, no current own learning is claimed, and genuine270mm jump/landing/stable recovery remains unachieved.
''',encoding='utf8');selected.append(note.relative_to(G).as_posix())
import record_experiment as recorder
original_git=recorder.git
def batched(*args):
    if args[:2]==('add','--'):
        for i in range(2,len(args),24):original_git('add','--',*args[i:i+24])
        return ''
    return original_git(*args)
recorder.git=batched
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Compare qualified E0 jumping201 and zero-yaw primary/E0 cases207 with frozen-base plan','--kind','evaluation','--note-file',str(note),
    '--validation','201V2 actual20s and original premodel failure;203/205 fresh views;204 literal source/runtime;206 original log history;207 two20s yaw0 cases; all old1502 tag objects protected',
    '--files',*selected,'--push']
recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head and git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,protected1502_objects_peels=True,tag_count=1503,indexed_files=len(rows),clean=True)))
