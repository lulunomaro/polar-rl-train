"""Declare a new S4 learner only after the old complete W35 restore succeeds.

The old terrain/DR/named/global/private restoration and reset chain is reused.
The old expert optimizer is provenance; the gate/critic optimizer is new.
"""
from pathlib import Path
import copy, hashlib, json, os, time
import torch
from s4_rsl5_frozen_pair_learner_v1 import S4RecordedChoicePPO, SOURCE_SHA, view35

SCHEMA = {
 'SENSOR_RESUME_STARTUP_VERIFIED.json': ('actor_critic_std_exact','optimizer_loaded_original_path','sensor_streams_restored','global_CPU_CUDA_streams_restored','all_episode_counters_incremented_once'),
 'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json': ('COM_PD_factors_episodes_six_CUDA_RNG_restored_exact','actual_CUDA_chassis_PD_disk_roundtrip_exact','COM_PD_episode_incremented_once'),
 'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json': ('terrain_state_restored_exact','actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact','E1_episode_incremented_once'),
 'E1_COMMAND_RETENTION_STARTUP_VERIFIED.json': ('predecessor_command_state_restored_exact','actual_CUDA_command_state_and_private_rng_disk_roundtrip_exact','saved_source_episode_plus_one_verified'),
 'DELAY_RESUME_STARTUP_VERIFIED.json': ('predecessor_had_delay_state','delay_state_and_RNG_exactly_restored_before_reset','full_sensor_optimizer_global_named_streams_verified','delay_episode_incremented_once'),
 'ACTION_DELAY_RESUME_STARTUP_VERIFIED.json': ('predecessor_had_action_queue','action_queue_targets_timestamps_both_RNG_restored_exact','action_episode_incremented_once','restored_before_new_scene_clock_rebase'),
 'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json': ('predecessor_had_spring_pressure_state','spring_factor_episode_two_CUDA_RNG_restored_exact','actual_CUDA_spring_state_disk_roundtrip_exact','spring_episode_incremented_once'),
 'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json': ('predecessor_had_gas_damping_state','gas_factor_episode_two_CUDA_RNG_restored_exact','actual_CUDA_gas_state_disk_roundtrip_exact','gas_episode_incremented_once'),
}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def same(a,b):
    if torch.is_tensor(a): return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
    if isinstance(a,dict): return isinstance(b,dict) and a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)):return type(a)is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return type(a)is type(b) and a==b

def gate_config(runner,refs):
    cfg=copy.deepcopy(runner.cfg)
    cfg['algorithm']['class_name']='s4_rsl5_frozen_pair_learner_v1:S4RecordedChoicePPO'
    cfg['actor']=dict(class_name='s4_rsl5_frozen_pair_learner_v1:S4FrozenPairActor',expert_refs=refs,routing_seed=20261015,
        hidden_dims=[64,32],activation='elu',obs_normalization=False)
    cfg['critic']=dict(class_name='s4_rsl5_frozen_pair_learner_v1:S4NewSourceCritic',expert_refs=refs,
        hidden_dims=[256,128,64],activation='elu',obs_normalization=False)
    cfg['obs_groups']=dict(actor=['policy'],critic=['critic'])
    assert cfg['num_steps_per_env']==24 and cfg['algorithm']['learning_rate']==1e-4
    assert cfg['algorithm']['schedule']=='adaptive' and cfg['algorithm']['num_learning_epochs']==5 and cfg['algorithm']['num_mini_batches']==4
    return cfg

def verify_original_restore(log_dir,path):
    source=sha(path); rows={}
    # Typed original schema: these receipts intentionally have no generic passed flag.
    for name,keys in SCHEMA.items():
        p=Path(log_dir)/name;v=json.loads(p.read_bytes())
        assert v['pid']==os.getpid() and v['source_sha256']==source
        for k in keys: assert v[k] is True,(name,k)
        assert v['PhysX_exact_resume_claimed'] is False
        rows[name]=dict(path=str(p),sha256=sha(p))
    return rows

class SharedControlState:
    def __init__(self, obs):
        x=view35(obs);self.cache=obs.clone();self.previous=x[:,22:28].detach().clone()
        self.z=torch.full((len(x),),-1,dtype=torch.long,device=x.device)
        self.completed_controls=0;self.pending=False

    def begin(self,obs,z):
        assert not self.pending and torch.equal(obs['policy'],self.cache['policy'])
        assert torch.equal(view35(obs)[:,22:28],self.previous)
        assert z.shape==self.z.shape and z.dtype==torch.long and ((z>=0)&(z<2)).all()
        self.z=z.clone();self.pending=True

    def finish(self,actual_action_before_reset,clipped_requested,dones,next_obs):
        assert self.pending and torch.equal(actual_action_before_reset,clipped_requested)
        self.previous=actual_action_before_reset.detach().clone();self.previous[dones.bool()]=0
        assert torch.equal(view35(next_obs)[:,22:28],self.previous)
        self.z[dones.bool()]=-1;self.cache=next_obs.clone()
        self.completed_controls+=1;self.pending=False

    def save(self):
        assert not self.pending
        return dict(version=1,previous=self.previous.clone(),last_selected=self.z.clone(),cache=self.cache.clone(),
                    completed_controls=self.completed_controls,complete_control_boundary=True)

    def restore(self,state):
        assert not self.pending and state['version']==1 and state['complete_control_boundary'] is True
        assert state['previous'].shape==self.previous.shape and state['last_selected'].shape==self.z.shape
        assert isinstance(state['completed_controls'],int) and state['completed_controls']>=0
        device=self.previous.device
        self.previous=state['previous'].to(device).clone();self.z=state['last_selected'].to(device).clone()
        from tensordict import TensorDict
        raw=state['cache']
        assert set(raw.keys())>={'policy','critic'} and set(raw.keys())<={'policy','critic','s4_training_supported_domain'}
        assert all(torch.is_tensor(v) and v.shape[0]==len(self.previous) for v in raw.values())
        # A freshly built container with each actual tensor moved explicitly;
        # never trust serialized container metadata or a cached .to() result.
        self.cache=TensorDict({k:v.detach().to(device=device).clone() for k,v in raw.items()},batch_size=[len(self.previous)],device=device)
        assert all(v.device==device for v in self.cache.values())
        self.completed_controls=state['completed_controls']
        assert torch.equal(view35(self.cache)[:,22:28],self.previous)

def migrate_first(runner,env,path,log_dir,refs):
    assert sha(path)==SOURCE_SHA[1]
    ck=torch.load(path,map_location='cpu',weights_only=False)
    assert same(runner.alg.actor.state_dict(),ck['actor_state_dict'])
    assert same(runner.alg.critic.state_dict(),ck['critic_state_dict'])
    assert same(runner.alg.optimizer.state_dict(),ck['optimizer_state_dict'])
    assert torch.equal(env._e1_episode.cpu(),ck['E1_terrain_state']['episode']+1)
    receipts=verify_original_restore(log_dir,path)
    obs=runner.env.get_observations();cfg=gate_config(runner,refs)
    cpu=torch.get_rng_state().clone();cuda=[g.clone() for g in torch.cuda.get_rng_state_all()]
    runner.alg=S4RecordedChoicePPO.construct_algorithm(obs,runner.env,cfg,runner.device)
    runner.cfg=cfg;runner.current_learning_iteration=0
    assert torch.equal(cpu,torch.get_rng_state()) and all(torch.equal(a,b) for a,b in zip(cuda,torch.cuda.get_rng_state_all()))
    assert not runner.alg.optimizer.state and runner.alg.actor.verify_frozen()
    runtime=SharedControlState(obs)
    proof=dict(epoch=time.time(),pid=os.getpid(),source_SHA=sha(path),passed=True,
        original_eight_DR_environment_sourceepisode_plus_one_before_new_S4=True,old_receipts=receipts,
        new_gate35_new_E0_initialized_critic38_new_empty_optimizer=True,old_expert_optimizer_resumed=False,
        new_private_routing_seed=20261015,global_CPU_CUDA_RNG_unchanged_by_new_models=True,
        original_fivefamily_W35_integration_scope_only=True,new_supported_learning_exposure_not_admitted=True,
        no_geometry_command_reward_clock_hardware_change_by_migration=True,
        no_PPO_updates=True,PhysX_exact_resume_claimed=False)
    (Path(log_dir)/'S4_FIRST_DECLARED_MIGRATION_ACTUAL.json').write_text(json.dumps(proof,indent=2))
    return runtime,proof

def install_owned_save(runner,runtime,original_source,oldproof):
    # Install this AFTER the unmodified retention/D0-D7 save hooks.
    oldsave=runner.save
    def save(path,*a,**kw):
        oldsave(path,*a,**kw)
        ck=torch.load(path,map_location='cpu',weights_only=False)
        assert ck['S4_owned_learning']['explicitly_new_gate_critic_optimizer'] is True
        ck['S4_shared_control_state']=runtime.save()
        ck['S4_original_W35_source_SHA']=sha(original_source)
        ck['S4_first_fullrestore_migration_proof']=copy.deepcopy(oldproof)
        ck['S4_GPU_learning_admitted']=False
        ck['S4_native_integration_checkpoint_not_production_learning_source']=True
        torch.save(ck,path)
    runner.save=save
