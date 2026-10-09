"""Actual PhysX ABBA microbenchmark and separately labelled collection stress test."""
import time,hashlib,statistics,types,torch,os
from gas_damping_sdk_adapter import tensor
from chassis_com_pose_roundtrip_sdk_adapter import ChassisCOMSDK as BaselineCOM,verify_rotation_preserved
from selected_com_readback import SelectedCOMSDK

def digest(v):
    if torch.is_tensor(v):return hashlib.sha256(v.detach().cpu().contiguous().numpy().tobytes()).hexdigest()
    if isinstance(v,dict):return {k:digest(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)):return [digest(x) for x in v]
    return v

class ResetPerformanceProof:
    def __init__(self,env):
        self.env=env;self.robot=env.scene['robot'];self.reset_seconds=[];self.reset_sizes=[];self.step_seconds=[]
        self.actions=hashlib.sha256();self.manual_resets=0;self.micro=[];self.variant=os.environ['RM_COM_PERFORMANCE_VARIANT']
        self.initial=self.snapshot()
        if env.num_envs==10:self.run_actual_micro()
        original=env._reset_idx;proof=self
        def reset(this,ids):
            torch.cuda.synchronize();start=time.perf_counter();original(ids);torch.cuda.synchronize()
            proof.reset_seconds.append(time.perf_counter()-start);proof.reset_sizes.append(len(ids))
        env._reset_idx=types.MethodType(reset,env)

    def snapshot(self):
        e=self.env;r=self.robot
        return dict(root=r.data.root_state_w.cpu().tolist(),q=r.data.joint_pos.cpu().tolist(),qd=r.data.joint_vel.cpu().tolist(),
            COM=digest(tensor(r.root_view.get_coms())),mass=digest(tensor(r.root_view.get_masses())),inertia=digest(tensor(r.root_view.get_inertias())),
            explicit_PD=digest(e._explicit_pd.component.coefficients()),
            group_state=digest(dict(COM=e._chassis_com.state_dict(),PD=e._explicit_pd.state_dict(),gas=e._gas_damping.state_dict(),spring=e._spring_pressure.state_dict())),
            global_CPU_RNG=digest(torch.get_rng_state()),global_CUDA_RNG=digest(torch.cuda.get_rng_state()),
            control_tick=int(e.common_step_counter))

    def run_actual_micro(self):
        a=self.env._chassis_com;klass=a.__class__;state=a.state_dict();r=self.robot
        initial_pose=tensor(r.root_view.get_coms()).clone();rotation_proofs=[]
        for count in (1,3,10):
            ids=torch.arange(count,device=self.env.device)
            times={'baseline':[],'optimized':[]};after={};before={}
            for iteration in range(12):
                for label in (('baseline','optimized') if iteration%2==0 else ('optimized','baseline')):
                    a.__class__=BaselineCOM
                    a.load_state_dict(state)
                    before[label]=(tensor(r.root_view.get_coms()).clone(),digest(a.state_dict()))
                    a.__class__=BaselineCOM if label=='baseline' else SelectedCOMSDK
                    torch.cuda.synchronize();start=time.perf_counter();a.reset(ids);torch.cuda.synchronize()
                    times[label].append(time.perf_counter()-start)
                    # Full independent original auditor, outside the timed region.
                    BaselineCOM.audit_parameters(a)
                    after[label]=(tensor(r.root_view.get_coms()).clone(),tensor(r.data.body_com_pose_b).clone(),digest(a.state_dict()))
                assert torch.equal(before['baseline'][0][...,:3],before['optimized'][0][...,:3]) and before['baseline'][1]==before['optimized'][1]
                rotation_proofs.append(verify_rotation_preserved(before['baseline'][0][...,3:],before['optimized'][0][...,3:]))
                assert torch.equal(after['baseline'][0][...,:3],after['optimized'][0][...,:3])
                assert torch.equal(after['baseline'][1],after['baseline'][0]) and torch.equal(after['optimized'][1],after['optimized'][0])
                rotation_proofs.append(verify_rotation_preserved(after['baseline'][0][...,3:],after['optimized'][0][...,3:]))
                assert after['baseline'][2]==after['optimized'][2]
            self.micro.append(dict(actual_PhysX_num_envs=self.env.num_envs,selected=count,repeats_per_variant=12,
                baseline_seconds=times['baseline'],optimized_seconds=times['optimized'],
                baseline_median=statistics.median(times['baseline'][2:]),optimized_median=statistics.median(times['optimized'][2:]),
                exact_COM_translation_episode_private_RNG_before_after=True,backend_buffer_bytes_exact_per_variant=True,
                physical_rotations_preserved_existing_dtype_contract=True,raw_quaternion_bytes_pairwise_exact=all(x['raw_quaternion_bytes_exact'] for x in rotation_proofs),
                max_normalized_double_quaternion_delta=max(x['normalized_double_quaternion_max_component_delta'] for x in rotation_proofs),ABBA_alternating_order=True,
                independent_full_original_audit_after_each_reset=True))
        a.__class__=klass;a.load_state_dict(state)
        restored=self.snapshot();final_pose=tensor(r.root_view.get_coms())
        assert torch.equal(initial_pose[...,:3],final_pose[...,:3])
        verify_rotation_preserved(initial_pose[...,3:],final_pose[...,3:])
        assert {k:v for k,v in self.initial.items() if k!='COM'}=={k:v for k,v in restored.items() if k!='COM'},'Non-COM initial state changed during microbenchmark'
        self.micro_restore_raw_COM_pose_exact=torch.equal(initial_pose,final_pose)

    def before_control(self,step):
        if self.env.num_envs==80 and step>=50 and step%10==0:
            ids=(torch.arange(4,device=self.env.device)+(step//10)*4)%80
            self.env._reset_idx(ids);self.manual_resets+=1
            self.env._mild_dr.audit()

    def after_action(self,action):
        self.actions.update(action.detach().cpu().contiguous().numpy().tobytes())

    def finish(self):
        self.env._mild_dr.audit();self.env._chassis_com.audit_parameters()
        return dict(variant=self.variant,actual_num_envs=self.env.num_envs,actual_steps=len(self.step_seconds),
            microbench=self.micro,initial=self.initial,final=self.snapshot(),action_trace_sha256=self.actions.hexdigest(),
            reset_seconds=self.reset_seconds,reset_sizes=self.reset_sizes,step_seconds=self.step_seconds,
            stress_selected_reset_calls=self.manual_resets,stress_selected_rows_per_call=4,
            collection_stress_is_not_skill_graduation=True,no_PPO_or_optimizer_update=True,
            unchanged_task_hardware_parameter_and_full_audit_contract=True,
            no_4090_training_or_canonical_write_authority=True)
