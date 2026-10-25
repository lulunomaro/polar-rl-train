"""Pure CPU synthetic interface tests. No actual H1 trajectory is generated."""
from __future__ import annotations

import copy
import json
import math
import os
from pathlib import Path
import unittest

from contract_v1 import (ACTION_ORDER, ACTION_UNITS, SCHEMA, ContractError,
                         convert, model_view, pack_episode, validate_raw, validate_splits)


def episode(name, group, decimation=4):
    frames = [{"sim_tick": tick, "sim_time_ns": tick * 2_500_000,
               "available_at_tick": tick, "uri": f"synthetic://{name}/{tick}.rgb",
               "sha256": "0" * 64, "origin": "SYNTHETIC_ONLY",
               "width": 224, "height": 224, "channels": "RGB",
               "camera_calibration_sha256": "1" * 64}
              for tick in range(0, 81, 20)]
    actions = [{"start_tick": tick, "end_tick": tick + 1,
                "target6": [tick // decimation + channel / 10 for channel in range(6)],
                "issued_control_step": tick // decimation, "provenance": "SYNTHETIC_ONLY"}
               for tick in range(80)]
    return {"episode_id": name, "source_episode_uuid": f"SYNTHETIC-{name}",
            "physical_group_id": group, "simulator_run_id": "SYNTHETIC-RUN",
            "physics_profile_sha256": "2" * 64, "action_contract_sha256": "3" * 64,
            "policy_checkpoint_sha256": "4" * 64,
            "clock": {"physics_dt_ns": 2_500_000, "control_decimation": decimation,
                      "video_frame_period_ns": 50_000_000},
            "frames": frames, "applied_actions": actions, "reset_ticks": [],
            "evaluation_only": {"physical_values": {"friction_mu": 0.7},
                                "contact": "SYNTHETIC_SENTINEL", "success": False,
                                "state": [999], "reward": 123}}


def fixture(decimation=4):
    eps = [episode("train", "opaque-A", decimation),
           episode("validation-support", "opaque-B", decimation),
           episode("validation-query", "opaque-B", decimation),
           episode("test-support", "opaque-C", decimation),
           episode("test-query", "opaque-C", decimation)]
    raw = {"schema": SCHEMA, "synthetic": True, "dataset_id": "SYNTHETIC-NOT-TRAINING",
           "action_order": ACTION_ORDER, "action_units": ACTION_UNITS, "episodes": eps}
    plan = {"schema": "mod4.h1.t2z.split.v1", "assignments": [
        {"episode_id": e["episode_id"], "split": ("train" if e["episode_id"] == "train" else e["episode_id"].split("-")[0]),
         "role": ("fit" if e["episode_id"] == "train" else e["episode_id"].split("-")[1])} for e in eps]}
    return raw, plan


class ContractTests(unittest.TestCase):
    def rejection(self, code, fn):
        with self.assertRaises(ContractError) as outcome:
            fn()
        self.assertEqual(outcome.exception.code, code)

    def test_h1_100hz_twenty_physics_targets_preserved(self):
        raw, plan = fixture()
        result = convert(raw, plan)
        action = result["records"][0]["model"]["action_packed_t20x7"]
        self.assertEqual(len(action), 5)
        self.assertEqual([row[0] for row in action[1]], [tick // 4 for tick in range(20)])
        self.assertEqual(sum(row[6] for row in action[0]), 0)
        self.assertFalse(result["training_ready"])
        self.assertTrue(result["synthetic"])

    def test_e3_50hz_fractional_control_frame_alignment(self):
        raw, plan = fixture(8)
        action = convert(raw, plan)["records"][0]["model"]["action_packed_t20x7"]
        self.assertEqual([row[0] for row in action[1]], [tick // 8 for tick in range(20)])
        self.assertEqual([row[0] for row in action[2]], [tick // 8 for tick in range(20, 40)])
        self.assertEqual(action[1][-1][0], action[2][0][0])

    def test_synthetic_refuses_real_training_path(self):
        raw, _ = fixture()
        self.rejection("SYNTHETIC_NOT_TRAINING", lambda: validate_raw(raw, require_real=True))

    def test_missing_native_dataset_refused(self):
        raw, _ = fixture()
        raw["synthetic"], raw["episodes"] = False, []
        self.rejection("DATASET_MISSING", lambda: validate_raw(raw, require_real=True))

    def test_action_gap_refused(self):
        raw, _ = fixture()
        raw["episodes"][0]["applied_actions"].pop(10)
        self.rejection("ACTION_COVERAGE", lambda: validate_raw(raw))

    def test_action_overlap_refused(self):
        raw, _ = fixture()
        raw["episodes"][0]["applied_actions"][10]["start_tick"] = 9
        self.rejection("ACTION_COVERAGE", lambda: validate_raw(raw))

    def test_reset_boundary_refused(self):
        raw, _ = fixture()
        raw["episodes"][0]["reset_ticks"] = [20]
        self.rejection("RESET_CROSSING", lambda: validate_raw(raw))

    def test_nonfinite_target_refused(self):
        raw, _ = fixture()
        raw["episodes"][0]["applied_actions"][0]["target6"][0] = math.nan
        self.rejection("NONFINITE", lambda: validate_raw(raw))

    def test_frame_gap_refused(self):
        raw, _ = fixture()
        raw["episodes"][0]["frames"][1]["sim_tick"] = 19
        raw["episodes"][0]["frames"][1]["sim_time_ns"] = 19 * 2_500_000
        raw["episodes"][0]["frames"][1]["available_at_tick"] = 19
        self.rejection("FRAME_GAP", lambda: validate_raw(raw))

    def test_physical_group_leak_refused(self):
        raw, plan = fixture()
        raw["episodes"][1]["physical_group_id"] = "opaque-A"
        self.rejection("PHYSICAL_GROUP_LEAK", lambda: validate_splits(raw, plan))

    def test_support_query_source_episode_reuse_refused(self):
        raw, plan = fixture()
        raw["episodes"][4]["source_episode_uuid"] = raw["episodes"][3]["source_episode_uuid"]
        for frame in raw["episodes"][4]["frames"]:
            frame["sim_tick"] += 100
        self.rejection("SUPPORT_QUERY_EPISODE_LEAK", lambda: validate_splits(raw, plan))

    def test_query_view_has_no_future_contact_parameter_labels_or_group(self):
        raw, plan = fixture()
        packed = pack_episode(raw["episodes"][4], True)
        query = model_view(packed, "query")
        self.assertEqual(set(query), {"sample_id", "synthetic", "initial_rgb", "action_packed_t20x7"})
        for marker in ("SYNTHETIC_SENTINEL", "friction_mu", "physical_group_id", "observed_target_rgb"):
            self.assertNotIn(marker, json.dumps(query))

    def test_query_truth_perturbation_cannot_change_model_input(self):
        raw, plan = fixture()
        before = convert(raw, plan)["records"][-1]["model"]
        raw["episodes"][-1]["evaluation_only"] = {"physical_values": {"friction_mu": -999}, "success": True}
        for frame in raw["episodes"][-1]["frames"][1:]:
            frame["uri"] = "synthetic://SECRET-FUTURE-TARGET"
        after = convert(raw, plan)["records"][-1]["model"]
        self.assertEqual(before, after)

    def test_group_id_never_enters_model_view(self):
        raw, plan = fixture()
        before = convert(raw, plan)["records"][-1]["model"]
        for ep in raw["episodes"][-2:]:
            ep["physical_group_id"] = "SECRET-numeric-physical-label"
        self.assertEqual(before, convert(raw, plan)["records"][-1]["model"])

    def test_same_requested_action_different_actual_application_remains_distinct(self):
        raw, plan = fixture()
        before = convert(raw, plan)["records"][0]["model"]["action_packed_t20x7"]
        raw["episodes"][0]["requested_raw6"] = [0] * 6
        raw["episodes"][0]["applied_actions"][10]["target6"][0] += 0.5
        after = convert(raw, plan)["records"][0]["model"]["action_packed_t20x7"]
        self.assertNotEqual(before, after)
        self.assertEqual(after[1][10][0] - before[1][10][0], 0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
