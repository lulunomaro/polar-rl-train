"""CPU fixtures only; all invocations preserve source snapshots and independent reports."""
from pathlib import Path
from types import SimpleNamespace as NS
from dataclasses import replace
import ast,hashlib,importlib,json,math,sys,time,traceback,unittest
import torch

HERE=Path(__file__).resolve().parent;T=HERE.parent.parent
SOURCE=T/"H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/e2/job0/runtime/isaac/mod4"
E=None;A=None


def fixture(modes=("stand","straight","pure","moving","transition")):
    n=len(modes);z=torch.zeros(n);one=torch.ones(n)
    packed=torch.zeros((n,73));packed[:,3]=1;packed[:,2]=.25
    flags=torch.zeros((n,5));command=torch.zeros((n,3));omega=torch.zeros(n)
    alpha=torch.linspace(-.7,.7,n)
    for i,mode in enumerate(modes):
        if mode=="stand":flags[i,0]=1
        if mode=="straight":command[i,0]=.3
        if mode in ("pure","transition"):flags[i,2]=1;omega[i]=-4.;command[i,2]=-4.
        if mode=="moving":flags[i,3]=1;omega[i]=4.;command[i,0]=torch.cos(alpha[i]);command[i,2]=4.
        if mode=="transition":flags[i,4]=1;command[i,2]=0
    return E.ActualSnapshot(packed,torch.arange(n*18).reshape(n,3,2,3).float(),torch.zeros((n,30)),command,flags,
        alpha,omega,one*.02,one*.5,one*1.5,one*.25,z.clone(),one*12,z.clone(),torch.zeros((3,n,4)),z.clone(),z.clone(),
        torch.zeros((3,n,2)),z.clone(),z.clone(),torch.zeros((n,6))).validate()


def ast_function(path,name,namespace):
    tree=ast.parse(path.read_text(encoding="utf8"));node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name)
    module=ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[]));exec(compile(module,str(path)+":isolated_pure_function","exec"),namespace)
    return namespace[name]


class E2Contracts(unittest.TestCase):
    def test01_exact_source_projection_and_transition_functions(self):
        body=ast_function(SOURCE/"spin_translation_math.py","body_command",dict(torch=torch))
        yaw=ast_function(SOURCE/"e2_directional_spin_runtime_v1.py","transition_yaw",dict(torch=torch))
        heading=torch.tensor([-math.pi,-math.pi/2,0.,.7,math.pi]);alpha=torch.tensor([0.,-.3,.1,.8,-.2])
        actual=E.body_command(torch.full_like(alpha,.5),alpha,heading,torch.full_like(alpha,1.5))
        expected=body(.5,alpha,heading,1.5)
        for a,b in zip(actual,expected):torch.testing.assert_close(a,b)
        phase=torch.tensor([0.,.5,1.,4.,4.5,5.,6.,6.5,7.,10.,10.5,11.,12.])
        torch.testing.assert_close(E.transition_yaw(phase,-4.),yaw(phase,-4.))
        self.assertAlmostEqual(float(E.transition_yaw_integral(torch.tensor(12.))),0.)

    def test02_complete_turn_signed_world_progress_and_cross_ripple(self):
        for rate in (-4.,4.):
            alpha=torch.tensor(.6);heading=torch.tensor(-.3);omega=torch.tensor(rate);v=torch.tensor(.5)
            period=2*math.pi/abs(rate);path,_=E.planned_world_moving_path(torch.tensor(period),heading,alpha,v,omega)
            along,cross=E.project_world_velocity(path/period,alpha)
            self.assertAlmostEqual(float(along),.5,places=5);self.assertAlmostEqual(float(cross),0.,places=5)
        # At yaw45deg and alpha0, the lawful instantaneous world velocity is(.5,.5).
        _,velocity=E.planned_world_moving_path(torch.tensor(0.),torch.tensor(math.pi/4),torch.tensor(0.),torch.tensor(.5),torch.tensor(4.))
        torch.testing.assert_close(velocity,torch.tensor([.5,.5]))
        self.assertGreater(float(abs(E.planned_world_moving_path(torch.tensor(.2),torch.tensor(0.),torch.tensor(0.),torch.tensor(.5),torch.tensor(4.))[0][1])),0)

    def test03_zero_yaw_limit_is_instantaneous_projection_not_fake_mean(self):
        path,velocity=E.planned_world_moving_path(torch.tensor(2.),torch.tensor(.7),torch.tensor(-.4),torch.tensor(.5),torch.tensor(0.))
        torch.testing.assert_close(path,velocity*2)
        self.assertFalse(torch.allclose(path,torch.tensor([math.cos(-.4),math.sin(-.4)])))

    def test04_real_context93_and_native_dimensions_are_derived(self):
        snap=fixture();book=E.E2ReferenceBook();frames=book.register(snap,torch.arange(5));mdp=E.E2GoalMdp(book)
        ctx=snap.context93();self.assertEqual(tuple(ctx.shape),(5,93))
        self.assertEqual(E.CONTEXT_SLICES["command_time_left"],(92,93))
        state=E.unpack73(snap.packed73);action=torch.zeros((5,6));obs=mdp.obs(state,action,ctx,frames)
        self.assertEqual(tuple(obs.shape),(5,175));self.assertEqual(tuple(mdp.critic_features(state,frames,torch.tanh(ctx)).shape),(5,170))
        self.assertEqual(tuple(mdp.goal(frames,3).shape),(5,219));self.assertTrue(bool((mdp.goal(frames,1)[:,13:]==0).all()))
        self.assertEqual(mdp.contract_manifest()["reference_kind"],"declared_command_kinematic_hypothesis_not_measured_demonstration")

    def test05_root_pack_preserves_raw_provenance_and_joint_velocity(self):
        root=torch.arange(26).reshape(2,13).float();q=torch.arange(60).reshape(2,30).float();dq=-q
        origin=torch.tensor([[2.,3.,4.],[5.,6.,7.]])
        original=root.clone();packed=E.pack_actual_root_xyzw(root,q,dq,origin)
        torch.testing.assert_close(root,original);torch.testing.assert_close(packed[:,:3],root[:,:3]-origin)
        torch.testing.assert_close(packed[:,3:7],root[:,[6,3,4,5]]);torch.testing.assert_close(packed[:,7:13],root[:,7:13])
        torch.testing.assert_close(packed[:,13:43],q);torch.testing.assert_close(packed[:,43:73],dq)

    def test06_goal_clock_profile_and_resampling_boundary(self):
        snap=fixture(("transition",));snap=replace(snap,command_time_left=torch.tensor([.1]))
        book=E.E2ReferenceBook();f=book.register(snap,torch.tensor([0]));mdp=E.E2GoalMdp(book)
        self.assertTrue(bool(mdp.valid_imagination_start(f,3)));self.assertFalse(bool(mdp.valid_imagination_start(f,5)))
        command=book.effective_command(E.unpack73(snap.packed73),f+25)
        self.assertAlmostEqual(float(command[0,2]),-2.,places=5)
        self.assertEqual(E.CONTROL_DT,.02);self.assertEqual(E.PHYSICS_DT*E.DECIMATION,.02)
        # Same-device learner MDP shares the live append-only plan book.
        other=mdp.to("cpu");book.register(fixture(("stand",)),torch.tensor([0]));self.assertEqual(len(other.book.table),2)

    def test07_declared_world_ripple_is_not_penalized_as_instantaneous_drift(self):
        snap=fixture(("moving",));q=snap.packed73.clone();heading=math.pi/4
        q[:,3]=math.cos(heading/2);q[:,6]=math.sin(heading/2)
        snap=replace(snap,packed73=q,world_direction=torch.tensor([0.]),command_body3=torch.tensor([[math.sqrt(.5),0.,4.]]))
        book=E.E2ReferenceBook();f=book.register(snap,torch.tensor([0]));mdp=E.E2GoalMdp(book)
        state=list(E.unpack73(q));state[2]=torch.tensor([[.5,.5,0.]]);state[3]=torch.tensor([[0.,0.,4.]])
        zero=torch.zeros((1,6));good=mdp.objective_terms(tuple(state),f,zero,zero)
        self.assertLess(float(good["forward_cost"]),1e-10);self.assertEqual(float(good["declared_path_cost"]),0.)
        state[2]=torch.tensor([[.5,0.,0.]])
        bad=mdp.objective_terms(tuple(state),f,zero,zero);self.assertGreater(float(bad["forward_cost"]),.1)
        state[3]=torch.tensor([[0.,0.,-4.]])
        self.assertGreater(float(mdp.objective_terms(tuple(state),f,zero,zero)["yaw_cost"]),100.)

    def test08_imagination_objective_has_finite_nonzero_state_gradients(self):
        snap=fixture(("straight",));book=E.E2ReferenceBook();f=book.register(snap,torch.tensor([0]));mdp=E.E2GoalMdp(book)
        values=list(E.unpack73(snap.packed73));velocity=torch.zeros((1,3),requires_grad=True);values[2]=velocity
        zero=torch.zeros((1,6));reward=mdp.reward(tuple(values),f,zero,zero);grad,=torch.autograd.grad(reward.sum(),(velocity,))
        self.assertTrue(bool(torch.isfinite(grad).all()));self.assertGreater(float(grad[0,0]),0)
        self.assertLessEqual(float(reward.max()),mdp.max_step_reward)

    def test09_no_hidden_H1_fields_and_invalid_source_kind_rejected(self):
        snap=fixture(("stand",))
        with self.assertRaisesRegex(E.E2ContractError,"expert kind"):replace(snap,source_kind="H1_step270").validate()
        text=(HERE/"e2_native_supermimic_candidate_v1.py").read_text()
        for forbidden in ("h1_phase","public_request","takeoff_count","landing_count","lifetime_goal_counter","torch.load(","manual_seed(","randn("):
            self.assertNotIn(forbidden,text)

    def test10_bridge_keeps_action_reward_and_pre_reset_transition_exact(self):
        first=fixture(("moving","straight"));second=replace(first,packed73=first.packed73.clone(),
            phase_elapsed=first.phase_elapsed+.02,command_time_left=first.command_time_left-.02)
        second.packed73[0,0]=0 # source auto-reset state
        second.packed73[1,0]=.01
        terminal=first.packed73.clone();terminal[0,0]=7.;terminal[1,0]=.01
        requested=torch.tensor([[20.,-20.,0.,1.,-9.,9.],[1.,2.,3.,4.,5.,6.]])
        ingress=requested.clamp(-6,6);physical=torch.tensor([12.,34.]);done=torch.tensor([True,False])
        class Vec:
            def step(self,action):self.received=action;return None,physical,done,{}
        vec=Vec();snapshots=iter((first,second));reader=lambda:next(snapshots)
        frame=dict(source_stage="termination_manager_compute_pre_reset",packed73=terminal,action_manager_ingress6=ingress)
        bridge=E.E2NativeBridge(vec,reader,lambda:frame,E.E2ReferenceBook());bridge.init_state();result=bridge.step(requested)
        self.assertIs(vec.received,requested);self.assertIs(result.reward,physical)
        transition=result.info[E.TRANSITION_KEY];torch.testing.assert_close(transition["s1"],terminal)
        torch.testing.assert_close(transition["a"],ingress);torch.testing.assert_close(transition["r"],physical)
        self.assertEqual(float(result.info[E.STATE_KEY]["s"][0,0]),0.)
        self.assertEqual(int(result.info[E.STATE_KEY]["ep_step"][0]),0)
        self.assertTrue(bool((result.info[E.STATE_KEY]["a_prev"][0]==0).all()))

    def test11_plan_draws_are_observed_not_resampled_or_overwritten(self):
        first=fixture(("moving",));next_snapshot=replace(first,phase_elapsed=first.phase_elapsed+.02,
            command_time_left=first.command_time_left-.02,command_body3=first.command_body3+torch.tensor([[.01,0.,0.]]))
        bridge=E.E2NativeBridge(None,None,None,E.E2ReferenceBook(max_plans=2))
        f0=bridge._frames_for(first).clone();old_goal=bridge.book.reference(f0+25).clone()
        f1=bridge._frames_for(next_snapshot).clone();self.assertEqual(int(f1),int(f0)+1);self.assertEqual(len(bridge.book.table),1)
        reset=replace(next_snapshot,phase_elapsed=torch.zeros(1),command_time_left=torch.full((1,),14.))
        bridge._frames_for(reset);self.assertEqual(len(bridge.book.table),2)
        torch.testing.assert_close(bridge.book.reference(f0+25),old_goal)
        with self.assertRaises(E.PlanCapacitySaveRequired):bridge.book.register(first,torch.tensor([0]))
        state=bridge.book.state_dict();restored=E.E2ReferenceBook(max_plans=2);restored.load_state_dict(state)
        torch.testing.assert_close(restored.reference(f0+25),old_goal)

    def test12_source_reader_maps_actual_fields_without_RNG_or_mutation(self):
        snap=fixture(("moving","pure"));n=2
        root=snap.packed73[:,:13].clone();root[:,3:7]=root[:,[4,5,6,3]]
        robot=NS(joint_names=[f"j{i}" for i in range(30)],data=NS(root_state_w=root,joint_pos=snap.packed73[:,13:43],
            joint_vel=snap.packed73[:,43:73],applied_torque=snap.applied_torque30))
        flags={name:snap.flags5[:,i].bool() for i,name in enumerate(E.FLAG_ORDER)}
        class RNGSentinel:
            def get_state(self):raise AssertionError("private RNG must remain untouched")
        term=NS(command=snap.command_body3,world_direction=snap.world_direction,signed_yaw=snap.signed_yaw,
            phase_elapsed=snap.phase_elapsed,progress_goal=.5,body_limit=1.5,manual_evaluation_mode=False,time_left=snap.command_time_left,
            _mode_rng=RNGSentinel(),**flags)
        legs=NS(_hist=snap.leg_delay_history,_lag=snap.leg_delay_lag,_age=snap.leg_delay_age,processed_actions=snap.processed_targets6[:,:4])
        wheels=NS(_hist=snap.wheel_delay_history,_lag=snap.wheel_delay_lag,_age=snap.wheel_delay_age,processed_actions=snap.processed_targets6[:,4:])
        scene=type("Scene",(dict,),{})(robot=robot);scene.env_origins=torch.zeros((n,3))
        env=NS(step_dt=.02,physics_dt=.0025,cfg=NS(decimation=8),scene=scene,
            command_manager=NS(get_term=lambda name:term),action_manager=NS(get_term=lambda name:{"legs":legs,"wheels":wheels}[name]),
            _integrated_contact=NS(history=snap.mean_force_history),_mod4_height_cmd=snap.height_command[:,None])
        before=term.phase_elapsed.clone();actual=A.actual_snapshot_from_source(env,torch.zeros(n),expected_joint_names=robot.joint_names)
        torch.testing.assert_close(actual.packed73,snap.packed73);torch.testing.assert_close(actual.context93(),snap.context93())
        torch.testing.assert_close(term.phase_elapsed,before)

    def test13_complete_bridge_book_tensor_roundtrip_is_not_PhysX_resume(self):
        snapshot=fixture(("moving","transition"));book=E.E2ReferenceBook()
        original=E.E2NativeBridge(None,lambda:snapshot,None,book);original.init_state()
        saved=original.state_dict();self.assertTrue(saved["not_exact_PhysX_restart"])
        restored=E.E2NativeBridge(None,None,None,E.E2ReferenceBook());restored.load_state_dict(saved)
        torch.testing.assert_close(restored.frames,original.frames)
        torch.testing.assert_close(restored.state.info[E.STATE_KEY]["xi"],original.state.info[E.STATE_KEY]["xi"])
        torch.testing.assert_close(restored.supermimic_mdp.goal(restored.frames+20,1),original.supermimic_mdp.goal(original.frames+20,1))
        # Mutating the exported tensors cannot alter live bridge/reference state.
        saved["frames"].add_(100)
        torch.testing.assert_close(restored.frames,original.frames)

    def test14_transition_command_changes_do_not_create_fake_new_random_plans(self):
        first=fixture(("transition",));next_snapshot=replace(first,phase_elapsed=first.phase_elapsed+.02,
            command_time_left=first.command_time_left-.02,command_body3=torch.tensor([[0.,0.,-.08]]))
        bridge=E.E2NativeBridge(None,None,None,E.E2ReferenceBook());f0=bridge._frames_for(first).clone()
        f1=bridge._frames_for(next_snapshot)
        self.assertEqual(len(bridge.book.table),1);self.assertEqual(int(f1),int(f0)+1)

    def test15_unobserved_joint_pose_is_not_an_imitation_target(self):
        snap=fixture(("stand",));book=E.E2ReferenceBook();f=book.register(snap,torch.tensor([0]));mdp=E.E2GoalMdp(book)
        state=list(E.unpack73(snap.packed73));zero=torch.zeros((1,6));before=mdp.reward(tuple(state),f,zero,zero)
        state[4]=state[4]+.5
        torch.testing.assert_close(mdp.reward(tuple(state),f,zero,zero),before)
        self.assertTrue(bool((mdp.goal(f,1)[:,13:]==0).all()))


class Result(unittest.TextTestResult):
    def __init__(self,*a,**k):super().__init__(*a,**k);self.records=[]
    def addSuccess(self,t):super().addSuccess(t);self.records.append(dict(test=t.id(),status="PASS"))
    def addFailure(self,t,e):super().addFailure(t,e);self.records.append(dict(test=t.id(),status="FAIL",error=self._exc_info_to_string(e,t)))
    def addError(self,t,e):super().addError(t,e);self.records.append(dict(test=t.id(),status="ERROR",error=self._exc_info_to_string(e,t)))


def main():
    global E,A
    trial="E2_NATIVE_SOURCE_CPU_"+str(time.time_ns());out=HERE/trial;out.mkdir(exist_ok=False);source=[]
    for path in sorted(HERE.glob("*.py")):
        raw=path.read_bytes();(out/path.name).write_bytes(raw);source.append(dict(path=str(out/path.name),SHA256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
    try:
        E=importlib.import_module("e2_native_supermimic_candidate_v1");A=importlib.import_module("e2_source_readonly_adapter_v1")
        result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
        contract=E.E2GoalMdp(E.E2ReferenceBook()).contract_manifest()
        path=out/"E2_NATIVE_SOURCE_CPU_RESULT.json"
        report=dict(trial_id=trial,status="PASS" if result.wasSuccessful() else "FAIL",source=source,tests=result.records,
            tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),contract=contract,
            actual_source_SDK_robot_physics_policy_optimizer_or_GPU_executed=False,
            fixtures="synthetic_CPU_algebra_and_readonly_adapter_only_not_measured_demonstrations",
            runtime_GO_and_skill_graduation="pending",git_archive_state="pending_root_stage_archive")
        with path.open("x",encoding="utf8") as f:json.dump(report,f,indent=2)
        print(json.dumps(dict(report=str(path),SHA256=hashlib.sha256(path.read_bytes()).hexdigest(),status=report["status"],tests=result.testsRun)))
        return 0 if result.wasSuccessful() else 1
    except BaseException:
        with (out/"E2_CPU_RUNNER_ORIGINAL_ERROR.json").open("x",encoding="utf8") as f:json.dump(dict(trial_id=trial,error=traceback.format_exc(),source=source,git_archive_state="pending_root_stage_archive"),f,indent=2)
        raise


if __name__=="__main__":sys.exit(main())
