"""Adapt only producer provenance before the unchanged full original N80 materializer."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent;target=D/'stage_fudan_fresh1cd_frozen_original_once.py';assert not target.exists()
s=(D/'stage_fudan_timeout8_frozen_original_once.py').read_text(encoding='utf8')
s=s.replace('FDN_FULL_LEARNER_CONTINUATION_FRESH_N20000_TIMEOUT8_ENV','FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8').replace('fdn_n20000_full_learner_timeout8_source','fdn_fresh_mlp_warm_1cd_n20000_timeout8').replace('FDNTIMEOUT8_FROZEN_','FDNFRESH1CD_FROZEN_').replace('source_fudan_frozen_native_eval_v3_timeout8','source_fudan_frozen_native_eval_v4_fresh1cd_timeout8').replace('source_fudan_frozen_parent_v3_timeout8','source_fudan_frozen_parent_v4_fresh1cd_timeout8')
a='BASE = dict(updates=133, policy_optimizer_steps=2660,\n            encoder_optimizer_steps=2660, transitions_seen=78822912)';assert s.count(a)==1;s=s.replace(a,'BASE = dict(updates=0, policy_optimizer_steps=0, encoder_optimizer_steps=0, transitions_seen=0)')
s=s.replace('["version"] == 3','["version"] == 4').replace('Qualified version3 timeout8 E3 full save required','Qualified version4 fresh1cd E3 full save required').replace('SINGLE_GPU_E3_FDN_TIMEOUT8_ORIGINAL_FRESH80_FROZEN_EVALUATION_PLAN','SINGLE_GPU_E3_FDN_FRESH1CD_ORIGINAL_FRESH80_FROZEN_EVALUATION_PLAN')
a='intent["parent_pid"] == f["parent_pid"]';assert s.count(a)==1;s=s.replace(a,'f["resource_binding"]["actual_parent_pid"] == f["parent_pid"]')
a=s.index('    base, window, counters =');b=s.index('    selected = dict(',a)
front='''    base, window, counters = f["base_counters"], f["window_counters"], f["counters"]
    need(base == BASE and window == counters and set(counters) == set(BASE) and
         all(type(counters[k]) is int and counters[k] >= 0 for k in COUNTERS),
         "Fresh zero-base, window-only counters required")
    wu = counters["updates"]
    need(0 < wu <= 25 and counters["policy_optimizer_steps"] == counters["encoder_optimizer_steps"] == 20 * wu and
         counters["transitions_seen"] == 48 * 20000 * wu, "Positive actual finite25 N20000 learning required")
    source_receipt = f["source_checkpoint"]
    need(source_receipt == latest["source_checkpoint"] == intent["source_checkpoint"] and
         source_receipt["source_sha256"] == MOTHER_SHA and source_receipt["source_bytes"] == 14715029 and
         source_receipt["source_iter"] == 43090 and source_receipt["physical_byte_opens"] ==
         source_receipt["SHA_calculations"] == source_receipt["CPU_decodes"] == latest["original_mother_reads"] == 1 and
         all(source_receipt[k] is True for k in ("whole_source_root_and_bytes_retained", "source_tensor_versions_unchanged",
             "actor_critic_MLP_only", "source_optimizer_and_DR_state_not_restored", "old_iteration_not_inherited")),
         "Actual single1cd MLP-only warm receipt and retained source required")
    init, update = m["FDN_SINGLE_SOURCE_NEW_BRANCH_WARM_START.json"], m["FDN_NATIVE_UPDATE.json"]
    need(init["version"] == 4 and init["fresh_envs"] == 20000 and init["initial_counters"] == BASE and
         init["source_checkpoint"] == source_receipt and init["history_initialized_from_new_returned_raw35_repeated_five"] is True and
         init["source_global_RNG_environment_DR_history_queues_or_pending_applied"] is False and
         update["rollout_N"] == 20000 and update["rollout_T"] == 48 and update["actual_native_training_update"] is True and
         update["base_counters"] == BASE and update["window_counters"] == update["counters"] == counters,
         "Actual fresh initialized/trained N20000 and T48 required")
    native = f["native_counters"]
    c = native["actual_native_policy_steps"]
    need(type(c) is int and c > 0 and f["native_counters_scope"] == "CURRENT_N20000_WINDOW_ONLY" and
         native["actual_native_transitions"] == 20000 * c and native["physical_callbacks"] == 8 * c and
         native["feedback_callbacks"] == 2 * c and native["termination_computations"] == c and
         0 <= c - 48 * wu <= 48, "Current N20000 native clocks/unoptimized partial differ")
    for item in (f, latest, intent):
        need(item["source_kind"] == SOURCE_KIND and item["base_counters"] == BASE and item["window_counters"] == counters and
             item["num_envs"] == 20000 and item["inherited_old_iterations"] == 0 and item["full_learner_resume"] is False and
             item["bad_candidate_reads"] == 0 and item["task_runtime_overlay"] == f["task_runtime_overlay"],
             "All fresh producer/save/intent provenance must match")
    need(latest["counters"] == counters and latest["native_counters"] == native and
         latest["native_counters_scope"] == "CURRENT_N20000_WINDOW_ONLY" and
         f["task_runtime_overlay"]["bytes"] == 8571 and f["task_runtime_overlay"]["sha256"] == OVERLAY_SHA,
         "Latest full state/current native/unchanged fixed timeout8 metadata required")
'''
s=s[:a]+front+s[b:]
a='selected["sha256"] not in (MOTHER_SHA, SOURCE_4K_SHA, LEARNER_SHA)';assert s.count(a)==1;s=s.replace(a,'selected["sha256"] not in (MOTHER_SHA, SOURCE_4K_SHA, LEARNER_SHA, "3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e")')
ast.parse(s);compile(s,str(target),'exec');target.write_text(s,encoding='utf8',newline='\n')
print('Created fresh1cd closed frontdoor + unchanged original full N80 materializer; source-only AST; no stage/SDK/models/SSH/GPU/C')
