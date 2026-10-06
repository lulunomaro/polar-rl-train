import unittest,torch
from history_latent_component import FeedbackHistory,VelocityEncoder,actor_input,supervised_velocity_loss,expand_actor_state
torch.set_num_threads(1)

class HistoryContracts(unittest.TestCase):
    def test_initial_frame_fills_all_history(self):
        h=FeedbackHistory(2);x=torch.arange(70,dtype=torch.float32).reshape(2,35)
        torch.testing.assert_close(h.observe(x,0).reshape(2,5,35),x[:,None,:].expand(-1,5,-1),rtol=0,atol=0)
    def test_time_order_and_span40ms(self):
        h=FeedbackHistory(1)
        for i in range(7):v=h.observe(torch.full((1,35),float(i)),i)
        self.assertEqual(v.reshape(1,5,35)[0,:,0].tolist(),[2.,3.,4.,5.,6.]);self.assertEqual((5-1)*.01,.04)
    def test_repeated_common_tick_is_cached(self):
        h=FeedbackHistory(2);x=torch.ones(2,35);a=h.observe(x,3);b=h.observe(x*9,3)
        self.assertTrue(torch.equal(a,b));self.assertEqual(h.advances,1)
    def test_selected_reset_no_old_episode_or_other_row_change(self):
        h=FeedbackHistory(3)
        h.observe(torch.ones(3,35),0);before=h.observe(torch.ones(3,35)*2,1)
        h.reset_rows([1]);x=torch.ones(3,35)*17;after=h.observe(x,1).reshape(3,5,35)
        self.assertTrue(torch.equal(after[[0,2]].flatten(1),before[[0,2]]))
        self.assertTrue(torch.equal(after[1],torch.full((5,35),17.)));self.assertEqual(h.last_tick,1)
    def test_reset_on_next_tick_still_preserves_other_histories(self):
        h=FeedbackHistory(2);h.observe(torch.ones(2,35),0);h.reset_rows([0]);v=h.observe(torch.ones(2,35)*5,1).reshape(2,5,35)
        self.assertEqual(v[0,:,0].tolist(),[5.]*5);self.assertEqual(v[1,:,0].tolist(),[1.,1.,1.,1.,5.])
    def test_no_input_or_cache_alias(self):
        h=FeedbackHistory(1);x=torch.ones(1,35);a=h.observe(x,0);a.zero_()
        self.assertTrue(torch.equal(x,torch.ones_like(x)));self.assertEqual(float(h.frames.sum()),175.)
    def test_reject_bad_shape_and_nonfinite(self):
        h=FeedbackHistory(1)
        for x in [torch.ones(1,38),torch.full((1,35),float('nan'))]:
            with self.assertRaises(ValueError):h.observe(x,0)
    def test_reject_missing_or_backward_tick(self):
        h=FeedbackHistory(1);h.observe(torch.ones(1,35),4)
        for t in [3,6,True]:
            with self.assertRaises(ValueError):h.observe(torch.ones(1,35),t)
    def test_reject_invalid_reset_row(self):
        h=FeedbackHistory(2)
        with self.assertRaises(ValueError):h.reset_rows([2])

class EncoderContracts(unittest.TestCase):
    def test_rng_is_unchanged_and_seed_is_reproducible(self):
        torch.manual_seed(7);before=torch.get_rng_state().clone();a=VelocityEncoder(21)
        self.assertTrue(torch.equal(before,torch.get_rng_state()));b=VelocityEncoder(21)
        self.assertTrue(all(torch.equal(a.state_dict()[k],v) for k,v in b.state_dict().items()))
    def test_deployment_input_has_only38_entries(self):
        e=VelocityEncoder();x=torch.ones(3,35);h=torch.ones(3,175)
        y=actor_input(x,h,e,'A1');self.assertEqual(y.shape,(3,38));self.assertTrue(torch.equal(y[:,:35],x))
    def test_A1_actor_gradient_does_not_update_encoder(self):
        e=VelocityEncoder();x=torch.ones(2,35,requires_grad=True)
        y=actor_input(x,torch.ones(2,175),e,'A1');y.sum().backward()
        self.assertTrue(all(p.grad is None for p in e.parameters()));self.assertIsNotNone(x.grad)
    def test_A1_separate_velocity_supervision_updates_encoder_only(self):
        e=VelocityEncoder();label=torch.ones(2,3,requires_grad=True)
        supervised_velocity_loss(torch.ones(2,175),e,label).backward()
        self.assertTrue(any(p.grad is not None and p.grad.abs().sum()>0 for p in e.parameters()));self.assertIsNone(label.grad)
    def test_A2_joint_gradient_reaches_encoder(self):
        e=VelocityEncoder();y=actor_input(torch.ones(2,35),torch.ones(2,175),e,'A2');y[:,-3:].square().sum().backward()
        self.assertTrue(any(p.grad is not None and p.grad.abs().sum()>0 for p in e.parameters()))
    def test_source_std_and_existing_weights_preserved(self):
        g=torch.Generator().manual_seed(5)
        old={'mlp.0.weight':torch.randn(256,35,generator=g),'mlp.0.bias':torch.randn(256,generator=g),'distribution.std_param':torch.tensor([.1,.2,.3,.4,.5,.6])}
        new=expand_actor_state(old)
        self.assertEqual(new['mlp.0.weight'].shape,(256,38));self.assertTrue(torch.equal(new['mlp.0.weight'][:,:35],old['mlp.0.weight']))
        self.assertTrue(torch.equal(new['distribution.std_param'],old['distribution.std_param']));self.assertEqual(float(new['mlp.0.weight'][:,-3:].abs().sum()),0.)
    def test_migration_rejects_wrong_actual_schema(self):
        with self.assertRaises(ValueError):expand_actor_state({'mlp.0.weight':torch.ones(256,38)})

if __name__=='__main__':unittest.main()
