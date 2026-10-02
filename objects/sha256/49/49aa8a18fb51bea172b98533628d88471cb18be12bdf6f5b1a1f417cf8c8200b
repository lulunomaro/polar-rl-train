import os
import unittest

from repair_contracts import PerKindProgress, REQUIRED_TRAINING_ENV, require_explicit_training_env


class PerKindProgressTest(unittest.TestCase):
    def test_parallel_envs_and_success_latch(self):
        p = PerKindProgress()
        kinds = ["run", "step_up"]
        p.update([0, 0, 1], [0, 0, 0], [0, 1, 0], kinds)
        p.update([0, 0, 1], [0, 0, 0], [1, 1, 0], kinds)
        self.assertEqual(p.counts["run"], {"att": 2, "suc": 2})
        self.assertEqual(p.counts["step_up"], {"att": 1, "suc": 0})
        p.update([1, 0, 1], [1, 0, 1], [0, 1, 1], kinds)
        self.assertEqual(p.counts["run"], {"att": 2, "suc": 2})
        self.assertEqual(p.counts["step_up"], {"att": 3, "suc": 1})

    def test_explicit_contract(self):
        env = {k: "1" for k in REQUIRED_TRAINING_ENV}
        env.update(RM_MOD4_MAP="rmuc2026", RM_MOD4_TERRAIN="field",
                   RM_CRANK_ACTION_SCALE="0.75", RM_SEQ_HISTORY="5")
        require_explicit_training_env(env)
        del env["RM_LEG_KP"]
        with self.assertRaisesRegex(ValueError, "RM_LEG_KP"):
            require_explicit_training_env(env)


if __name__ == "__main__":
    unittest.main()
