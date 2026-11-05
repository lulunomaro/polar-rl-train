from pathlib import Path
import hashlib,json,time

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200'
A=N/'newton_fudan_final620_1h/episode_reset04'
read=lambda p:json.loads(Path(p).read_bytes())
actual=read(A/'reports/FIRST_ACTUAL_RETURNED.json')['files']
first=actual['production/FIRST_UPDATED.json']
profile=read(N/'sampling_profile01/RESULT.json')
cached=read(N/'sampling_cached_profile03/RESULT.json')
parity=read(N/'sampling_scan_cache02/RESULT.json')
ppo=read(N/'reports/NEWTON_SCAN_CACHE_OVERFLOW_PPO09.json')
assert all(x['passed']for x in (profile,cached,parity,ppo))
rows=lambda j:[r for r in j['rows']if r['name']=='MOD4/scans' and r['cpu_us']>0]
rawlog=actual['WORKER.log']
report=dict(epoch=time.time(),kind='NEWTON_FIRST621_AND_LOCAL_SAMPLING_DIAGNOSIS',
    human_quote='为何step速度这么慢?我看其他的他们的人形机器人训练基本上都是十几万step美妙',
    current_production_first=first,
    collection_fraction=first['collection_seconds']/(first['collection_seconds']+first['learning_seconds']),
    control_samples_per_second=first['samples_per_second'],
    first_physics_world_steps_per_second_unit_conversion=first['samples_per_second']*8,
    different_counter_not_a_speedup=True,
    seconds_per480k_at100k=4.8,
    original_log={k:v for k,v in rawlog.items()if k!='text'},
    linesearch_warning_occurrences_in_first_return=rawlog['text'].count('linesearch iterations limit reached'),
    local_profile=dict(path=str(N/'sampling_profile01/RESULT.json'),
        gpu=profile['GPU'],num_envs=profile['num_envs'],controls=profile['controls'],
        scans=rows(profile),
        launches=next(r for r in profile['rows']if r['name']=='cudaLaunchKernel'),
        synchronizations=next(r for r in profile['rows']if r['name']=='cudaStreamSynchronize')),
    repair='Cache immutable scanner configuration/grid once at construction; identical grid/raycast/math. Replace per-world line-search GPU printf with cumulative native overflow-bit counts; solver iterations unchanged.',
    scan_parity=parity,
    local_full_step_before_seconds=profile['unprofiled_local_seconds'],
    local_full_step_after_seconds=cached['unprofiled_local_seconds'],
    local_full_step_ratio=profile['unprofiled_local_seconds']/cached['unprofiled_local_seconds'],
    postrepair_scan_profile=rows(cached),
    postrepair_actual_PPO4env=ppo,
    production_20k_postrepair_speed_not_measured=True,
    active_frozen_production_modified=False,SSH=0,production_PT_reads=0,
    current_collector=35288,
    pending=['At original fullsave/80/native review boundary measure candidate20k whole-round throughput',
             'Fuse400Hz acceptance/state/queue hotpath; original Warp path not yet enabled on direct Newton bridge',
             'Review true numerical resets and solver convergence before BPTT switch',
             'Finish finite SuperMimic worker/evaluator and full environment-stream continuation'],
    prior_local_reader_failures=[dict(path='N/test_newton_native.py',reason='Missing file; actual script is N/newton_smoke.py'),
        dict(path='CODE/jump200.py',reason='Shared module is bound by BINDINGS at import; no local duplicate')])
path=N/'reports/NEWTON_SAMPLING_SPEED_DIAGNOSIS.json'
with path.open('x',encoding='utf8')as f:json.dump(report,f,indent=2,ensure_ascii=False)
for p in [N.parents[1]/'admin/CURRENT_STATE.json',D/'WORK_ORDER.json']:
    state=read(p)
    state['sampling_speed_diagnosis']=dict(report=str(path),
        actual_first_control_steps_per_s=first['samples_per_second'],
        cache_and_overflow_reporting_repair_tested=True,
        local_unprofiled_ratio=report['local_full_step_ratio'],
        production_candidate_not_yet_measured=True,
        active_frozen_run_unchanged=True,
        next='After current fullsave/independent80/native review use tested cache/aggregate-reporting code in next saved-boundary segment; finish SuperMimic worker during PPO.')
    state['supermimic_interleaving']['legacy_mod4_200_rl_bptt']='Foreign ACTIVE automation; do not modify'
    p.write_text(json.dumps(state,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(dict(saved=str(path),local_ratio=report['local_full_step_ratio'],current_run_unchanged=True)))
