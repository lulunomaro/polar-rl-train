from pathlib import Path
import json,time

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200'
P=N/'newton_fudan_final620_1h/episode_reset04';A=N/'supermimic_final881_1h'
read=lambda p:json.loads(Path(p).read_bytes())
review=read(P/'reports/NEWTON_CLOSED_LEARNER_AND_ALL80.json')
actual=read(P/'reports/LOCAL_COMPLETE_RETURNED.json')['files']
native=read(P/'reports/ACTUAL_NATIVE_REVIEW.json')
stable=read(N/'constraint400hz_8sec_final881_04/RESULT.json')
bptt=read(N/'supermimic_constraint400hz07/RESULT.json')
assert stable['numerical_resets']==0 and stable['peak']['root_speed']<2 and bptt['passed']
report=dict(epoch=time.time(),status='FINAL881_CLOSED_NATIVE_REVIEW_AND_SUPERMIMIC_LAUNCH_PENDING_FIRST',
    source_final=review['checkpoint'],learning=review,
    old_owner_release=actual['OWNER_EXIT.json'],native_review=native,
    speed=dict(logger_hourly_arithmetic_mean=review['timings']['Steps per second']['mean'],
        last=review['timings']['Steps per second']['last'],
        aggregate_samples_over_collection_plus_learn=480000/(review['timings']['Collection time']['mean']+review['timings']['Learning time']['mean']),
        samples=125280000,PPO_updates=261),
    original_400Hz_failures_preserved=True,
    failed_solver_candidates=[dict(path=str(N/name/'RESULT.json'),numerical_or_divergence_remains=True)
        for name in ['solver_ls64_final881_01','solver_ls64_iter128_final881_02']],
    actual_repair='Apply the existing10mm closure and.01rad mimic episode reset at400Hz before subsequent solver steps; zero bad-contact sensor result and mask acceptance/reward/replay for the invalid control. Keep .0025/32Newton/15LS and model/DR/reward unchanged.',
    repaired_full8sec_test=dict(path=str(N/'constraint400hz_8sec_final881_04/RESULT.json'),
        numerical_resets=0,constraint_resets=stable['constraint_resets'],peak=stable['peak']),
    BPTT_after_constraint_repair=dict(path=str(N/'supermimic_constraint400hz07/RESULT.json'),passed=True),
    current_root=str(A),plan=read(A/'PLAN.json'),controller=read(A/'reports/LAUNCH_EXACT_CIM.json'),
    actual_LAUNCH_ONCE=(A/'reports/LAUNCH_ONCE.json').exists(),
    FIRST_BPTT_verified=False,production_switch_qualified=False,
    return_size_issue='Immutable original1.598GB return contains1.397GB complete WORKER log; streamed unchanged into SHA-verified local log files. Full metadata and complete review retained; huge raw/log are indexed by actualpathbytesSHA.',
    local_reader_failure=dict(script='compact_newton_return.py',error='Last item boundary assumed LF but actual fullreturn uses CRLF; preserved original then corrected CRLF-aware boundary, reused already SHA-verified local log exports;0newSSH'),
    next='Only exact48636local/FIRST/error. Original newowner verifies actual20k H32fullsave and binds sole. No secondcontroller/SSH or hotpatch. Real GO/SAVE come from FIRST receipt, not launch time.')
with(N/'reports/FINAL881_AND_SUPERMIMIC_LAUNCH.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
for p in [N.parents[1]/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json']:
    value=read(p)
    value.update(epoch=time.time(),current_training=report['status'],current_training_root=str(A),
        current_training_remote=report['plan']['remote_root'],local_controller=report['controller'],next=report['next'])
    value['newton_migration'].update(status=report['status'],current_root=str(A),
        current_remote=report['plan']['remote_root'],source_iteration=881,
        source_SHA=review['checkpoint']['SHA'],FIRST_pending=True,
        previous_final881=dict(PPO_updates=261,successes=0,numerical_resets=1824,
            loggermeanstep_s=review['timings']['Steps per second']['mean'],ownclosed=True,native_reviewed=True))
    value['supermimic_interleaving'].update(production_worker_pending=False,
        actual_launch_pending_FIRST=True,current_root=str(A),production_switch_ready=False,
        constraint400Hz_repair_test_passed=True,
        next='Actual20k H32 BPTT FIRST/fullsave then sole collection; do not claim skill or Newton numerical cleanliness from old flags')
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(dict(saved=True,source881=True,newlocalcontroller=48636,FIRST_pending=True)))
