from pathlib import Path
import base64,hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';G=W/'polar-rl-train'
ID='mod4-lqr-mpc-depth-supermimic-teacher-route-review279';TAG='trial-20261101-'+ID;V=G/'versions'/('20261101_'+ID)
def read(p):return json.loads(Path(p).read_bytes())
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{x.split()[1]:x.split()[0]for x in s.splitlines()if x.strip()}
def put(p,x):
 with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not V.exists()and not git('status','--porcelain')and not git('tag','--list','*'+ID+'*'),'Continue existing phase objects instead of record/retag again'
x=read(R/'CURRENT_USER279_LQR_MPC_TEACHER_FOR_DEPTH_SUPERMIMIC_WORK_ORDER.json');assert x['status']=='SOURCE_REVIEW_AND_TEACHER_ROUTE_PREPARATION_ONLY'and not x['new_GO']and x['source_AST_files']==5 and x['model_raw_trajectory_NPZ_SDK_GPU_optimizer_remote_reads']==0
req=read(R/'AUTOMATION_USER279_TEACHER_ROUTE_UPDATE_REQUEST.json');app=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'));assert app['prompt']==req['prompt'].rstrip('\n')and app['status']=='ACTIVE'and app['rrule']==req['rrule']and app['target_thread_id']==req['targetThreadId']
old=refs(git('show-ref','--tags','-d'));remote_old=refs(git('ls-remote','--tags','origin'));assert all(remote_old.get(k)==v for k,v in old.items());old_lqr=git('ls-remote','origin','refs/heads/lqr').split()[0]
put(R/'RECORD279_SOURCE_REVIEW_ONCE_CONSUMED.json',dict(epoch=time.time(),ID=ID,TAG=TAG,main_before=git('rev-parse','HEAD'),old_lqr_branch=old_lqr,source_only=True,no_actual_Pi_or_WM_training=True,protect_all_local_remote_tags=True))
roots=[(N.name,N)];put(R/'CAPTURE279_SOURCE_TEACHER_ROUTE_SCOPE.json',dict(epoch=time.time(),roots=[dict(archive_label=k,path=str(p))for k,p in roots],existing_LQR_reference=dict(branch=x['teacher_source']['branch'],commit=x['teacher_source']['commit']),source_only=True,pending=x['next_order']))
note=R/'USER279_LQR_MPC_TEACHER_DEPTH_SUPERMIMIC_SOURCE_REVIEW_NOTE.md'
with note.open('x',encoding='utf8')as f:f.write('''The human asked to use the successful LQR/MPC controllers as teachers for depth-camera SuperMimic stair learning. This phase reviews five actual local source files and records the integration route. It performs no model/trajectory/NPZ/SDK/GPU/optimizer/remote read or execution, no old one-shot replay and no new GO. Current276V3 WM warm and original save/exit/accounting stay untouched.

Local DSH prepare_reference.py already converts the real nominal LQR73state trace to50Hz by stride2 and preserves the measured timestamps; it explicitly labels this as reference-only, not PhysX world-model transitions or action cloning. Local train_supermimic.py has real-world replay plus differentiable imagined actor/critic training around a frozen E0 residual design. These are source observations, not a claim that the same current remote runtime is qualified or that this ROOT reselects retired E0 branches.

Crucially, this local LQRStepMDP.reward is a custom position/rotation/joint/velocity/top tracking reward, and step_env replaces the physical RewardManager with an alive term. The40context bridge is35observation corruption plus five zeros and has no D435i sensor use. That whole local MDP cannot be silently substituted for this chat's literal Fudan19methods/fullconfig16weights and real-depth future-safe pipeline. The source snapshots, actual sizes/SHA and AST result are retained; no module main was run.

Selected teacher-assisted direction: freeze the existing LQR and MPC, use their independently validated successful state/reference demonstrations with clearly declared separate supervised actor loss or supervised initialization, and train a depth student that observes only its own sensors/current depth. The original Fudan reward remains byte-literal; auxiliary imitation changes the learning objective and must be explicitly named/weighted/scheduled in a new Task. Teacher privileged WORLD state/known geometry/future reference may be labels or training targets, never the student's actor inputs, future-camera context or privileged map lookup. Randomized step placement/approach distance/bearing and goal-relative reference alignment are needed so a fixed episode-clock jump cannot masquerade as visual targeting.

The teacher is100Hz MuJoCo torque control while the target is50Hz normalized six-action own PhysX. Reference resampling does not establish controller/action transfer. Do not copy or average two torque outputs as normalized actions. Before action imitation, bind actual joint/motor names/order/units/PD/clipping/physical queues and own target clocks; until then use state/reference supervision. Teacher MuJoCo states must not enter target PhysX WM as measured dynamics transitions. Target WM learns only actual own-MOD4 transitions. Preserve400N engineeringk2000/fullD0-D7/50policy100feedback400physics2.5msTGS32/4F32/10mm closure/.01mimic and real motor/closed-joint dynamics.

Current276V3 completes its original bounded warm window first. Its original solewriter normal900 collector, one rawfeeSUMONCE, qualified NEWformal and one wholeCPU remain unchanged. Later a separate actual teacher-reference capture/mapping/loss-gradient purpose and explicit depth-goal task can integrate the frozen teachers, actual27744/47 mapping and learned WM. Do not create the backwards prerequisite that the teacher must already perfectly solve target PhysX270 before RL may learn; validate interfaces and finite physical execution, then assess learned skill independently. No current source/checkpoint/reward/GO is hotpatched and no fresh learning window is claimed by this source review.

All original source files, saved report and app update receipt are archived as a source-only evaluation phase. All old local and remote annotated objects/peels and the lqr branch head remain protected. No teacher dataset was read, copied or rehashed for Git; previous LQR results remain referenced at5848b45a on lqr. Later implementation must remain independently classified until actually executed.
''')
capture_source=(T/'D435I_DEPTH270_BOUND_SOURCE_V266_20261101/archive_actual10mm_depth_supermimic246_once.py').read_text('utf8');a=capture_source.index("sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact");b=capture_source.index("index=V/'CAPTURE_INDEX.json'",a);exec(compile(capture_source[a:b],'<reused-text-only-capture-engine>','exec'),globals())
index=V/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,source_review=x,old_local_tag_objects_peels=old,old_remote_tag_objects_peels=remote_old,protected_lqr_branch=old_lqr,source_only_not_learning=True),indent=2,ensure_ascii=False),encoding='utf8');selected.append(index.relative_to(G).as_posix())
import record_experiment as recorder
original_git=recorder.git
def batch(*a):
 if a[:2]==('add','--'):
  for i in range(2,len(a),24):original_git('add','--',*a[i:i+24])
  return''
 return original_git(*a)
recorder.git=batch;note_gp=next(r['Git_path']for r in rows if r['path']==str(note))
sys.argv=[str(G/'archive_tools/record_experiment.py'),'--id',ID,'--title','Review LQR/MPC teachers for depth SuperMimic and preserve literal Fudan reward boundaries; source only','--kind','evaluation','--note-file',str(G/note_gp),'--validation','5local source byte snapshots/AST; existing50Hzreference-only adapter found/customtrackingreward and noD435i recorded; teacher privileged inputs withheld from student; reference/action/clocks/ownWM replay boundaries explicit;0model0raw0SDK0GPU0remote0optimizer0GO;current276unchanged;alloldtags+lqrhead protected','--files',*selected,'--push'];recorder.main()
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'));assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())and all(remote.get(k)==v for k,v in remote_old.items())and git('ls-remote','origin','refs/heads/lqr').split()[0]==old_lqr
head=git('rev-parse','HEAD');obj=git('rev-parse','refs/tags/'+TAG);assert remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head and git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,tag=TAG,tag_object=obj,source_only=True,all_old_tags_and_lqr_branch_protected=True,indexed_files=len(rows),clean=True)))
