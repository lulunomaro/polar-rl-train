from __future__ import annotations
import ast, copy, hashlib, importlib.util, json, os, pathlib, sys, tempfile, types, unittest
from unittest.mock import patch
import torch
from torch import nn

ROOT = pathlib.Path(__file__).resolve().parents[1]
CODE = ROOT/'overlay/isaac/mod4'
sys.path.insert(0, str(CODE))
from repair_contracts import (POLICY_TERMS, EpisodeLedger, latest_term_indices,
                              episode_counts, validate_warmstart, assert_checkpoint_semantics)
import repair_gate
from repair_step import RepairStepMixin


def function_from(path, name, namespace):
    tree = ast.parse(path.read_text(encoding='utf8'))
    node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace[name]


def episode(env=0, number=0, win=False, fail=False, rid=0):
    return dict(env_id=env, episode_id=number, route_id=rid, duration_s=45.,
                terminated=fail, truncated=not fail, goal_seen=win,
                spin_deg=0., peak_rise_m=.03, max_air_time_s=.1,
                underpass_seen=False, launched=False, air_after_launch=False, landed=False,
                terms={'base_contact':fail, 'time_out':not fail})


class ContractsTests(unittest.TestCase):
    def test_history_gathers_each_term_latest_sample(self):
        # Distinct values expose a false whole-frame assumption even with all-equal history.
        blocks = [torch.arange(5*d).reshape(5,d) + 1000*i for i, (_,d) in enumerate(POLICY_TERMS)]
        packed = torch.cat([v.flatten() for v in blocks])
        want = torch.cat([v[-1] for v in blocks])
        self.assertTrue(torch.equal(packed[latest_term_indices(5)], want))
        self.assertFalse(torch.equal(packed[-35:], want))

    def test_plain_history_identity(self):
        self.assertEqual(latest_term_indices(1).tolist(), list(range(35)))

    def test_history_unknown_layout_refused(self):
        with self.assertRaises(ValueError): latest_term_indices(5, 34)
        with self.assertRaises(ValueError): latest_term_indices(0)

    def test_curriculum_one_episode_not_1000_attempts(self):
        ids = torch.tensor([0,1])
        total = torch.zeros(2)
        for _ in range(100):
            a,_ = episode_counts(ids, ['run','spin'], ['run','spin'], torch.tensor([False,False]),
                                 torch.tensor([True,False]), torch.tensor([False,False]))
            total += a
        a,s = episode_counts(ids, ['run','spin'], ['run','spin'], torch.tensor([True,True]),
                             torch.tensor([True,False]), torch.tensor([False,True]))
        self.assertEqual((total+a).tolist(), [1,1])
        self.assertEqual(s.tolist(), [1,0])

    def test_route_index_maps_to_kind_instead_of_clamping(self):
        a,s = episode_counts(torch.tensor([0,2,3]), ['run','run','ramp','spin'], ['run','ramp','spin'],
                            torch.tensor([True,True,True]), torch.tensor([True,True,True]),
                            torch.tensor([False,True,False]))
        self.assertEqual(a.tolist(), [1,1,1]); self.assertEqual(s.tolist(), [1,0,1])

    def test_route_index_invalid_is_not_silently_clamped(self):
        with self.assertRaises(IndexError):
            episode_counts(torch.tensor([9]), ['run'], ['run'], torch.tensor([True]),
                           torch.tensor([True]),torch.tensor([False]))

    def test_success_cannot_hide_failure_next_episode(self):
        ledger = EpisodeLedger(1, ['run'])
        ledger.consume([episode(win=True)])
        ledger.consume([episode(number=1, fail=True)])
        b = ledger.buckets()['run']
        self.assertEqual(b['episodes'], 2); self.assertEqual(b['complete_rate'], .5)

    def test_simultaneous_goal_and_crash_fails(self):
        ledger = EpisodeLedger(1,['run']); ledger.consume([episode(win=True,fail=True)])
        self.assertEqual(ledger.buckets()['run']['successes'],0)

    def test_duplicate_and_unfinished_episodes_refused(self):
        ledger = EpisodeLedger(1,['run']); row=episode()
        ledger.consume([row])
        with self.assertRaises(ValueError): ledger.consume([row])
        row=episode(number=1);row['truncated']=False
        with self.assertRaises(ValueError): ledger.consume([row])

    def test_episode_gap_refused(self):
        ledger=EpisodeLedger(1,['run']);ledger.consume([episode()])
        with self.assertRaises(ValueError): ledger.consume([episode(number=2)])

    def test_empty_bucket_is_not_zero_or_pass(self):
        self.assertIsNone(EpisodeLedger(2,['run']).buckets()['run']['complete_rate'])

    def test_warmstart_allows_complete_encoder_only(self):
        actor={'mlp.0.weight':torch.ones(2,3),'encoder.0.weight':torch.ones(1,3)}
        critic={'mlp.0.weight':torch.ones(2,3)}
        ck={'actor_state_dict':{'mlp.0.weight':torch.ones(2,3)},'critic_state_dict':critic}
        self.assertEqual(validate_warmstart(actor,critic,ck,True),['encoder.0.weight'])
        with self.assertRaises(ValueError): validate_warmstart(actor,critic,ck,False)

    def test_warmstart_rejects_missing_head_critic_nonfinite(self):
        actor={'a':torch.ones(1),'b':torch.ones(1)};critic={'v':torch.ones(1)}
        for ck in [dict(actor_state_dict={'a':torch.ones(1)},critic_state_dict=critic),
                   dict(actor_state_dict=actor,critic_state_dict={}),
                   dict(actor_state_dict={'a':torch.tensor([float('nan')]),'b':torch.ones(1)},critic_state_dict=critic)]:
            with self.assertRaises(ValueError): validate_warmstart(actor,critic,ck,True)

    def test_half_present_encoder_refused(self):
        actor={'a':torch.ones(1),'encoder.0':torch.ones(1),'encoder.1':torch.ones(1)}
        critic={'v':torch.ones(1)}
        with self.assertRaises(ValueError):
            validate_warmstart(actor,critic,dict(actor_state_dict={'a':torch.ones(1),'encoder.0':torch.ones(1)},
                                               critic_state_dict=critic),True)

    def test_legacy_sequence_checkpoint_needs_semantic_version(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'model.pt';torch.save({'actor_state_dict':{'encoder.0':torch.ones(1)}},p)
            with self.assertRaises(ValueError): assert_checkpoint_semantics(p)
            (p.parent/'run_manifest.json').write_text(json.dumps({'observation_semantics':'mod4_term_major_latest_gather_v1'}))
            assert_checkpoint_semantics(p)

    def test_chassis_force_is_not_subtracted_from_roller_force(self):
        S=types.SimpleNamespace
        scene_cfg=lambda name:S(name=name)
        robot=S(data=S(root_pos_w=torch.tensor([[0.,0.,.18]])))
        make=lambda force:S(data=S(net_forces_w=torch.tensor([[[0.,0.,force]]])))
        env=S(scene=S(sensors={'chassis':make(100.),'guide_contact':make(200.)}),
              _mod4_ground_z=torch.tensor([0.]), _mod4_height_cmd=torch.tensor([[.18]]))
        ns={'torch':torch, 'SceneEntityCfg':scene_cfg, '_robot':lambda _:robot}
        fn=function_from(CODE/'skills_isaac.py','chassis_belly_down',ns)
        self.assertTrue(bool(fn(env,scene_cfg('chassis'))[0]))

    def test_backward_crouch_gets_no_forward_credit(self):
        robot=types.SimpleNamespace(data=types.SimpleNamespace(root_lin_vel_b=torch.tensor([[-.1,0,0],[.1,0,0]])))
        ns={'torch':torch,'CROUCH_MOVE_GATE':True,'CROUCH_MOVE_VMIN':.05,'_robot':lambda _:robot}
        fn=function_from(CODE/'skills_isaac.py','_crouch_drive',ns)
        self.assertEqual(fn(None).tolist(),[0.,1.])


class SequenceModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class FakeMLPModel(nn.Module):
            def __init__(self, obs_dim=175, obs_set='actor', **kw):
                super().__init__();self.obs_dim=obs_dim
                self.mlp=nn.Sequential(nn.Linear(self._get_latent_dim(),6))
                self.obs_normalizer=nn.Identity();self.distribution=None
            def get_latent(self, obs, masks=None, hidden_state=None): return obs
            def forward(self,x): return self.mlp(self.get_latent(x))
        def MLP(i,o,hidden,activation):
            dims=[i]+list(hidden)+[o]; layers=[]
            for j in range(len(dims)-1):
                layers.append(nn.Linear(dims[j],dims[j+1]))
                if j<len(dims)-2: layers.append(nn.ELU())
            return nn.Sequential(*layers)
        modules={'rsl_rl':types.ModuleType('rsl_rl'), 'rsl_rl.models':types.ModuleType('rsl_rl.models'),
                 'rsl_rl.modules':types.ModuleType('rsl_rl.modules')}
        modules['rsl_rl.models'].MLPModel=FakeMLPModel; modules['rsl_rl.modules'].MLP=MLP
        with patch.dict(sys.modules,modules):
            spec=importlib.util.spec_from_file_location('tested_sequence',CODE/'mod4_sequence_model.py')
            cls.module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.module;spec.loader.exec_module(cls.module)

    def test_plain_warmstart_exact_and_latent_branch_can_learn(self):
        torch.manual_seed(4)
        m=self.module.LatentEncoderModel(obs_dim=175,obs_set='actor')
        with torch.no_grad(): m.mlp[0].weight[:,35:]=0
        x=torch.randn(8,175); current=x.index_select(-1,latest_term_indices(5))
        expected=nn.functional.linear(current,m.mlp[0].weight[:,:35],m.mlp[0].bias)
        self.assertTrue(torch.allclose(m(x),expected,atol=1e-6))
        m(x).square().sum().backward()
        self.assertGreater(float(m.mlp[0].weight.grad[:,35:].abs().sum()),0)
        opt=torch.optim.SGD(m.parameters(),lr=.001);opt.step();opt.zero_grad()
        m(x).square().sum().backward()
        self.assertGreater(sum(float(p.grad.abs().sum()) for p in m.encoder.parameters()),0)

    def test_exports_use_identical_current_frame(self):
        m=self.module.LatentEncoderModel(obs_dim=175,obs_set='actor');x=torch.randn(2,175)
        self.assertTrue(torch.allclose(m(x),m.as_jit()(x)))
        self.assertTrue(torch.allclose(m(x),m.as_onnx(False)(x)))
        jit=torch.jit.script(m.as_jit())
        self.assertTrue(torch.allclose(jit(x),m(x)))


class PhaseTests(unittest.TestCase):
    def test_required_hook_cannot_silently_disappear(self):
        env=RepairStepMixin();cfg=types.SimpleNamespace(events=types.SimpleNamespace())
        with self.assertRaises(ValueError): env._repair_configure(cfg)

    def test_unknown_event_refused(self):
        env=RepairStepMixin(); cfg=types.SimpleNamespace(events=types.SimpleNamespace(x=types.SimpleNamespace(mode='step')))
        with self.assertRaises(ValueError): env._repair_configure(cfg)

    def test_engine_loop_terminal_snapshot_precedes_auto_reset(self):
        S=types.SimpleNamespace
        trace=[]
        ns={'torch':torch,'VecEnvStepReturn':tuple}
        step=function_from(CODE/'mod4_env.py','step',ns)
        for decimated in (True,False):
            trace.clear()
            recorder=S(active_terms=[],record_pre_step=lambda:None,record_post_physics_decimation_step=lambda:None,
                       record_pre_reset=lambda ids:trace.append('pre_reset'),record_post_reset=lambda ids:None)
            env=S(device='cpu',cfg=S(decimation=2,sim=S(render_interval=2),num_rerenders_on_reset=0),
                _sim_step_counter=0,_physics_handles_decimation=decimated,step_dt=.01,physics_dt=.005,
                render_enabled=False,has_rtx_sensors=False,episode_length_buf=torch.zeros(1),common_step_counter=0,
                extras={},recorder_manager=recorder,
                action_manager=S(process_action=lambda x:trace.append('action'), apply_action=lambda:None),
                sim=S(is_rendering=False,step=lambda **kw:trace.append('physics')),
                scene=S(write_data_to_sim=lambda:None,update=lambda **kw:None),
                termination_manager=S(compute=lambda:torch.tensor([True]),terminated=torch.tensor([False]),time_outs=torch.tensor([True])),
                reward_manager=S(compute=lambda **kw:trace.append('reward') or torch.ones(1)),
                command_manager=S(compute=lambda **kw:trace.append('command')),
                event_manager=S(available_modes=[]),
                observation_manager=S(compute=lambda **kw:trace.append('obs') or {}),
                _repair_before_physics=lambda:trace.append('pre'),
                _repair_after_physics=lambda:trace.append('post'),
                _repair_after_reward=lambda:trace.append('snapshot') or [{'goal':True}],
                _repair_publish_reference=lambda:trace.append('reference'),
                _reset_idx=lambda ids:trace.append('reset'))
            output=step(env,torch.zeros(1,6))
            self.assertLess(trace.index('post'),trace.index('reward'))
            self.assertLess(trace.index('physics'),trace.index('post'))
            self.assertLess(trace.index('snapshot'),trace.index('reset'))
            self.assertLess(trace.index('reference'),trace.index('obs'))
            self.assertEqual(output[-1]['repair_terminal_episodes'],[{'goal':True}])


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.directory=pathlib.Path(self.tmp.name)

    def report(self,seed=1,rate=1.,tag='x'):
        protocol={'max_episode_length':4500,'usd_sha256':'d'*64}
        ph=hashlib.sha256(json.dumps(protocol,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        ledger=EpisodeLedger(10,['run']);ledger.consume([episode(env=i,win=i<10*rate) for i in range(10)])
        d=dict(schema='mod4_episode_eval_v1',status='ROLLOUT_COMPLETE',seed=seed,
               checkpoint_sha256=('a' if tag=='old' else 'b')*64,protocol=protocol,protocol_sha256=ph,
               steps_completed=9000,episodes=ledger.records,route_kinds=ledger.buckets(),closure_max_m=.001,mimic_max_rad=.002)
        p=self.directory/f'{tag}_{seed}.json';p.write_text(json.dumps(d));return p

    def test_valid_suite_and_retention(self):
        old=[self.report(s,1.,'old') for s in (1,2,3)]
        new=[self.report(s,1.,'new') for s in (1,2,3)]
        self.assertEqual(repair_gate.gate(new,old,['run'])['status'],'PASS')
        new=[self.report(s,.5,'bad') for s in (1,2,3)]
        self.assertEqual(repair_gate.gate(new,old,['run'])['status'],'FAIL')

    def test_missing_report_or_baseline_refused(self):
        with self.assertRaises(OSError): repair_gate.load_report(self.directory/'missing.json')
        with self.assertRaises(ValueError): repair_gate.suite([],['run'])

    def test_nan_and_forged_denominator_refused(self):
        p=self.report();d=json.loads(p.read_text());d['route_kinds']['run']['complete_rate']=float('nan');p.write_text(json.dumps(d))
        with self.assertRaises(ValueError): repair_gate.load_report(p)
        p=self.report();d=json.loads(p.read_text());d['route_kinds']['run']['episodes']=999;p.write_text(json.dumps(d))
        with self.assertRaises(ValueError): repair_gate.load_report(p)

    def test_same_seed_not_independent_evidence(self):
        p=self.report()
        with self.assertRaises(ValueError): repair_gate.suite([p,p,p],['run'])

    def test_legacy_env_bucket_report_refused(self):
        p=self.directory/'old.json';p.write_text(json.dumps({'route_kinds':{'run':{'envs':64,'complete_rate':1}}}))
        with self.assertRaises(ValueError): repair_gate.load_report(p)

    def test_smoke_missing_guard_refused(self):
        p=self.directory/'log';p.write_text('Learning iteration 249/250\n')
        with self.assertRaises(ValueError): repair_gate.smoke(p,250)

    def test_smoke_complete_finite_guards(self):
        p=self.directory/'log';p.write_text('Learning iteration 249/250\nclosure_err_session_max_m: 0.001\nmimic_err_session_max_rad: 0.002\n')
        self.assertEqual(repair_gate.smoke(p,250)['status'],'PASS_SMOKE_ONLY')

    def test_newest_actor_input_layout_matches_task_terms(self):
        # Parse the shipped snapshot copied into evidence by the packager when present.
        source=ROOT/'evidence/mod4_task.py'
        if not source.exists(): self.skipTest('packaging validation adds the frozen task source')
        tree=ast.parse(source.read_text(encoding='utf8'))
        cfg=next(n for n in ast.walk(tree) if isinstance(n,ast.ClassDef) and n.name=='PolicyCfg')
        names=[n.targets[0].id for n in cfg.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call)]
        self.assertEqual(names,[k for k,_ in POLICY_TERMS])


if __name__=='__main__':
    unittest.main(verbosity=2)
