"""Publish actual closed results and audited repair handoff, without PT/physics."""
from pathlib import Path
from datetime import datetime,timezone
import ast,hashlib,importlib.util,json,os,time

N=Path(__file__).resolve().parent;A=N/'env20000_1h';R=A/'reports';S=N.parents[1]
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train');CODE=G/'project/isaac/mod4v1_scut'
D=G/'history/reviews/20261103-mod4v1-scut-native-training';Q=A/'action_clip_eval1'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v,exclusive=True):
    if exclusive:
        with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2)
    else:
        tmp=p.with_suffix(p.suffix+'.partial');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8',newline='\n');os.replace(tmp,p)
def identity(p):
    raw=p.read_bytes();return dict(path=str(p),bytes=len(raw),SHA=H(raw))

now=time.time();stamp=datetime.now(timezone.utc).isoformat()
spec=importlib.util.spec_from_file_location('repair_local_inventory',N/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=m.local_rows();other=[row for row in rows if row['ProcessId']!=os.getpid()]
local=dict(epoch=now,rows=rows,serialFREE=not other,read_only=True,new_SSH=0)
put(R/'COMPREHENSIVE_REPAIR_LOCAL_CIM.json',local)
tests=[]
for name in ('ACTION_TESTS','AUDIT_TESTS','STARTUP_TESTS','PARITY_TESTS','REVIEW_TESTS','VALIDATE'):
    p=R/f'FULL_REPAIR_{name}_ATTEMPT1.json';v=read(p);assert v['passed']
    tests.append(dict(identity(p),tests=v['tests'],passed=True))
assert sum(v['tests']for v in tests)==56
source=[]
for p in sorted(CODE.glob('*.py')):
    tree=ast.parse(p.read_bytes(),filename=str(p))
    source.append(dict(identity(p),git_path=p.relative_to(G).as_posix(),functions=[dict(name=n.name,line=n.lineno,end=n.end_lineno)
        for n in ast.walk(tree)if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]))
idx=read(Q/'SOURCE_FROZEN_REV3.json')
for row in idx['files']:
    actual=identity(Path(row['path']));assert actual['bytes']==row['bytes']and actual['SHA']==row['SHA']
    if row['relative'].endswith('.py'):ast.parse(Path(row['path']).read_bytes())
assert len({r['relative']for r in idx['files']})==len(idx['files'])
assert not(Q/'reports/LAUNCH_ONCE.json').exists()
source_index=dict(captured_at=stamp,files=source,diagnostic_index=identity(Q/'SOURCE_FROZEN_REV3.json'),
    test_reports=tests,CPU_tests=56,passed=True,production_PT_reads=0,physics=0,new_SSH=0)
put(D/'COMPREHENSIVE_REPAIR_SOURCE_INDEX.json',source_index)

registry=read(CODE/'SOURCES.json')['files']
base=Path(registry['base_env']['path']);lines=base.read_text(encoding='utf-8-sig').splitlines()
source_lines=[dict(line=i+1,text=t)for i,t in enumerate(lines)if any(x in t for x in
    ('def _debug_print_reward_and_state_stats','self._value_debug_step +=','self._value_debug_enabled =','self._value_debug_step > 10'))]
e0=Path('F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E0_MOD4V1_SOURCE_V1/runtime/isaac/mod4/train_mod4v1_e0.py')
e0lines=[dict(line=i+1,text=t)for i,t in enumerate(e0.read_text(encoding='utf-8-sig').splitlines())if 'clip_actions' in t]
def locations(file,names):
    row=next(v for v in source if Path(v['path']).name==file)
    return [dict(file=row['git_path'],**n)for n in row['functions']if n['name']in names]
delta=dict(captured_at=stamp,SCUT_commit='1a26356d6f591734d4f6f666f5cead1a6925da67',
    old_18540_line_alignment_preserved=True,not_whole_program_equivalence=True,
    source_debug_clock=dict(file=registry['base_env'],relevant_lines=source_lines),
    source_MOD4_clip=dict(identity(e0),relevant_lines=e0lines),
    fixes=[dict(id='F1',targets=locations('train.py',['step'])),
           dict(id='F2',targets=locations('rewards.py',['cache_raw_observations','_debug_print_reward_and_state_stats'])),
           dict(id='F3',targets=locations('sdk.py',['snapshot'])+locations('evaluate.py',['main'])),
           dict(id='F4',targets=locations('evaluate.py',['first_episode_contact_summary'])),
           dict(id='F5',targets=locations('course.py',['set_spawn_orientation'])+locations('sdk.py',['reset'])),
           dict(id='F6',targets=locations('checkpoint.py',['save','restore','restore_resized_learning']))])
put(D/'REPAIR_SOURCE_LINE_DELTA.json',delta)
issues=[
 dict(id='POSTROUND_DECODE',kind='reader_failure',detail='UnicodeDecodeError in original receiver; old failure report kept, repaired formal transfer complete'),
 dict(id='POSTROUND_NULL_WORKER',kind='reader_failure',detail='Nullable OWNER_CURRENT worker reader failure; old failure report kept, repaired formal transfer complete'),
 dict(id='CPU_MODEL_ATTEMPT1',kind='reader_failure',detail='Module sys.path failed before model load'),
 dict(id='CPU_MODEL_ATTEMPT2',kind='reader_failure',detail='NumPy2 numpy._core pickle incompatibility while reading actual final'),
 dict(id='CPU_MODEL_ATTEMPT3',kind='reader_failure',detail='Global alias attempt exited1 with no output; not a successful model decode'),
 dict(id='CPU_MODEL_ATTEMPT4',kind='reader_repair',detail='Scoped pickle.Unpickler remap numpy._core to numpy.core completed one successful diagnosis decode; source unchanged'),
 dict(id='BROAD_READER_PATHS',kind='reader_failure',detail='Guessed initialize.py, integration_tests.py, staged E0 mod4_task/mild_dr, local A/owner.py and gaussian.py were absent; corrected from rg/dependency registry; no mutation'),
 dict(id='WORKFLOW_FILENAME',kind='reader_failure',detail='NEXT_AI_WORKFLOW.md absent; actual AGENTS linked NEXT_AI_GIT_WORKFLOW.md read'),
 dict(id='POWERSHELL_GLOB',kind='reader_failure',detail='Bash-style brace path parsed as PowerShell error; later literal rg wildcard also failed; corrected rg directory with -g'),
 dict(id='JSON_CASE_KEYS',kind='reader_failure',detail='PowerShell ConvertFrom-Json rejected GO/go keys; reread with AsHashtable/Python, source unchanged'),
 dict(id='OUTPUT_BOUNDS',kind='reader_failure',detail='Several combined outputs truncated; inspected bounded required source sections instead; no experiment rerun'),
 dict(id='DIAGNOSTIC_UNUSED_REVISIONS',kind='prepared_not_launched',detail='REV1 superseded by complete audit REV2 then human lightGPU permission REV3; same namespace, all original indices preserved, no once consumed'),
 dict(id='RAW_GATE_CAUSAL_CORRECTION',kind='subsequent_finding',detail='F2 debug clock omitted from first clip-only diagnosis; append correction, do not overwrite original report or claim all early deaths solely caused by missing clip'),
]
put(R/'COMPREHENSIVE_REPAIR_ISSUES.json',dict(captured_at=stamp,issues=issues,preserved_originals=True))

returned=read(R/'POSTROUND_FULL_RETURNED.json')['files'];closed=read(R/'POSTROUND_COMPLETED.json')
diagnosis=read(R/'ACTUAL20000_ACTION_FAILURE_CPU.json')
peerroot=Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103');peer=read(peerroot/'CURRENT_WORK_ORDER.json')
peerstatus=read(peerroot/peer['latest_status'])
blocker=dict(local=local,peer_run=peer['run_id'],peer_snapshot=identity(peerroot/peer['latest_status']),
    peer_snapshot_epoch=peerstatus['epoch'],original_GO=peerstatus['files']['GO_PRODUCTION.json'],
    original_identity=peerstatus['files']['OWNER_STARTED.json']['identity'],snapshot_not_live_free=True,
    actual_read_only_local_no_new_SSH=True)
cpu=dict(total_tests=56,passed=True,reports=tests,production_PT_reads=0,physics=0,GPU_training=0,
    actual_final_CPU_diagnosis_separate=str(R/'ACTUAL20000_ACTION_FAILURE_CPU.json'))
nextstep='Read current exact controllers locally. When serialfree and peer ownwaited/settled/released, run the unused REV3 same-final finite diagnostic via action_clip_eval.py run. Check ownreceipt/once first. Inspect all80/pre-reset reasons/manifold and render stored poses for native review, then decide source recovery or actual20000 PPO continuation; never replay closed run.'
work=read(D/'WORK_ORDER.json')
work.update(captured_at=stamp,status='ACTUAL20000_CLOSED_FAILED_REPAIR_CPU56_NATIVE_PENDING',
    human_latest='全面检查是否还有其他问题别再出问题修了；如果卡上有有占用但占用不大可以直接用',
    training_configuration='20000 environments, one-hour window; original request retained',
    final=closed['final'],independent_evaluation=closed['actual_result'],
    owner_exit=diagnosis['owner_exit'],local_controller=None,training_completed=True,
    trained_skill=False,strict_successes=0,actual_samples=diagnosis['actual_samples'],
    evaluation_completed=True,native_pose_visual_review=diagnosis['native_visual_review'],
    full_restore_CPU_diagnosis=diagnosis['CPU'],repair_report=str(D/'COMPREHENSIVE_REPAIR.md'),
    current_source_index=str(D/'COMPREHENSIVE_REPAIR_SOURCE_INDEX.json'),
    source_line_delta=str(D/'REPAIR_SOURCE_LINE_DELTA.json'),CPU_validation=cpu,
    diagnostic=dict(root=str(Q),plan=identity(Q/'PLAN_REV3.json'),index=identity(Q/'SOURCE_FROZEN_REV3.json'),
        entry=str(N/'action_clip_eval.py')+' run',launched=False,once_consumed=False,
        model_source=closed['final']['checkpoint'],optimizer_operations=0,ledger_writes=0),
    resource_blocker=blocker,GPU_policy=read(Q/'PLAN_REV3.json')['resource_policy'],
    human_light_gpu_occupancy_authorized=True,next=nextstep,
    git='ordinary supplement to existing native phase; no record/retag; exact commit verified in tool output')
work['independent_evaluation']['native_pose_visual_review_pending']=False
work['closed80']['independent_evaluation']['native_pose_visual_review_pending']=False
work['consumed']=list(dict.fromkeys(work['consumed']+['POSTROUND_FINITE_READ','POSTROUND_READER_RECOVERY','POSTROUND_READER_NULL_FIX2','FORMAL_RETURN','INDEPENDENT_EVAL']))
work['actual_issues']+=issues
put(D/'WORK_ORDER.json',work,False)
statepath=S/'admin/CURRENT_STATE.json';state=read(statepath)
state.update(epoch=now,human_latest_request=work['human_latest'],current_training=work['status'],
    current_work_order=str(D/'WORK_ORDER.json'),read_next=str(D/'WORK_ORDER.json'),next=nextstep,
    mod4v1_scut_native_20000_1h=work,
    boundaries='EnhancedMOD4v1 explicitUSD/fullD0-D7/400N2000damping3/.0025TGS32-4/50-100-400/.01closure&mimic/strict270. Single originalcanonical; lightGPU occupancy authorized subject measured capacity and original locks. No oldonce replay; nativevision only.')
state['scut_mod4v1_adaptation'].update(status='ACTUAL20000_CLOSED_REPAIR_CPU56_NATIVE_PENDING',
    latest_validation='56 current repair CPU checks pass; old source native failed0/80; current repair native pending',
    next=nextstep,read_next=str(D/'WORK_ORDER.json'))
put(statepath,state,False)
put(R/'COMPREHENSIVE_REPAIR_DECISION.json',dict(captured_at=stamp,status=work['status'],
    fixes=['F1_action_clip','F2_source_debug_clock','F3_pre_reset_diagnostics','F4_first_episode_force','F5_spawn_yaw','F6_checkpoint_counters'],
    CPU=cpu,resource_blocker=blocker,diagnostic=work['diagnostic'],next=nextstep,new_SSH=0,newphysics=0))
print(json.dumps(dict(status=work['status'],CPU_tests=56,source_files=len(source),local_other_controllers=len(other),
    work_order=str(D/'WORK_ORDER.json'),checkpoint_reads_for_handoff=0,physics=0)))
