from scut_wave_io import *
from datetime import datetime,timezone,timedelta

def main():
    b=json.loads((R/'WAVE_CANONICAL_ROOT_SEGMENTS_ACTUAL.json').read_bytes());rows=b['all_wave_named_completed_segments'];formal=[];pre=[]
    for x in rows:
        assert x['ended_epoch']==x['accounted_through_epoch'] and x['ended_epoch']>=x['started_epoch']
        v=dict(x,seconds=x['ended_epoch']-x['started_epoch'])
        (formal if '_observation_' in x['kind'] else pre).append(v)
    assert len(formal)==9 and len({x['log'] for x in formal})==9
    seconds=sum(x['seconds'] for x in formal);s35=sum(x['seconds'] for x in formal if 'WAVE50' not in x['log']);s50=seconds-s35
    first=min(x['started_epoch'] for x in formal);last=max(x['ended_epoch'] for x in formal);tz=timezone(timedelta(hours=8))
    v=dict(epoch=time.time(),passed=True,canonical_ref=str(R/'WAVE_CANONICAL_ROOT_SEGMENTS_ACTUAL.json'),canonical_SHA=b['canonical_SHA'],formal_unique_completed_segments=formal,formal_segments=9,formal_total_seconds=seconds,formal_35mm_seconds=s35,formal_50mm_seconds=s50,other_Wave_owned_PPO_preflight_or_failed_startup_segments=pre,other_charged_seconds=sum(x['seconds'] for x in pre),formal_clock_includes_load_learn_save_exit=True,not_pure_optimizer_compute_time=True,CPU_SDK_native_frozen_and_SCUT_noPPO_not_charged=True,first_formal_local=datetime.fromtimestamp(first,tz).isoformat(),latest_formal_exit_local=datetime.fromtimestamp(last,tz).isoformat(),elapsed_since_first_seconds=b['epoch']-first,elapsed_is_not_continuous_training=True,excludes_generic_ancestor129_mixed_terrain_training=True,does_not_claim_SCUT_author_training_duration=True,no_ledger_write_copy_tail_extension_recharge=True)
    save('WAVE_ACTUAL_TRAINING_DURATION_SUMMARY.json',v)
    print(json.dumps({k:v[k] for k in ('formal_segments','formal_total_seconds','formal_35mm_seconds','formal_50mm_seconds','other_charged_seconds','first_formal_local','latest_formal_exit_local','elapsed_since_first_seconds')}))

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE_DURATION_SUMMARY_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),CPU_only_no_budget_write=True));raise
