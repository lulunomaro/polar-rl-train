"""Deterministic synthetic contracts; no original task, model or RNG execution."""
from __future__ import annotations
import ast
import copy
import datetime
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
import phase1_contract as c

HERE = Path(__file__).resolve().parent
SCHEMA = c.load_schema()


def sensor_pair(delay=1, episode=3):
    samples = []
    for i,tick in enumerate((11,12)):
        sample = {"physics_tick":tick*4,"sample_tick":tick,"episode":episode,"channels":{}}
        for name,spec in SCHEMA["sensor_channels"].items():
            width = spec["width"]
            clean = [(.05*(j+1) + i*.2) for j in range(width)]
            noise = [(1 if j%2 == 0 else -1)*spec["noise_uniform_bound"]/2 for j in range(width)]
            bias = [.003 if name == "leg_pos" else 0 for _ in range(width)]
            noisy = [x+n+b for x,n,b in zip(clean,noise,bias)]
            previous = samples[-1]["channels"][name] if samples else None
            old = tick-1 if previous else -1
            prev_cur = previous["cur"] if previous else [0]*width
            out = prev_cur if previous and delay else noisy
            selected_tick = old if previous and delay else tick
            sample["channels"][name] = {"profile":"noise_bias_mild_v1","clean_at_sample":clean,"noise_used":noise,
                "episode_bias":bias,"noisy_before_queue":noisy,"cur":list(noisy),"out":list(out),"previous_cur":list(prev_cur),
                "previous_last":old,"last":tick,"ready":bool(previous),"delay_steps":delay,"selected_sample_tick":selected_tick,
                "actual_age_us":(tick-selected_tick)*10000,"actor_stored":[x*spec["manager_scale"] for x in out],
                "draw_count_before":i*4,"draw_count_after":(i+1)*4,"due_environment_count":4,
                "noise_cache_last_after":tick,"probe_rng_before":"fixture-no-RNG-called","probe_rng_after":"fixture-no-RNG-called"}
        samples.append(sample)
    return samples


def action_trace(legs_lag=2, wheels_lag=1, start=40):
    result = {}
    for group,width in SCHEMA["action_groups"].items():
        lag = legs_lag if group == "legs" else wheels_lag
        neutral = [.01*(i+1) for i in range(width)]
        target = [.15*(i+1) for i in range(width)]
        before = {"lag_steps":lag,"episode":3,"pending":list(neutral),"pending_valid":False,
            "issued_tick":-1,"due_tick":-1,"applied":list(neutral),"applied_valid":False,
            "applied_issue_tick":-1,"first_apply_tick":-1,"last_submit_tick":-1,"last_apply_tick":start-1}
        frames = []
        for i in range(8):
            tick = start+i; fresh = i >= lag
            q = {"lag_steps":lag,"episode":3,"pending":list(target),"pending_valid":not fresh,
                "issued_tick":start,"due_tick":start+lag,"applied":list(target if fresh else neutral),"applied_valid":fresh,
                "applied_issue_tick":start if fresh else -1,"first_apply_tick":start+lag if fresh else -1,
                "last_submit_tick":start,"last_apply_tick":tick}
            frames.append({"queue":q,"first_transition_delay_us":lag*2500 if fresh else -1,
                "held_command_sample_age_us":i*2500 if fresh else -1,"articulation_target_readback":list(q["applied"])})
        result[group] = {"before_submit":before,"submitted_target":target,"apply_frames":frames}
    return result


def named_context(role):
    return {f["name"]:[.1*(i+1) for i in range(f["width"])] for f in SCHEMA["layouts"][role]["fields"]}


def static_capture(role="E3"):
    state = {"episode":3}
    for f in SCHEMA["layouts"][role]["fields"]:
        if "STATIC_DR" in f["classes"]:state[f["name"]] = [1]*f["width"]
    state.update(mild_motor_episode_scale_legs=[1]*4,mild_motor_episode_scale_wheels=[1]*2,
                 wheel_mu=[.9],mild_nominal=[0],sensor_leg_encoder_bias=[.003]*4)
    return state


class Contracts(unittest.TestCase):
    def test_schema_all_eight_exact_dimensions(self):
        result = c.validate_schema(SCHEMA)
        self.assertFalse(result["exact"])
        self.assertEqual({r:v["context_dim"] for r,v in SCHEMA["layouts"].items()}, c.ROLES)

    def test_source_manifest_identity(self):
        result = c.verify_local_schema_manifest()
        self.assertEqual(result["source_count"],202)
        self.assertFalse(result["actual_sdk_pass"])

    def test_allowlisted_source_hashes_still_match(self):
        manifest = json.loads((HERE/"source_manifest.json").read_text(encoding="utf-8"))
        for path,expected in manifest["sources"].items():
            with self.subTest(source=path):
                self.assertEqual(hashlib.sha256((HERE.parent/path).read_bytes()).hexdigest(),expected["sha256"])

    def test_missing_fields_keep_null_legacy_offsets(self):
        missing = SCHEMA["required_extended_fields"]
        self.assertEqual(len(missing),76)
        self.assertTrue(all(x["offset"] is None for x in missing))
        names = {x["name"] for x in missing}
        self.assertTrue({"mild_motor_episode_scale_legs","mild_motor_episode_scale_wheels","wheel_mu","leg_pos.queue_cur","leg_pos.queue_out","action_queue.legs.issued_tick","action_queue.wheels.due_tick"} <= names)

    def test_offsets_and_time_unit_distinction(self):
        fields = {f["name"]:f for f in SCHEMA["layouts"]["E3"]["fields"]}
        self.assertEqual((fields["feedback_delay"]["offset"],fields["feedback_delay"]["width"]),(98,1))
        self.assertEqual(fields["command_time_left"]["legacy_to_canonical_multiplier"],100)
        self.assertEqual(fields["recovery_age"]["legacy_to_canonical_multiplier"],1)
        self.assertNotIn("STATIC_DR",fields["recovery_stable"]["classes"])

    def test_bad_offset_rejected(self):
        schema = copy.deepcopy(SCHEMA); schema["layouts"]["E3"]["fields"][1]["offset"] = 36
        with self.assertRaises(c.ContractViolation):c.validate_schema(schema)

    def test_raw35_not_clean(self):
        schema = copy.deepcopy(SCHEMA); schema["layouts"]["E3"]["fields"][0]["clean"] = True
        with self.assertRaises(c.ContractViolation):c.validate_schema(schema)

    def test_named_context_keeps_privileged_hidden_all_roles(self):
        for role in c.ROLES:
            with self.subTest(role=role):
                result = c.validate_named_context(role,named_context(role),SCHEMA)
                self.assertEqual(len(result["actor"]),35)
                self.assertNotIn("actor35_original",result["privileged_only"])
                self.assertIn("applied_torque",result["privileged_only"])
                self.assertFalse(result["exact"])

    def test_flat_old_context_rejected(self):
        with self.assertRaises(c.ContractViolation):c.validate_named_context("E3",[0]*122,SCHEMA)

    def test_missing_named_field_is_unknown(self):
        named = named_context("E3"); del named["applied_torque"]
        with self.assertRaises(c.ContractUnknown):c.validate_named_context("E3",named,SCHEMA)

    def test_nonfinite_and_wrong_width_rejected(self):
        for value in ([float("nan")]*35,[0]*34):
            named = named_context("E3"); named["actor35_original"] = value
            with self.assertRaises(c.ContractViolation):c.validate_named_context("E3",named,SCHEMA)

    def test_actor_original_named_terms_only(self):
        terms = {f["name"]:[.1]*f["width"] for f in SCHEMA["raw35_fields"]}
        terms["wheel_pos_slots"] = [0,0]; terms["mode_onehot"] = [1,0,0,0,0,0,0]
        original = tuple(x for f in SCHEMA["raw35_fields"] for x in terms[f["name"]])
        self.assertEqual(c.validate_actor_view(terms,original,SCHEMA),original)
        terms["applied_torque"] = [0]*30
        with self.assertRaises(c.ContractViolation):c.validate_actor_view(terms,original,SCHEMA)

    def test_sensor_both_delays_and_warmup(self):
        for delay in (0,1):
            with self.subTest(delay=delay):
                result = c.validate_sensor_pair(sensor_pair(delay),40,3,SCHEMA)
                self.assertTrue(result["two_samples_valid"]); self.assertFalse(result["actual_sdk_pass"])

    def test_mid_missing_and_50hz_endpoint_rejected(self):
        with self.assertRaises(c.ContractUnknown):c.validate_sensor_pair([sensor_pair()[1]],40,3,SCHEMA)

    def test_clean_sample_absent_is_unknown(self):
        samples = sensor_pair();del samples[0]["channels"]["leg_pos"]["clean_at_sample"]
        with self.assertRaises(c.ContractUnknown):c.validate_sensor_pair(samples,40,3,SCHEMA)

    def test_noise_used_required_not_redrawn(self):
        samples = sensor_pair();del samples[0]["channels"]["wheel_vel"]["noise_used"]
        with self.assertRaises(c.ContractUnknown):c.validate_sensor_pair(samples,40,3,SCHEMA)

    def test_source_profile_bounds_not_paper_defaults(self):
        samples = sensor_pair();samples[0]["channels"]["leg_pos"]["noise_used"][0] = .006
        with self.assertRaises(c.ContractViolation):c.validate_sensor_pair(samples,40,3,SCHEMA)

    def test_sensor_algebra_corruption_rejected(self):
        samples = sensor_pair();samples[0]["channels"]["leg_vel"]["noisy_before_queue"][0] += .2
        with self.assertRaises(c.ContractViolation):c.validate_sensor_pair(samples,40,3,SCHEMA)

    def test_feedback_delay_not_clean_endpoint(self):
        samples = sensor_pair();samples[1]["channels"]["base_ang_vel"]["out"] = list(samples[1]["channels"]["base_ang_vel"]["cur"])
        with self.assertRaises(c.ContractViolation):c.validate_sensor_pair(samples,40,3,SCHEMA)

    def test_skipped_clock_and_mixed_episode_rejected(self):
        for key,value in (("physics_tick",49),("episode",4)):
            samples = sensor_pair();samples[1][key] = value
            with self.assertRaises(c.ContractViolation):c.validate_sensor_pair(samples,40,3,SCHEMA)

    def test_previous_cache_absent_is_unknown(self):
        samples = sensor_pair();samples[0]["channels"]["base_ang_vel"]["previous_last"] = 10
        samples[0]["channels"]["base_ang_vel"]["ready"] = True
        with self.assertRaises(c.ContractUnknown):c.validate_sensor_pair(samples,40,3,SCHEMA)

    def test_observer_rng_mutation_rejected(self):
        samples = sensor_pair();samples[0]["channels"]["wheel_vel"]["probe_rng_after"] = "changed"
        with self.assertRaises(c.ContractViolation):c.validate_sensor_pair(samples,40,3,SCHEMA)

    def test_natural_draw_counter_mismatch_rejected(self):
        samples = sensor_pair();samples[0]["channels"]["wheel_vel"]["draw_count_after"] += 1
        with self.assertRaises(c.ContractViolation):c.validate_sensor_pair(samples,40,3,SCHEMA)

    def test_action_all_nine_lag_combinations(self):
        for legs in (0,1,2):
            for wheels in (0,1,2):
                with self.subTest(legs=legs,wheels=wheels):
                    self.assertTrue(c.validate_action_trace(action_trace(legs,wheels),40,3,SCHEMA)["eight_apply_ticks_valid"])

    def test_action_validity_issue_due_required(self):
        capture = action_trace();del capture["legs"]["apply_frames"][0]["queue"]["pending_valid"]
        with self.assertRaises(c.ContractUnknown):c.validate_action_trace(capture,40,3,SCHEMA)

    def test_late_first_application_rejected(self):
        capture = action_trace();capture["legs"]["apply_frames"][2]["queue"]["first_apply_tick"] = 43
        with self.assertRaises(c.ContractViolation):c.validate_action_trace(capture,40,3,SCHEMA)

    def test_first_latency_not_held_age(self):
        capture = action_trace();capture["legs"]["apply_frames"][7]["first_transition_delay_us"] = 17500
        with self.assertRaises(c.ContractViolation):c.validate_action_trace(capture,40,3,SCHEMA)

    def test_actual_articulation_target_mismatch_rejected(self):
        capture = action_trace();capture["wheels"]["apply_frames"][4]["articulation_target_readback"][0] += .1
        with self.assertRaises(c.ContractViolation):c.validate_action_trace(capture,40,3,SCHEMA)

    def test_only_one_action_group_rejected(self):
        capture = action_trace();del capture["wheels"]
        with self.assertRaises(c.ContractUnknown):c.validate_action_trace(capture,40,3,SCHEMA)

    def test_static_and_missing_motor_scale(self):
        before = static_capture();self.assertTrue(c.validate_static_episode(before,copy.deepcopy(before),SCHEMA,"E3"))
        after = copy.deepcopy(before);after["mild_motor_episode_scale_legs"][0] = .97
        with self.assertRaises(c.ContractViolation):c.validate_static_episode(before,after,SCHEMA,"E3")
        del after["mild_motor_episode_scale_legs"]
        with self.assertRaises(c.ContractUnknown):c.validate_static_episode(before,after,SCHEMA,"E3")

    def test_source_synthetic_fake_actual_never_exact(self):
        for receipt in (None,{"evidence_kind":"SOURCE"},{"evidence_kind":"SYNTHETIC"},{"evidence_kind":"ACTUAL_ORIGINAL100HZ_PASSIVE_CAPTURE"}):
            with self.subTest(receipt=receipt):
                with self.assertRaises(c.ContractUnknown):c.exact_gate(SCHEMA,receipt)

    def test_no_native_imports_rng_or_vector_slices(self):
        tree = ast.parse((HERE/"phase1_contract.py").read_text(encoding="utf-8"))
        imports = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names}
        self.assertLessEqual(imports,{"hashlib","json","math"})
        self.assertFalse(any(isinstance(n,ast.Slice) for n in ast.walk(tree)))
        self.assertFalse(any(isinstance(n,ast.Name) and n.id in {"torch","random","numpy","subprocess"} for n in ast.walk(tree)))


def main():
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Contracts)
    result = unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    output = stream.getvalue();print(output,end="")
    if "--receipt" in sys.argv:
        target = HERE/"SOURCE_RECEIPT.json"
        if target.exists():raise SystemExit("Frozen receipt already exists; tests above were read-only")
        evidence = c.verify_local_schema_manifest()
        receipt = {"version":1,"status":"SOURCE_SYNTHETIC_CONTRACT_PASS" if result.wasSuccessful() else "SOURCE_SYNTHETIC_CONTRACT_FAIL",
            "created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"tests_run":result.testsRun,
            "failures":len(result.failures),"errors":len(result.errors),"subtests":"all8 role views;9 actuator lag combinations;positive and negative sensor/clock/queue cases",
            "scope":"SOURCE + deterministic synthetic only; no SDK/native/model/replay/rawJSONL/canonical/Git/budget/locks",
            "schema_api":["load_schema","validate_schema","validate_named_context","validate_actor_view","validate_sensor_pair","validate_action_trace","validate_static_episode","exact_gate"],
            "source_identity":evidence,"actual_sdk_pass":False,"gate1_admitted":False,"gate1_status":"UNKNOWN_MISSING_PASSIVE_ORIGINAL100HZ_RECEIPTS",
            "exact":False,"paper_ready":False,"source_unchanged_hash_check_pass":result.wasSuccessful(),
            "existing_artifacts_modified":False,"stage2_trainer":False,"test_log_sha256":hashlib.sha256(output.encode()).hexdigest()}
        (HERE/"SYNTHETIC_TEST_LOG.txt").write_text(output,encoding="utf-8")
        target.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    raise SystemExit(main())
