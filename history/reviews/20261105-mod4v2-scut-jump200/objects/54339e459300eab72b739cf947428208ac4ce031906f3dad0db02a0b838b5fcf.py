"""Record measured source comparison and saved-boundary execution choice."""
from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
D=G/'history/reviews/20261105-mod4v2-scut-jump200';S=N.parents[1]
read=lambda p:json.loads(Path(p).read_bytes())
benchmark=read(N/'sampling_scripted_isolated_ABBA11/RESULT.json')
assert benchmark['passed']and read(N/'reports/SAMPLING_SCRIPTED_FULL_RESUME_TEST.json')['passed']
sources=[]
for p in (N/'sampling_official_sources').glob('*.py'):
    raw=p.read_bytes();sources.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
profile=read(N/'sampling_total_profile05/RESULT.json')
rows=[r for r in profile['rows']if r['cpu_us']and r['name'].startswith(('TOTAL/','DETAIL/'))]
report=dict(epoch=time.time(),human_request='怎么速度这么慢?优化采样，看看官方采样流程',
    requested_metric='real control samples / full collect+WM4+aux4+H32+critic4 wall time',
    official_repository='https://github.com/PoplarCrystal/basic_loco_lib',
    official_commit='e4181af587330d0b70ca72e0d36b49be32e12a65',official_sources=sources,
    official_findings=['MimicWM replay is device-resident and CUDA Adam fused=True',
        'Official train loop measures collection and learning with synchronization',
        'Warp MDP and pre-reset physical endpoint capture; no reset poses as WM targets',
        'Current official analytic mimic task is distinct from MOD4 learned Fudan reward/context heads'],
    current_difference='CPU fullreplay retained because actual20k GPU replay previously OOM; measured transfer is minor in local profile, not presumed main bottleneck',
    local_profile=dict(path=str(N/'sampling_total_profile05/RESULT.json'),rows=rows,
        cudaLaunchKernel_count=73281,cudaStreamSynchronize_count=2670,
        local_num_envs=128,production_dimensions=True,production20k_throughput_claim=False),
    implementation=['Warp fused400Hz sixclosure/fourmimic checks, same .01m/.01rad reset boundary',
        'Warp fused400Hz acceptance with original physical_valid mask and all counters',
        'Reuse parity-tested Fudan16 kernel at50Hz with same termclip/dt/commandtail',
        'Four existing Adam instances use fused execution; state moments/steps/hooks retained',
        'TorchScript pure learned-model geometry, fp32 unchanged, output and gradient parity',
        'Explicit per-round and window control sample throughput; worker elapsed includes init and checkpoint overhead'],
    baseline=benchmark['totals']['A'],candidate=benchmark['totals']['B'],
    total_speed_ratio=benchmark['total_speed_ratio'],collection_speed_ratio=benchmark['collection_speed_ratio'],
    benchmark_protocol='ABBA128env, same saved learner/4Adam/replay/RNG before each arm, original geometry restored in both A arms, 2/3controls and4WM4auxH32critic4 every round',
    benchmark_variation='A1 9.862s, B1 6.281s, B2 5.927s, A2 7.766s per4rounds; laptop walltime variation exists; report aggregate and raw arms, not server4090 throughput',
    production20k_speed_not_yet_measured=True,GPU=benchmark['GPU'],
    parity=read(N/'sampling_fusion_parity06/RESULT.json'),
    geometry_parity=read(N/'reports/SCRIPTED_GEOMETRY_OUTPUT_GRADIENT_PARITY.json'),
    integrated_full_resume=read(N/'reports/SAMPLING_SCRIPTED_FULL_RESUME_TEST.json'),
    actual_CLI=read(N/'sampling_optimized_cli14/RESULT.json'),
    prior_sampling_only_total_speed_ratio=read(N/'sampling_total_ABBA07/RESULT.json')['total_speed_ratio'],
    failed_and_nonfinal_attempts=[
        dict(path=str(N/'sampling_scripted_ABBA09/RESULT.json'),kind='Benchmark harness variable collision original became tuple; no production change'),
        dict(path=str(N/'sampling_scripted_ABBA10/RESULT.json'),kind='Exploratory only: final A retained scripted geometry. Replaced by isolatedABBA11, raw preserved'),
        dict(path=str(N/'sampling_optimized_cli13/FINAL.json'),kind='CLI warmup-only1->2;0newBPTT. Corrected by newrandomfixture schedule32->33 CLI14, actual1newH32/fullsave/close'),
        dict(kind='Read-only source discovery GitHub API rate-limit, raw.githubusercontent exactcommit read succeeded; PowerShell JSON GO/go case collision fixed AsHashtable; missing optional paths not executed')],
    production_PT_reads=0,SSH=0,active_run_modified=False,
    active_root=str(N/'supermimic_first1941_reboot_periodic_1h'),sole_collector=79388,
    next='After current originalfinal/fullsave/release/80/all4native review use prepare_sampling_continuation.py. New source is actualfinal all4Adam/replay/RNG, frozen references and small overlay; run20k and report total throughput. No hotpatch or duplicate reader.',
    deployment_status='LOCAL_VALIDATED_SAVED_BOUNDARY_READY_NOT_ACTIVE',
    constraints_unchanged=['HW300N60','Fudan16','400/100/50Hz','.0025Newton32LS15','fullD0-D7',
        'residual.25','learnedWM H32','fourAdam updatecounts','fullreplay64x20k','hour3600+300','100h ceiling','independent80 native playback'],
    state_read_fusion_enabled=False,old_rejected_fullstep093014_preserved=True)
(N/'reports/SAMPLING_OFFICIAL_OPTIMIZATION.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
brief={k:report[k]for k in ('epoch','human_request','requested_metric','official_commit','total_speed_ratio',
    'collection_speed_ratio','production20k_speed_not_yet_measured','deployment_status','active_root','sole_collector','next')}
brief.update(report=str(N/'reports/SAMPLING_OFFICIAL_OPTIMIZATION.json'),
    full_resume_passed=True,geometry_gradient_parity_passed=True,active_frozen_unchanged=True)
for p in (D/'WORK_ORDER.json',S/'admin/CURRENT_STATE.json'):
    value=read(p);value['sampling_optimization_20261106']=brief
    p.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(brief,ensure_ascii=False))
