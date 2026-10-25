"""Unique actual75 training stage; original74 closure is an already committed ordinary supplement."""
from pathlib import Path
import json, time, tomllib, traceback

N=Path(__file__).resolve().parent; T=N.parent; W=T.parent; G=W/'polar-rl-train'; R=N/'reports'
P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V74B_20261026'
engine=T/'MOD4_SAMPLING_THROUGHPUT_OPTIMIZATION_PREPARATION_20261025/archive_current_implementation_and_MOE_preparation_stages_unique_once.py'
s=engine.read_text('utf8')
def patch(old,new):
    global s
    assert s.count(old)==1,old
    s=s.replace(old,new,1)
patch("'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation'", "'t2z':'mod4-whole-moe-rl-t2z-dual4090-preparation','stage75':'mod4-three4090-h1-sampled-leg-excess-v8-training75'")
patch("nr=(S if kind=='performance' else T/'MOD4_MOE_RL_T2Z_TRANSFER_PAPER_PREPARATION_20261025')/'reports'", "nr=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V75_20261026'/'reports'")
patch("TAG='trial-20261025-'+ID;D=G/('versions/20261025_'+ID)", "TAG='trial-20261026-'+ID;D=G/('versions/20261026_'+ID)")
patch("'--kind','diagnostic'", "'--kind','training'")
ns={'__name__':'archive75_utilities_only','__file__':str(engine)}
exec(compile(s,str(engine),'exec'),ns); git=ns['git']

def main():
    assert git('rev-parse','HEAD')=='3eec16b9764dc6d815920a0adbbd70b3c0521652'
    assert len(git('tag','--list').splitlines())==1446 and not git('status','--porcelain')
    first=json.loads((R/'THREE_EXPERT_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
    assert first['passed'] and first['actual_finite_returned'] and first['all_three_actual_GO_and_positive_PPO']
    assert first['H1_V8_sampled_excess_reward_and_original_success_standard']
    cpu=json.loads((R/'H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json').read_bytes())
    assert cpu['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested']
    assert cpu['sampling_acceleration_CPU']['V8_reward_publication_AST']['passed']
    proof=json.loads((P/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
    assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
    a=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
    assert a['prompt']==(R/'CURRENT_ACTUAL75_THREE4090_V8_MONITOR_SOURCE.txt').read_text('utf8')
    assert a['status']=='ACTIVE' and a['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
    for p in [G/'versions/20261026_mod4-three4090-qualified73b-continuation74-v8-preparation/COMPLETE_FILE_CAPTURE_INDEX.json',
              G/'versions/20261026_mod4-three4090-qualified73b-continuation74-v8-preparation/ordinary_closed74b_models_cost_saved_motion/ORDINARY_CAPTURE_INDEX.json']:
        ns['prior'](p)
    note='''Continue all three4090 cards on H1 step270, E2 world-moving and E3 recovery from the three actually complete74b checkpoints. H1 131/17Adam806120, E2 86/845140 and E3 84/845840 passed full twohost SHA, wholeCPU finite fullstate,17Adam x20, actor9 including sixSTD and critic8 allchanged,270phase and50Hz checks. Original singlewriter settled three actual intervals3620.5648260116577+3637.862925052643+3655.699939727783=10914.127690792084s; closed balance690339.4171483517. All normal duration flags true, ownprocesses/children out, original canonicalNone and locks free. Their closure and new saved-only74 replay are already an ordinary supplement to the consumed74 trial, not a repeated trial.

New actual75 installs the bounded H1 V8 training-only sampled-leg-action-excess reward, weight-.001, while retaining V5 delayed target-feasibility penalty-.05, V6A sagittalXZ tuck.22/1.7 and V7 near-edge gate. The existing preclip raw sample clone is temporarily exposed readonly during production vec.step under explicit learningflag, forwarding unchanged original actions and old_step output; finally clears rawreference and flag. Missing/invalid/nonfinite raw in active learning fails; nonlearning/native/frozen probes newregularizer0. No actor inputs, commands, clipping, PD, delay, PPO, optimizer, physics or success-standard changes. New sourceauth explicitly uses existing H1 repair authorization; exactweight approval was not fabricated. Historical V1..V5 candidate iterations and all original CPU refusals/pass reports remain in prior full captures.

This stage passed fresh installed actual SDK RewardManager.compute for the new term, sampler exact AST including original persistence/retention/error logic, fullsource RSL/17Adam CPU, original valid_ready and real after-copy resource guards. Then all three actualGO and firstcompletePPO updates passed, distinct expected4090 UUIDs and precise process identities verified. H1 original traceindex includes h1_step270_sampled_leg_action_excess and actual Task has V8recipe. This proves runtime registration and firstPPO, not a complete75 model, sustained utilization, equivalent long-run training or skill success. Current75 originalwriter fee remains pending. No training/SDK/GPU/policy/raw action for Git.

Closed74 saved48controls across20k contain271 takeoff increments,1043 recorded bothcrossed envframes, landing/recovery0. Selected noreset case13231 has takeoff and recordedcrossed with approximately.30239m reconstructed bothbottom peak and.29896m clearance at closestgap-.08439m; no proven topcontact/stable recovery. FINAL currently-retainedepisode21crossedenvs and zero landing/recovery/success are not wholewindow totals or frozen policy evaluation. Different selected scopes cannot establish causal V7/V8 learning improvement. Saved kinematics do not replace callback truth or introduce a new closure traininggate.

All exact source histories, receipts, reports and binder nonfatal backslash-S warnings are retained. Three-slot86412.86069250107 strict remainingguard and original canonical singlewriter,3900/3600save/300exit, physics2.5ms/TGS32/4 and original fullsave protections unchanged. No grant/refund/duplicatecharge/copiedcanonical/clearactive/secondwriter or oldonce replay. No subagents or automatic T2-z training. Existing hourly monitor updated with actual75 schedule, completion requirements and quiet-unless-meaningful behavior. Binary originals are retained and indexed only by realpath/bytes/existing producer SHA; no binary rehash/download for archival. This is one new actual stage, later supplements ordinary only.
'''
    ns['run_stage']('stage75',[N],[T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v117.py',engine],note,'Train three experts from closed74b with bounded H1 sampled-leg-excess V8 repair')

if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('ARCHIVE75_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(epoch=time.time(),error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),resume_existing_objects_if_record_started=True,no_repeated_record_tag_or_training=True),f,ensure_ascii=False,indent=2)
        raise
