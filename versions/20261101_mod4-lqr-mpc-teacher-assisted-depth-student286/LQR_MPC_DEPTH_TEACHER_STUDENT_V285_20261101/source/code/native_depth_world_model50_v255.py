"""Native SuperMimic WM pretraining from frozen own-MOD4 PPO teacher controls.



Only the original WM tensor kernels/replay semantics are reused. This stage does

not pretend that WM warmup has already trained or qualified a native policy.

"""

from pathlib import Path

import importlib,sys,types

import torch





def load_native_kernels(source):

    name='supermimic_wheel_leg_v3'

    if name not in sys.modules:

        module=types.ModuleType(name);module.__path__=[str(Path(source)/name)]

        sys.modules[name]=module

    geometry=importlib.import_module(name+'.geometry')

    world=importlib.import_module(name+'.augmented_wheel_leg_world_model_v1')

    replay=importlib.import_module(name+'.replay')

    return geometry,world,replay





class DepthTeacherWorldModel:

    """Build the original augmented WM with flat-ground coordinate features."""

    @staticmethod

    def make(base,context_dim,hidden):

        class FlatModel(base):

            def terrain_relative(self,state):

                p=state[0]

                # No privileged terrain feature: observed depth9 is in context40. This is not the old flat-ground assumption.

                return torch.zeros_like(p)

        return FlatModel(context_dim=context_dim,hidden=hidden,num_joints=30,

                         auxiliary_dim=54,action_dim=6,edge_x_m=0,platform_top_z_m=0)





class DepthTeacherWM50:

    def __init__(self,source,device,*,seed,envs=2048,window=32,batch=1024,

                 hidden=(512,512,512),learning_rate=1e-4):

        if not (isinstance(envs,int) and envs>0 and 1<=window<=64 and batch>0):raise ValueError('Invalid bounded replay dimensions')

        self.device=torch.device(device);self.envs=envs;self.window=window;self.batch=batch

        self.last_physics_tick=None

        self.geometry,world,replay=load_native_kernels(source)

        devices=[self.device.index or 0] if self.device.type=='cuda' else []

        # Initialization and replay sampling never consume the teacher's streams.

        with torch.random.fork_rng(devices=devices):

            torch.manual_seed(seed)

            self.model=DepthTeacherWorldModel.make(world.AugmentedWheelLegWorldModel,40,hidden).to(self.device)

        self.optimizer=torch.optim.Adam(self.model.parameters(),lr=learning_rate)

        self.generator=torch.Generator(device=self.device);self.generator.manual_seed(seed+1)

        self.buffer=replay.ReplayBuffer(64,envs,self.device,num_joints=30,context_dim=40,action_dim=6,state_dim=127)

        self.floor=world.learner_error_floor(world.WheelLegStateLayout()).to(self.device)

        self.updates=0;self.controls=0

        self.protocol=dict(kind='NATIVE_SUPERMIMIC_OWN_FULLSTATE_DEPTH_CONTEXT40_WM50',

            physics_us=2500,policy_us=20000,physics_callbacks=8,

            state127=True,static31=True,depth9=True,context40=True,actions6=True,window=window,batch=batch,

            time_loss_reduction='sum time / batch, original native loss semantics',

            gradient_clip=1.0,hidden=list(hidden),new_WM_parameters_and_optimizer=True,

            original_PPO_actor_critic_STD_17Adam_frozen=True,policy_BPTT_updates=0)



    def add(self,transition,*,physics_end_tick,physics_us,feedback_samples,producer,synthetic_CPU_test=False):
        expected='SYNTHETIC_CPU_INTERFACE_ONLY' if synthetic_CPU_test else 'ACTUAL_OWN_MOD4_FULLSTATE_DEPTH_PRODUCER'
        if producer.get('kind')!=expected or producer.get('plant')!='own_MOD4_live_USD':raise ValueError('Own fullstate/depth producer required')
        if not all(producer.get(k) for k in ('run_id','generation','source_admission_SHA')):raise ValueError('Missing actual producer binding')
        if not 0<=producer['max_depth_age_seconds']<=.20:raise ValueError('Future/stale depth')


        # A protocol label alone cannot convert100Hz transitions into50Hz truth.

        if type(physics_end_tick) is not int or physics_end_tick<8 or physics_end_tick%8 or physics_us!=2500 or feedback_samples!=2:

            raise ValueError('Actual eight2500us callbacks and two100Hz feedback samples required')

        if self.last_physics_tick is not None and physics_end_tick!=self.last_physics_tick+8:

            raise ValueError('Duplicate, skipped, or100Hz transition clock')

        if not set(self.buffer.fields)<=set(transition):raise ValueError('Incomplete measured transition')

        fields={}

        for key,(width,dtype) in self.buffer.fields.items():

            value=transition[key]

            tail=(width,) if isinstance(width,int) else width

            if not torch.is_tensor(value) or value.ndim!=1+len(tail) or value.shape[0]<self.envs or tuple(value.shape[1:])!=tail or value.dtype!=dtype or value.device!=self.device:

                raise ValueError('Wrong transition shape/type/device '+key)

            if (value.is_floating_point() or value.is_complex()) and not torch.isfinite(value).all():raise ValueError('Nonfinite measured transition '+key)

            fields[key]=value[:self.envs].detach()

        s=self.geometry.unflatten_state(fields['s']);s1=self.geometry.unflatten_state(fields['s1'])

        # Original output labels and norm updates come only from real transitions.

        normalize_static31=normalize_context40

        self.model.in_norm.update(self.model.inputs(s,fields['a'],normalize_static31(fields['xi'])))

        self.model.out_norm.update(self.model.targets(s,s1))

        self.buffer.add(fields);self.controls+=1;self.last_physics_tick=physics_end_tick



    def sample(self):

        b=self.buffer;k=self.window

        assert b.size>=k

        start=torch.randint(0,b.size-k+1,(self.batch,),device=self.device,generator=self.generator)

        env=torch.randint(0,b.N,(self.batch,),device=self.device,generator=self.generator)

        rows=b._row(start[:,None]+torch.arange(k,device=self.device))

        ids=env[:,None].expand_as(rows)

        out={key:b.data[key][rows,ids] for key in ('s','s1','a','xi','done')}

        done=out['done'].float()

        out['mask']=torch.cumprod(torch.cat((torch.ones(self.batch,1,device=self.device),1-done[:,:-1]),-1),-1)

        return out



    def update(self):

        normalize_static31=normalize_context40

        batch=self.sample();state=self.geometry.unflatten_state(batch['s'][:,0]);states=[]

        for i in range(self.window):

            state=self.model.step(state,batch['a'][:,i],normalize_static31(batch['xi'][:,i]));states.append(state)

        prediction=tuple(torch.stack([value[i] for value in states],1) for i in range(7))

        scale=torch.maximum(self.model.out_norm.std(),self.floor)

        error=(self.model.state_error(prediction,self.geometry.unflatten_state(batch['s1']))/scale).square().mean(-1)

        loss=(error*batch['mask']).sum()/self.batch

        assert torch.isfinite(loss)

        self.optimizer.zero_grad(set_to_none=True);loss.backward()

        norm=torch.nn.utils.clip_grad_norm_(self.model.parameters(),1.)

        assert torch.isfinite(norm)

        assert all(parameter.grad is None or torch.isfinite(parameter.grad).all() for parameter in self.model.parameters())

        self.optimizer.step();self.updates+=1

        assert all(torch.isfinite(parameter).all() for parameter in self.model.parameters())

        return dict(world_updates=self.updates,loss=float(loss.detach()),preclip_grad_L2=float(norm),

                    replay_controls=self.buffer.size,window=self.window,

                    source='caller-declared input; actual measured-producer provenance requires separate runtime admission',policy_updates=0)



    def checkpoint(self):

        return dict(world_model=self.model.state_dict(),world_optimizer=self.optimizer.state_dict(),

                    dedicated_sampling_rng=self.generator.get_state(),world_updates=self.updates,

                    physical_controls=self.controls,last_physics_tick=self.last_physics_tick,protocol=self.protocol,replay_saved=False,

                    replay_resume_scope='fresh replay; full WM weights/norms/optimizer/counters retained',

                    complete_native_policy_conversion=False)



def normalize_context40(x):
    from compact_episode_static31_v1 import normalize_static31
    if x.shape[-1]!=40:raise ValueError('static31 raw plus raw depth9 required')
    scale=x.new_tensor([4.,.4,2.,3.141592653589793,2.,4.,1.,.2,1.])
    return torch.cat((normalize_static31(x[...,:31]),x[...,31:]/scale),-1)
