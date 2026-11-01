"""Archive all saved stage trials/reports; large artifacts remain indexed only."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';G=W/'polar-rl-train'
ID='mod4-lqr-mpc-teacher-assisted-depth-student286';TAG='trial-20261101-'+ID
V=G/'versions'/('20261101_'+ID)
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{x.split()[1]:x.split()[0]for x in s.splitlines()if x.strip()}
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not V.exists() and not git('status','--porcelain') and not git('tag','--list','*'+ID+'*'),'Existing objects must be pushed/continued, never record or retag again'
work=read(R/'CURRENT_ACTUAL286_TEACHER_DEPTH_STUDENT_WORK_ORDER_V2.json');assert work['first']['passed'] and work['first']['actual_new_Pi_updates']==1
assert read(R/'ROOT286_STATUS_ARCHIVE1_SSH_FREE.json')['global_serial_control_client_lease']=='FREE'
app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
req=read(R/'AUTOMATION_ACTUAL286_UPDATE_REQUEST.json')
assert app['prompt']==req['prompt'].rstrip('\n') and app['target_thread_id']==req['targetThreadId'] and app['rrule']==req['rrule']
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(remote.get(k)==v for k,v in old.items())
remote_lqr=git('ls-remote','origin','refs/heads/lqr').split()[0]
assert remote_lqr=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
put(R/'RECORD286_PHASE_ONCE_CONSUMED_BEFORE_RECORD.json',dict(epoch=time.time(),ID=ID,TAG=TAG,
 protected_old_tag_objects_peels=len(old),lqr_branch=remote_lqr,no_experiment_model_raw_GPU_reads_for_Git=True))
put(R/'AUTOMATION_ACTUAL286_UPDATE_APP_RECEIPT.json',dict(epoch=time.time(),
 tool_return='Updated automation in the app.',automationId='mod4-10',mode='update',status='ACTIVE',
 request=str(R/'AUTOMATION_ACTUAL286_UPDATE_REQUEST.json'),request_SHA=H(R/'AUTOMATION_ACTUAL286_UPDATE_REQUEST.json'),
 saved_configuration_exact_prompt_schedule_target_verified=True,targetThreadId=app['target_thread_id']))
put(R/'LOCAL_COMMAND_FAILURES_PRESERVED_286.json',dict(epoch=time.time(),
 entries=[dict(trial_id='continuation-history-read-size',error='read_thread10turns with outputs exceeded single-turn response size; retried3then2 without outputs',no_mutation=True),
 dict(trial_id='continuation-root-inventory',error='broad rg output truncated and inaccessible rmuc unpack path; subsequent scoped reads used',no_mutation=True),
 dict(trial_id='continuation-source-path-lookup',error='guessed package root PPO/plant paths missing; rg actual nestedruntime/control_core resolved',no_model_read=True),
 dict(trial_id='continuation-not-git-root',error='git status in experiment staging parent refused; actual repo polar-rl-train clean',no_mutation=True),
 dict(trial_id='continuation-status-invalid-cwd',error='invalid directory typo MOD4_H1_SCUT_STEP270_ON_2103? failed before command; corrected actual286 cwd used',no_remote_or_model_read=True),
 dict(trial_id='new-final-reader-ast-false',error='conditional missing space after else; original source snapshot and AST repair preserved',new_CPU_reader_UNEXECUTED=True)]))
note=R/'TEACHER286_EXPERIMENT_NOTE.md'
with note.open('x',encoding='utf8')as f:f.write('''The user explicitly instructed the previous chat to start LQR/MPC teacher-assisted depth SuperMimic RL; the current chat requested reading that conversation and continuing. This phase continues the interrupted source282, preserves all prior bytes, and starts a distinct depth student through the existing original72 sole canonical owner. It does not claim successful autonomous270mm stair landing.

Original276V3 completed its one-hour WM-only window normally:4719WM updates,4750controls/380000own transitions, final31985705bytes SHA cbd25c80a55c87296b4b2a50eb21869e4b12127f9aa3a5d5f9a607823d44242b. Its original owner settled3602.413195848465s once. The new281 LayerNorm-aware CPU reader passed531 finite tensors; no Pi/Critic updates occurred during276. These post-276 reports and281 source are included as ordinary supplements, without rerunning or retagging276.

The interrupted282 created two successful fullDR LQR/MPC references from the already saved MuJoCo cases, each250states at50Hz with actual source times, only state labels. Original MuJoCo100Hz torque labels are not copied or averaged into50Hz normalized actions, and foreign MuJoCo transitions are never added to the own PhysX WM replay. The earlier282 generated IndentationError is preserved beside its unused source_v2, stale state-loss copy and reference producer metadata. We copied the corrected root282 learner to independent283, repaired inherited WM-only Task/node/save/count semantics, made separate actor/Critic/WM optimizer state explicit and retained all teacher/fullstate/norm/RNG/DR/queue/air-contact-action memory.

CPU283 initially failed before migration because a CUDA Philox16B sampling state was handed to a CPU MT19937 generator. IndependentCPU284 explicitly uses a fresh CPU-only admission RNG; production preserves the CUDA RNG. CPU284 next exposed eight passive guide roller naming differences (guide_roller_00..07 versus guide_roller_spin_0..7); all22 other named joints match exactly. The alias fix used the already resident decoded carrier, without rereading it. Both original CPU errors and original source snapshots are retained. Actual source RSL PPO constructor and live parameter object IDs bind all17Adam states; target actor9/Critic8 states are partitioned once, not duplicated. Actor35->44/Critic38->47 append9zero input columns and corresponding zero moments. Original weights/STD/Adam42940/LR restore are preserved; current student training explicitly selectsLR1e-4 and keeps learnedSTD frozen. CPU H32 no-step test produced finite nonzero reward-only8.145936/terminal-only16.229773/teacher-only1.023393/combined19.647617 actor gradients with exact before/after parameter and norm preservation. It is synthetic integration evidence, not world accuracy.

Actual283 failed authoring the physical mesh before any model read: USD rejects a mixed Python/NumPy scalar list for VtArray<GfVec3f>. Owner/node naturally closed; original fee18.382315635681152s retained. Independent285 uses float32array.tolist, preserving geometry. It built the scene and decoded the carrier once, then failed restoring RNG because torch.load(map_location=cuda) moved its ByteTensor to CUDA while Generator.set_state expects CPU storage. No new learning step occurred; original fee22.172412395477295s retained. Independent286 restores the original CUDA Philox byte state through.cpu(). All old frozen sources, false outcomes, full stdout, actual terminal rows and fees remain unchanged.

Actual286 began2026-11-01T18:29:00.362623+08:00, original SAVE19:29:00.362623/NOMINAL19:34:00.362623, normal900 earliest19:19:00.362623. One4090 c27GPU,80environments (72single270mm platforms and8disjoint originalE0ground),50Hzpolicy/100Hzfeedback/400Hzphysics2.5msTGS32/4F32,400Nengineeringk2000/fullD0white_v3D1-D7/closure10mm per-env reset/mimic.01rad. New platform edge distance.65..1.35m, lateral+/-.12m, yaw+/-.12rad are seeded fixed per-env placements; they are not an unchanged original Fudan .21m curriculum or held-out navigation test. Provisional front-fixed geometric RayCaster84x48 mount(.15,0,.15)m/down10deg is not actual D435i stereo/FPS/hardware calibration.

The actor sees proprioception35+current observed depth9. The critic sees38+depth9. Teacher/GT targets stay on the supervision side; H32 context uses only the first currently observed world support anchor and predicted poses, with no future real camera or GT map fallback. Original Fudan19methods/16weights/per-termclip2.5dt.02 and original reward buffers stay unchanged. A separately declared state reference auxiliary coefficient max(.05,1-Pi_updates/4000) joins original reward plus terminal critic; the critic target excludes teacher loss. This is SuperMimic differentiable policy/value learning, not a PPO update. The frozen reference controllers are never retrained.

Actual286 passed24native controls/192physics/48feedback before firstWM update. Before any student step, it verified H32 gradients using its real fresh own replay and original current-depth anchors. Its first real student update completedPi1/Critic1 and newWM33(total4752),64controls/5120own transitions/512physics/128feedback. Reward-only8.797243/terminal-only19.540718/teacher-only.977907/combined24.384129 gradients were finite and nonzero. Complete first artifact32407215bytes SHA156c7c92252264a75ce18e7bce106a3041d93d7d62c497e1011a14108c95ea42 contains actor/CriticAdam42941,WMAdam4752, full teacher/STD/three optimizers/norm/RNG/DR/queue/reward memory. ARCHIVE1 observedPi280/Critic280/newWM312(total5031),343controls/27440transitions.1526episode terminations (1525orientation/1basecontact,0closure/0mimic) remain evidence that skill is unfinished. Loss decrease, root height or flight counts are not strict stair success.

Inherited Task descriptive276 flags (WM_ONLYtrue/Pi_allowedfalse/oldterrain etc.) contradict the new explicit kind/44/47/current4719/GO_WM_ONLYfalse and actual three-optimizer FIRST; an append-only scope correction discloses them. Frozen Task/source are not hotpatched or used to hide the contradiction. Future Task constructors must select/override the relevant current fields. Nested reused273 WM-module metadata remains WM-module scope. Historical production source-read receipt names still include276; the unused normalV1 incorrectly renamed one. A separate normalV2 corrected that source name and an unusedSHA literal, passed signed900 boundary/closed/finalpositive/earlysave rejection metadata checks. Both unusedV1 andV2 are preserved. No healthy training restart was done for metadata cleanup.

The unused normalV2 collector preserves original owner850/node180 waits, all-own-exits/zombie identity, private and shared locks, canonicalNone, one original segment/GO equality, rawfeeSUMONCE, finalsave>=deadline and exactly one qualified newformal transfer/two-hostSHA. A separately frozen NEWfinal CPU reader awaits that qualified formal. Its initial local AST spacing error and source are retained; no finalmodel read has occurred. Current heartbeat retains schedule/status and is routed to the new continuation chat because the former chat rejects cross-account encrypted history. It stays quiet while state is unchanged/non-actionable and continues existing authorized scope only; no newgrant, secondwriter, automatic extra window or budget copy/clear/refund.

Every saved source/error/report/handoff/automation receipt through this archive is included. LargePT/NPZ/USD/media are indexed from producer paths/bytes/SHA, never read forGit. All old annotated tagobjects and peels plus lqr branch5848b45a are protected. PostGit remote checks stay tool output instead of producing an endless chain of new reports. Subsequent normalfinal/fee/CPU/evaluation reports require an ordinary supplemental commit, not replay of this record/tag or any consumed once.
''')
names=['OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276V3_20261101','WM276_NEW_FORMAL_CPU_LAYERNORM_READER_V281_20261101',
 'LQR_MPC_DEPTH_TEACHER_STUDENT_V282_20261101','LQR_MPC_DEPTH_TEACHER_STUDENT_V283_20261101',
 'LQR_MPC_DEPTH_TEACHER_STUDENT_V285_20261101',N.name]
roots=[(name,T/name)for name in names]
capture_source=(T/'D435I_DEPTH270_BOUND_SOURCE_V266_20261101/archive_actual10mm_depth_supermimic246_once.py').read_text('utf8')
a=capture_source.index("sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact")
b=capture_source.index("index=V/'CAPTURE_INDEX.json'",a)
exec(compile(capture_source[a:b],'<existing content-addressed capture engine>','exec'),globals())
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,
 actual286_workorder=work,protected_old_tag_objects_peels=old,lqr_branch=remote_lqr,
 binary_metadata_only=True,models_raw_GPU_reads_for_Git=0),indent=2,ensure_ascii=False),encoding='utf8')
selected.append(index.relative_to(G).as_posix())
import record_experiment as recorder
original_git=recorder.git
def batch(*a):
    if a[:2]==('add','--'):
        for i in range(2,len(a),24):original_git('add','--',*a[i:i+24])
        return''
    return original_git(*a)
recorder.git=batch
note_gp=next(r['Git_path']for r in rows if r['path']==str(note))
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title',
 'Start LQR/MPC teacher-assisted depth SuperMimic student with real three-optimizer learning; preserve all integration failures',
 '--kind','training','--note-file',str(G/note_gp),'--validation',
 '276normalfinal4719WM380000pairs+281CPU;282ASTfalse;283CPU-RNGfalse/284cachedrolleraliasCPUH32pass0steps;actual283USDscalarfalsefee18.3823;285CUDA-RNGstoragefalsefee22.1724;286realnative24/H32gradient/Pi1critic1WM4752/full32407215Bsave;ARCHIVE1Pi280critic280WM5031/343controls27440pairs/1526terminations0closure0mimic;80env400N50Hz10mm/originalFudan+separateteacheraux;normalV2/NEWfinalCPUunused;alloldrefsprotected/270skillpending',
 '--files',*selected,'--push'];recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG)
assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
assert git('ls-remote','origin','refs/heads/main').split()[0]==head
assert git('ls-remote','origin','refs/heads/lqr').split()[0]==remote_lqr and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,tag_count=len([k for k in after if not k.endswith('^{}')]),
 indexed_files=len(rows),new_full_files=len(selected),old_refs_protected=True,lqr_protected=True,clean=True)))
