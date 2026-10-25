"""One actual quantized-only stage record; use previous verified archive engine."""
from pathlib import Path
import hashlib,json,sys,time,traceback
Q=Path(__file__).resolve().parent;T=Q.parent;W=T.parent;G=W/'polar-rl-train';R=Q/'reports'
try:
    engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py'
    original=engine.read_text('utf8')
    needle="'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'"
    assert original.count(needle)==1
    source=original.replace(needle,needle+",'quantized':'mod4-single4090-quantized-wan5b-preparation'")
    needle="nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'"
    assert source.count(needle)==1
    source=source.replace(needle,"nr=T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025/reports'")
    ns={'__name__':'reviewed_quant_archive_engine','__file__':str(engine)};exec(compile(source,str(engine),'exec'),ns)
    git=ns['git'];assert git('rev-parse','HEAD')=='60645bb899db0064c3ebde604db13419ec084af8' and len(git('tag','--list').splitlines())==1439 and not git('status','--porcelain')
    # Previous stages are already verified full captures. This new root has no
    # historical duplicate files; do not reread the entire140k-entry history.
    for path in [G/'versions/20261025_mod4-post67-v6a-sampling-acceleration-implementation/COMPLETE_FILE_CAPTURE_INDEX.json',G/'versions/20261025_mod4-whole-moe-rl-t2z-dual4090-preparation/COMPLETE_FILE_CAPTURE_INDEX.json']:
        ns['prior_descriptors'].append(dict(path=path.relative_to(G).as_posix(),SHA=hashlib.sha256(path.read_bytes()).hexdigest(),existing_full_capture_already_verified=True))
    results=[json.loads(p.read_bytes()) for p in R.glob('Q8_WINDOWS_MEMORY_RELAY_*_RETURNED_ACTUAL.json')]
    results += [v['download_result'] for p in R.glob('SINGLE4090_Q8_BATCH_*_RETURNED_ACTUAL.json') if isinstance((v:=json.loads(p.read_bytes())).get('download_result'),dict)]
    complete=[x for x in results if x.get('status')=='COMPLETE_FULL_SHA_AND_GGUF_HEADER_VERIFIED']
    assert len(complete)==1 and complete[0]['actual_bytes']==5400179040 and complete[0]['producer_SHA']=='57bece983817ab2f957546683bb670f13be7d99022d45674840cd999a050ea8f'
    n68=T/'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025'
    extras=[T/'H1_STEP270_REWARD_PATH_V1_20261022'/('same_authorized_session_compressed_transport_v'+str(i)+'.py') for i in range(77,84)]
    extras += [n68/'read_current68_owner_H1_original_account_after_network_retry_once.py',*sorted((n68/'reports').glob('HUMAN_REQUESTED_CURRENT68_RECONNECT_*.json'))]
    ns['run_stage']('quantized',[Q],extras,
        'Human narrowed the world-model preparation to one quantized backbone for a single24GB4090. The old13-file44.253GB full-weight download is cancelled. Only Wan2.2-TI2V-5B-Q8_0.gguf is obtained, pinned to QuantStack revision57437632ddd08bdcbd1508c866aa22e126ed51d2. Its5,400,179,040 bytes, complete official SHA256 and GGUF header are actually verified on host72. No local duplicate weight, other quant variant, fullT5 or unquantized BWM checkpoint was downloaded in this stage.\n\nPrimary model/source metadata, direct-host timeout and fallback memory-relay results are retained. A synthetic CPU test proves input/latent gradients for frozen Q8_0 linear math, but does not establish fullWan/T2-z GGUF integration, real MoE action conditioning, single4090 peakVRAM, physical skill or paper result. This is a quantized visual base, distinct from a trained action-conditioned BWM checkpoint. No model GPUload, new rollout, training or canonical accounting change. All current subagents finished; no further delegation until human reauthorizes.\n',
        'Prepare one verified Q8 Wan5B backbone for single4090 MoE T2-z research')
except BaseException:
    with (R/('QUANTIZED_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),resume_existing_objects_only_no_repeated_record_or_tag=True),f,indent=2)
    raise
