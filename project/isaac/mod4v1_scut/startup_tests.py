"""CPU tests for the authorized initialization/spawn changes; no production PT."""
from copy import deepcopy
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
import tempfile
import hashlib
import torch
from tensordict import TensorDict
from .train import build_runner
from .config import runner_config,model_contract
from .finetune import migrate_weights
from .course import FourSideStrict270,top_mask,metadata
from .math_ops import quat_from_euler_xyz


class Tests(unittest.TestCase):
    def test_resized_population_keeps_complete_ppo_and_rejects_bad_identity(self):
        from .checkpoint import restore_resized_learning,learning_state,FORMAT,INTERFACE
        from .config import USD_SHA,CONTRACT_SHA,ACTION_CLIP,ACTION_INTERFACE
        class Env:
            num_envs=8;num_actions=6;device='cpu';max_episode_length=400;cfg={}
            episode_length_buf=torch.zeros(8,dtype=torch.long)
            def get_observations(self):
                return TensorDict(dict(policy=torch.zeros(8,35),critic=torch.zeros(8,78)),batch_size=[8])
        old=build_runner(Env(),None);new=build_runner(Env(),None)
        # Give every parameter real Adam first/second moments with one finite step.
        loss=sum(p.square().sum()for g in old.alg.optimizer.param_groups for p in g['params'])
        loss.backward();old.alg.optimizer.step();old.current_learning_iteration=26
        import numpy as np,random
        saved=dict(learning_state(old),format=FORMAT,interface=INTERFACE,profile='jump270',
            usd_SHA=USD_SHA,contract_SHA=CONTRACT_SHA,actor_dim=35,critic_dim=78,
            action_clip=ACTION_CLIP,action_interface=ACTION_INTERFACE,num_envs=80,cpu_rng=torch.get_rng_state(),
            cuda_rng=[],python_rng=random.getstate(),numpy_rng=np.random.get_state(),
            source_global_counters=dict(_value_debug_step=17,common_step_counter=624))
        reward=SimpleNamespace(_value_debug_step=0,common_step_counter=0)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'synthetic.pt';torch.save(saved,path);raw=path.read_bytes()
            receipt=restore_resized_learning(new,path,hashlib.sha256(raw).hexdigest(),len(raw),'jump270',20000,reward)
            self.assertEqual(new.current_learning_iteration,26)
            self.assertEqual(receipt['new_envs'],20000)
            self.assertTrue(receipt['actor_critic_STD_Adam_LR_iteration_restored'])
            self.assertEqual((reward._value_debug_step,reward.common_step_counter),(17,624))
            for key,value in old.alg.actor.state_dict().items():torch.testing.assert_close(value,new.alg.actor.state_dict()[key],atol=0,rtol=0)
            for key,value in old.alg.optimizer.state_dict()['state'].items():
                for name,tensor in value.items():torch.testing.assert_close(tensor,new.alg.optimizer.state_dict()['state'][key][name],atol=0,rtol=0)
            with self.assertRaises(ValueError):restore_resized_learning(new,path,'0'*64,len(raw),'jump270',20000,reward)

    def test_weights_and_semantic_critic_columns(self):
        from rsl_rl.runners import OnPolicyRunner
        class Env:
            num_envs=8;num_actions=6;device='cpu';max_episode_length=400;cfg={}
            episode_length_buf=torch.zeros(8,dtype=torch.long)
            dim=38
            def get_observations(self):
                return TensorDict(dict(policy=torch.zeros(8,35),critic=torch.zeros(8,self.dim)),batch_size=[8])
        old=OnPolicyRunner(Env(),deepcopy(runner_config()),log_dir=None,device='cpu')
        env=Env();env.dim=78
        new=build_runner(env,None)
        receipt=migrate_weights(new,old.alg.save())
        policy=torch.linspace(-.2,.2,280).reshape(8,35)
        x=torch.linspace(-.3,.3,624).reshape(8,78)
        oldx=torch.zeros(8,38)
        for a,b,scale in receipt['critic38_to78_named_columns']:oldx[:,a]=x[:,b]*scale
        with torch.no_grad():
            torch.testing.assert_close(old.alg.actor(TensorDict(dict(policy=policy),[8])),new.alg.actor(TensorDict(dict(policy=policy),[8])))
            torch.testing.assert_close(old.alg.critic(TensorDict(dict(critic=oldx),[8])),new.alg.critic(TensorDict(dict(critic=x),[8])),atol=2e-6,rtol=1e-5)
        self.assertEqual(len(new.alg.optimizer.state),0)
        self.assertEqual(new.current_learning_iteration,0)
        for key,value in old.alg.actor.state_dict().items():
            torch.testing.assert_close(value,new.alg.actor.state_dict()[key],rtol=0,atol=0)
        first=next(v for v in new.alg.critic.state_dict().values() if v.ndim==2 and v.shape[1]==78)
        self.assertEqual(int(torch.count_nonzero(first[:,31])),0)
        self.assertEqual(int(torch.count_nonzero(first[:,39:])),0)

    def test_four_actual_edges_keep_strict_clearance_and_support(self):
        c=model_contract('F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/assets')
        n=4;m=FourSideStrict270(n,'cpu')
        angles=torch.arange(4)*torch.pi/2
        q=quat_from_euler_xyz(torch.zeros(n),torch.zeros(n),angles)
        def update(distance,z,force):
            p=torch.zeros(n,2,3)
            for i,a in enumerate(angles):
                p[i,:,0]=distance*torch.cos(a)-torch.tensor([-.12,.12])*torch.sin(a)
                p[i,:,1]=distance*torch.sin(a)+torch.tensor([-.12,.12])*torch.cos(a)
            p[:,:,2]=z
            net=torch.zeros(n,2,3);net[:,:,2]=force
            top=torch.full((n,2),force if z>.3 else 0.)
            m.update_world(p,q[:,None].expand(-1,2,-1),c,torch.zeros(n,3),top,
                torch.zeros(n,2),net,torch.zeros(n),torch.zeros(n,3),q,torch.ones(n,dtype=torch.bool))
        update(0.,.0625,20.)
        # Real upward flight gate; this synthetic test calls unchanged meter up directly
        # only after the no-force endpoint created first flight in all four directions.
        update(.3,.35,0.)
        for meter in m.meters:meter.up |= meter.flight_id==1
        update(.7,.35,0.)
        self.assertTrue(bool(m.wholeclear.all()))
        for _ in range(212):update(.7,.3325,20.)
        self.assertTrue(bool(m.success.all()))
        m.reset(torch.tensor([1]));self.assertFalse(bool(m.success[1]));self.assertTrue(bool(m.success[0]))

    def test_contact_surface_and_published_spawn(self):
        p=torch.tensor([[0.,0.,.27],[.51,0.,.27],[0.,-.51,.27],[3.6,0.,.27],[.51,0.,0.]])
        self.assertEqual(top_mask(p).tolist(),[False,True,True,False,False])
        self.assertEqual(metadata()['root_position_m'],[0.,0.,.38])
        self.assertEqual(metadata()['nearest_edge_from_centre_m'],.5)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--report',type=Path,required=True);a=parser.parse_args()
    if a.report.exists():raise FileExistsError(a.report)
    torch.set_num_threads(2);torch.manual_seed(270)
    stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    a.report.write_text(json.dumps(dict(passed=r.wasSuccessful(),tests=r.testsRun,output=stream.getvalue(),
        production_PT_reads=0,physics=0,kind='CPU_SYNTHETIC_STARTUP_POSITION_FINETUNE'),indent=2))
    print(stream.getvalue());raise SystemExit(0 if r.wasSuccessful() else 1)
