"""Describe new76 saved samples and actual V8 scalar contributions; no model or new rollout."""
from pathlib import Path
import json,time,traceback
import numpy as np
S=Path(__file__).resolve().parent;R=S/'reports'
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
    source=json.loads((R/'CLOSED77_RECORDED_MOTION_SOURCE_CPU_ACTUAL.json').read_bytes())
    name='h1_step270_sampled_leg_action_excess';idx=source['reward_terms'].index(name)
    with np.load(S/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False) as z:
        raw=z['raw_sampled6'];executed=z['executed6'];actual=z['reward_term_contribution'][:,:,idx]
        assert raw.shape==executed.shape and raw.shape[-1]==6 and np.isfinite(raw).all() and np.isfinite(actual).all()
        cost=np.square(np.maximum(np.abs(raw[:,:,:4])-np.float32(6),np.float32(0))).mean(-1,dtype=np.float32)
        expected=cost*np.float32(-.001)*np.float32(.01)
        error=np.abs(actual-expected)
        same=np.isclose(actual,expected,rtol=3e-5,atol=1e-7)
        def describe(mask):
            a=raw[mask];b=actual[mask]
            if not len(a):return dict(envframes=0)
            return dict(envframes=len(a),raw_abs_ge6_fraction_per_action=(np.abs(a)>=6).mean(0).tolist(),
                        raw_abs_max=float(np.abs(a).max()),actual_V8_nonzero_fraction=float((b!=0).mean()),
                        actual_V8_contribution_mean=float(b.mean(dtype=np.float64)),actual_V8_contribution_sum=float(b.sum(dtype=np.float64)),
                        actual_V8_min=float(b.min()),actual_V8_max=float(b.max()))
        allmask=np.ones(raw.shape[:2],dtype=bool);continuous=np.broadcast_to(z['continuous_no_reset'],allmask.shape)
        result=dict(epoch=time.time(),scope=source['scope'],selected_cases=raw.shape[1],frames=raw.shape[0],
                    all_selected=describe(allmask),continuous_selected=describe(continuous),
                    original_executed_actions_exact_clip_raw6=bool(np.array_equal(executed,np.clip(raw,-6,6))),
                    actual_reward_term=name,weight=-.001,control_dt=.01,
                    formula_comparison_max_abs_error=float(error.max()),formula_comparison_matching_fraction=float(same.mean()),
                    formula_consistent_all_selected=bool(same.all()),
                    original_SDK_step_reward_is_rate_and_trace_uses_actual_control_dt_scale=True,
                    full20k_new48_requested_clip_fractions=source['full20k_requested_raw_abs_ge6_fraction'],
                    full20k_new48_tuck_paid_clip_fractions=source['full20k_tuck_paid_raw_abs_ge6_fraction'],
                    full20k_new48_actual_V8_contribution=source['actual_weighted_reward_contributions'][name],
                    not_whole_training_window_or_matched_cohort_causal_learning_gain=True,
                    descriptive_only_not_new_training_or_skill_gate=True,no_policy_PhysX_GPU_remote_or_account_write=True)
    put('CLOSED77_ACTUAL_V8_CONTRIBUTION_AND_SELECTED_CLIPPING_CPU_ACTUAL.json',result)
    print(json.dumps({k:result[k] for k in ('all_selected','continuous_selected','original_executed_actions_exact_clip_raw6','formula_comparison_max_abs_error','formula_consistent_all_selected','full20k_new48_actual_V8_contribution')}))
except BaseException:
    put('CLOSED77_SELECTED_V8_READER_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_replay=True));raise
