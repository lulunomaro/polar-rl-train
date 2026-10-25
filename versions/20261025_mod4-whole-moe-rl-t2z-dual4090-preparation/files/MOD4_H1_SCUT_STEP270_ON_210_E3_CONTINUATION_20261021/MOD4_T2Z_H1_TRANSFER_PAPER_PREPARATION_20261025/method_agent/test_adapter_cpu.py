"""Only tiny CPU synthetic tensors. Does not load or execute Wan/PPO/PhysX."""
from __future__ import annotations

import unittest
import torch
from h1_temporal_action_adapter import H1TemporalActionEncoder
from contract_v1 import convert
from test_contract_cpu import fixture


class AdapterTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(731)
        torch.set_num_threads(1)
        self.adapter = H1TemporalActionEncoder(32, [0] * 6, [1] * 6,
                                                frame_width=16, hidden_width=32).cpu()
        raw, plan = fixture()
        action = convert(raw, plan)["records"][0]["model"]["action_packed_t20x7"]
        self.action = torch.tensor([action], dtype=torch.float32, device="cpu")

    def test_context_and_causal_vae_modulation_shapes(self):
        context, modulation = self.adapter.encode_ti2v2(self.action)
        self.assertEqual(tuple(context.shape), (1, 5, 32))
        self.assertEqual(tuple(modulation.shape), (1, 2, 32))
        self.assertTrue(bool(torch.isfinite(context).all() and torch.isfinite(modulation).all()))

    def test_proposed_forty_one_frame_geometry(self):
        # Synthetic shape exercise only: not a native 2s trajectory/dataset.
        action = torch.cat((self.action[:, :1], self.action[:, 1:].repeat(1, 10, 1, 1)), dim=1)
        context, modulation = self.adapter.encode_ti2v2(action)
        self.assertEqual(tuple(context.shape), (1, 41, 32))
        self.assertEqual(tuple(modulation.shape), (1, 11, 32))

    def test_order_changes_embedding_even_with_identical_interval_mean(self):
        swapped = self.action.clone()
        swapped[:, 1] = swapped[:, 1].flip(1)
        # Reduction order can change float32 rounding although the multisets
        # are identical. This checks the mean, not bitwise accumulation order.
        self.assertTrue(torch.allclose(swapped[:, 1].mean(1), self.action[:, 1].mean(1),
                                       atol=1e-6, rtol=1e-6))
        first = self.adapter.encode_ti2v2(self.action)[1]
        second = self.adapter.encode_ti2v2(swapped)[1]
        self.assertGreater(float((first - second).abs().max()), 1e-7)

    def test_cpu_gradient_reaches_new_adapter(self):
        context, modulation = self.adapter.encode_ti2v2(self.action)
        loss = context.square().mean() + modulation.square().mean()
        loss.backward()
        self.assertTrue(all(p.device.type == "cpu" for p in self.adapter.parameters()))
        self.assertTrue(all(p.grad is not None and bool(torch.isfinite(p.grad).all()) for p in self.adapter.parameters()))
        self.assertFalse(torch.cuda.is_initialized())

    def test_missing_tick_is_rejected(self):
        invalid = self.action.clone()
        invalid[0, 2, 5, 6] = 0
        with self.assertRaisesRegex(ValueError, "all future physics ticks"):
            self.adapter(invalid)

    def test_future_action_cannot_enter_anchor(self):
        invalid = self.action.clone()
        invalid[0, 0, 0, 0] = 1
        with self.assertRaisesRegex(ValueError, "initial observation anchor"):
            self.adapter(invalid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
