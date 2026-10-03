"""Meaningful negative gates, accounting and whitelist equivalence tests."""
import copy, importlib.util, os, sys, types, unittest
from pathlib import Path
import torch
from autonomy_policy import next_action, settle_segment, safety_veto, DR_PROFILES

class GateTests(unittest.TestCase):
    def test_cannot_promote_unskilled_or_unpaired_or_short_budget(self):
        for args in [(6,'white_v1',1,True,10000,[]),(6,'white_v1',2,False,10000,[]),(6,'white_v1',2,True,5000,[])]:
            self.assertEqual(next_action(*args),('continue',None))
    def test_separate_dr_and_rate(self):
        self.assertEqual(next_action(6,'white_v1',2,True,10000,[]),('dr_trial','white_v2'))
        self.assertEqual(next_action(6,'white_v2',2,True,10000,[]),('rate_preflight',8))
        self.assertEqual(next_action(8,'white_v2',2,True,10000,[]),('dr_trial','white_v3'))
        self.assertEqual(next_action(6,'white_v1',2,True,10000,['white_v2']),('rate_preflight',8))
    def test_single_tail_no_new_authority_or_double_charge(self):
        b={'authorized_training_seconds':180000.,'charged_training_seconds':100.,
           'extensions':[{'id':'original'}], 'active_segment':{'pid':12,'accounted_through_epoch':50.}}
        self.assertEqual(settle_segment(b,12,55.),5.)
        self.assertEqual(b['charged_training_seconds'],105.)
        self.assertEqual(b['authorized_training_seconds'],180000.)
        self.assertEqual(b['extensions'],[{'id':'original'}])
        with self.assertRaises(ValueError):settle_segment(b,12,60.)
    def test_wrong_pid_or_backwards_end_does_not_mutate(self):
        for pid,end in [(13,55.),(12,49.)]:
            b={'charged_training_seconds':100.,'active_segment':{'pid':12,'accounted_through_epoch':50.}}
            old=copy.deepcopy(b)
            with self.assertRaises(ValueError):settle_segment(b,pid,end)
            self.assertEqual(b,old)
    def test_severe_individual_not_hidden_in_group(self):
        self.assertFalse(safety_veto({'alive':[True]*8,'per_environment':{'peak_tilt':[1]*7+[29.5]}}))
        self.assertFalse(safety_veto({'alive':[True]*7+[False]}))
        self.assertFalse(safety_veto({'nonfinite':True}))
    def test_flat_extrapolation_still_diagnostic(self):
        r={'mode':'deterministic_policy','groups':[{'command_vx':1.5},{'command_vx':2.}],
           'per_environment':{'group_ids':[0,1],'alive':[True,False],'max_tilt':[1.,29.5],
                              'longest_both_low_force_s_substep':[.01,.03]}}
        self.assertTrue(safety_veto(r))

def load_dr(path,name):
    managers=types.ModuleType('isaaclab.managers')
    class Manager:
        def __init__(self,cfg,env):pass
    managers.ManagerTermBase=Manager;managers.EventTermCfg=lambda **kw:kw
    warp=types.ModuleType('warp');warp.float32=torch.float32;warp.int32=torch.int32
    warp.from_torch=lambda x,**kw:x;warp.to_torch=lambda x:x
    sys.modules['warp']=warp;sys.modules['isaaclab']=types.ModuleType('isaaclab');sys.modules['isaaclab.managers']=managers
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def fake_env(n=8192):
    ns=types.SimpleNamespace
    class View:
        max_shapes=4
        link_paths=[['a','b','c','d']]
        def __init__(self):
            self.mass=torch.full((n,4),2.);self.inertia=torch.full((n,4,9),.1)
            self.material=torch.zeros(n,4,3);self.material[:,:,:2]=.9
        def get_masses(self):return self.mass
        def get_inertias(self):return self.inertia
        def get_material_properties(self):return self.material
        def set_material_properties(self,m,ids):self.material[ids.long()]=m[ids.long()]
    view=View()
    acts={k:ns(stiffness=torch.ones(n,w)*20,damping=torch.ones(n,w)) for k,w in [('legs',4),('wheels',2)]}
    r=ns(root_view=view,data=ns(body_com_pos_b=torch.zeros(n,4,3)),actuators=acts,
         body_names=['base','left_wheel','right_wheel','guide'],
         _physics_sim_view=ns(create_rigid_body_view=lambda p:ns(max_shapes=1)))
    r.set_masses_index=lambda masses,env_ids:view.mass.__setitem__(env_ids,masses)
    r.set_inertias_index=lambda inertias,env_ids:view.inertia.__setitem__(env_ids,inertias)
    return ns(scene={'robot':r},cfg=ns(seed=20261003),device='cpu',num_envs=n)

class DRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d=Path(__file__).parent
        cls.old=load_dr(d/'mild_dr_original.py','old_dr');cls.new=load_dr(d/'mild_dr.py','new_dr')
    def test_white1_bit_exact_resets_rng_and_actual_arrays(self):
        os.environ['RM_MILD_DR_PROFILE']='white_v1'
        a,b=fake_env(),fake_env();old=self.old.MildDR(None,a);new=self.new.MildDR(None,b)
        for ids in [None,torch.arange(0,a.num_envs,2),None]:
            old(a,ids);new(b,ids)
            for key in ['factor','mu','nominal','reset_count']:
                self.assertTrue(torch.equal(getattr(old,key),getattr(new,key)),key)
            for key in ['mass','inertia','material']:
                self.assertTrue(torch.equal(getattr(a.scene['robot'].root_view,key),getattr(b.scene['robot'].root_view,key)))
            for name in ['legs','wheels']:
                self.assertTrue(torch.equal(old.output[name],new.output[name]))
            self.assertTrue(torch.equal(old.generator.get_state(),new.generator.get_state()))
            self.assertTrue(torch.equal(old.cpu_generator.get_state(),new.cpu_generator.get_state()))
            self.assertTrue(old.audit()['actual_parameters_pass'] and new.audit()['actual_parameters_pass'])
    def test_wider_whitelist_parameters_and_clean_nominal(self):
        for profile in ['white_v2','white_v3']:
            os.environ['RM_MILD_DR_PROFILE']=profile;e=fake_env();dr=self.new.MildDR(None,e);dr(e,None)
            audit=dr.audit();self.assertEqual(audit['profile'],profile)
            bounds=DR_PROFILES[profile]
            self.assertTrue(bounds['mass'][0]<=float(dr.factor.min())<=float(dr.factor.max())<=bounds['mass'][1])
            self.assertTrue(bounds['friction'][0]-1e-6<=float(dr.mu.min())<=float(dr.mu.max())<=1.00001)
            self.assertTrue(torch.equal(dr.factor[dr.nominal],torch.ones_like(dr.factor[dr.nominal])))
            for name in ['legs','wheels']:
                self.assertTrue(torch.equal(dr.output[name][dr.nominal],torch.ones_like(dr.output[name][dr.nominal])))
            self.assertEqual(audit['errors']['local_com_position_error'],0.)
            self.assertEqual(audit['errors']['nonwheel_material_error'],0.)
    def test_unknown_profile_and_legacy_bundle_rejected(self):
        cfg=types.SimpleNamespace(events=types.SimpleNamespace())
        os.environ['RM_MILD_DR_PROFILE']='all_dr';os.environ['RM_DR_OFF']='1'
        with self.assertRaises(ValueError):self.new.configure(cfg)
        os.environ['RM_MILD_DR_PROFILE']='white_v2';os.environ['RM_DR_OFF']='0'
        with self.assertRaises(RuntimeError):self.new.configure(cfg)
    def test_gain_after_rating_is_clipped_for_every_whitelist(self):
        # Execute the real actuator method against a bounded motor envelope.
        import ast
        task=Path(__file__).with_name('mod4_task.py').read_text(encoding='utf-8')
        tree=ast.parse(task)
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Mod4DCMotor')
        method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_clip_effort')
        class Parent:
            def _clip_effort(self,x):return x.clamp(-3.,3.)
        module=ast.Module(body=[ast.ClassDef(name='Motor',bases=[ast.Name(id='Parent',ctx=ast.Load())],
             keywords=[],body=[method],decorator_list=[])],type_ignores=[])
        namespace={'Parent':Parent,'torch':torch,'os':os}
        exec(compile(ast.fix_missing_locations(module),'actuator','exec'),namespace)
        for profile in DR_PROFILES:
            os.environ['RM_MILD_DR_PROFILE']=profile
            motor=namespace['Motor']();motor.episode_scale=1.1;motor.step_scale=1.
            self.assertEqual(motor._clip_effort(torch.tensor([100.]))[0],3.)

class WorkflowTests(unittest.TestCase):
    def load_workflow(self):
        from tempfile import TemporaryDirectory
        self.folder=TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        root=Path(self.folder.name)
        base=types.SimpleNamespace(STATE={},atomic_json=lambda *a:None)
        spin=types.SimpleNamespace()
        helpers=types.SimpleNamespace(read=lambda p:{},identity=lambda p:None)
        rate=types.SimpleNamespace(base=base,spin=spin,helpers=helpers,ROOT=root,CODE=root,REPORTS=root,
                                  CANONICAL=root/'budget.json',PROBES=())
        old=sys.modules.get('supervise_spin_rate');sys.modules['supervise_spin_rate']=rate
        try:
            spec=importlib.util.spec_from_file_location('workflow_under_test',Path(__file__).with_name('supervise_autonomy.py'))
            m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        finally:
            if old is None:sys.modules.pop('supervise_spin_rate',None)
            else:sys.modules['supervise_spin_rate']=old
        m.persist=lambda:None;m.idle=lambda:None;m.verify=lambda:None
        m.fresh_label=lambda kind:kind
        m.base.checkpoint=lambda ck:{'path':str(ck),'sha256':str(ck),'iteration_stored':1}
        return m
    def test_failed_eight_restores_six_and_blocks_eight(self):
        m=self.load_workflow();box={'cap':8.,'done':False,'trained_source':None}
        m.S={'profile':'white_v2','chosen_checkpoint':'failed8.pt','consecutive':0,'failed_blocks':2,
             'dr_rejected':[],'rate_rejected':[],
             'mature':{'checkpoint':'mature6.pt','profile':'white_v2','cap':6.}}
        m.read=lambda p:m.S;m.rate.current_limit=lambda:box['cap']
        m.rate.set_limit=lambda cap,reason:box.__setitem__('cap',cap)
        m.set_profile=lambda profile,reason:m.S.__setitem__('profile',profile)
        m.remaining=lambda:0 if box['done'] else 9000
        m.current_decision=lambda ck:(True,False)
        def train(ck,*a,**kw):
            box['trained_source']=str(ck);box['done']=True;return ck
        m.training=train;m.finish=lambda *a:None;m.helpers.acquire=lambda p:None
        m.controller()
        self.assertEqual(box['cap'],6.)
        self.assertEqual(box['trained_source'],'mature6.pt')
        self.assertIn(8.,m.S['rate_rejected'])
        self.assertNotIn(6.,m.S['rate_rejected'])
    def test_flat_pair_supports_original_metadata_without_profile_field(self):
        m=self.load_workflow();m.S={'profile':'white_v1'};m.rate.current_limit=lambda:6.
        m.gate=lambda r,kind:True
        def probe(ck,label,kind,profile,seed):
            r={'reset_joint_pos_before_physics':[0.],'reset_root_before_physics':[.25]}
            if profile!='nominal':
                r['mild_initial_parameters']={'actual_parameters_pass':True}
                r['mild_final_parameters']={'actual_parameters_pass':True}
            return r
        m.probe=probe
        self.assertTrue(m.pairs(Path('mature6.pt'),'paired',('nominal','white_v1'),kinds=('flat',)))

if __name__=='__main__':
    torch.set_num_threads(1)
    suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
