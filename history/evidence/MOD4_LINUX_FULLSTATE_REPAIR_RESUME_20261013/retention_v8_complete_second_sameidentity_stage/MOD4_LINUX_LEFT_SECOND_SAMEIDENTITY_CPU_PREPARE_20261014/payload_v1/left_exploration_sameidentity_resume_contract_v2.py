"""Sameidentity-only restore. No candidate or initializer branch exists."""
from pathlib import Path
import copy,hashlib,json,time,os
import torch
KEY='LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'
EXPECTED_OWN_SOURCE_SHA='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
PROFILE='left_initial_joint_margin014_std1_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def same(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return type(a)is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    if hasattr(a,'shape'):
        import numpy as np
        return type(a)is type(b) and np.array_equal(a,b)
    return type(a)is type(b) and a==b
def actual_action_API(env):
    assert env.num_envs==20000
    rows=[]
    for name,term in env.action_manager._terms.items():
        if term.action_dim==4:
            offset=term._offset;q=env.scene['robot'].data.default_joint_pos[:,term._joint_ids]
            assert isinstance(offset,torch.Tensor) and offset.shape==(20000,4)
            assert torch.equal(offset,torch.zeros_like(offset)) and torch.equal(q,torch.zeros_like(q))
            scale=term._scale
            if isinstance(scale,torch.Tensor):assert bool((scale==.5).all())
            else:assert scale==.5
            rows.append(dict(term=name,count=20000,offset_shape=list(offset.shape),offset_all_exact_zero=True,default_joint_q_all_exact_zero=True,scale_exact_half=True,joint_names=term._joint_names))
    assert len(rows)==1
    return rows
def patch(module,root):
    old_resume=module.resume_e1_new_episode;old_install=module.install_e1_save_contract
    def resume(runner,env,path,log_dir):
        assert sha(path)==EXPECTED_OWN_SOURCE_SHA,'Onlyactualwhole20kown2bsource'
        ck=torch.load(path,map_location='cpu',weights_only=False)
        assert ck['sensor_DR_state']['n']==20000 and ck['independent_terrain_expert']=='E1_WAVE50'
        assert ck['E1_WAVE50_initial_source_sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
        assert KEY in ck and ck[KEY]['profile']==PROFILE and ck[KEY]['source_envs']==20000
        assert ck[KEY]['source_SHA']=='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
        assert not any(k.startswith('LINUX20K_LEFT_JOINT_CENTER_') or k.startswith('LINUX20K_LEFT_JOINT_LOWER_') for k in ck)
        original_proof=old_resume(runner,env,path,log_dir)
        assert same(runner.alg.actor.state_dict(),ck['actor_state_dict'])
        assert same(runner.alg.critic.state_dict(),ck['critic_state_dict'])
        assert same(runner.alg.optimizer.state_dict(),ck['optimizer_state_dict'])
        api=actual_action_API(env)
        beforeCPU=torch.get_rng_state().clone();beforeCUDA=[x.clone() for x in torch.cuda.get_rng_state_all()]
        mark=copy.deepcopy(ck[KEY]);runner._linux_left_exploration_mark=mark
        state=dict(actor=runner.alg.actor.state_dict(),optimizer=runner.alg.optimizer.state_dict(),mark=mark)
        q=Path(log_dir)/'LEFT_EXPLORATION_ACTUAL_CUDA_ROUNDTRIP.pt';torch.save(state,q)
        disk=torch.load(q,map_location='cpu',weights_only=False);assert same(state,disk)
        assert torch.equal(beforeCPU,torch.get_rng_state()) and all(torch.equal(a,b) for a,b in zip(beforeCUDA,torch.cuda.get_rng_state_all()))
        proof=dict(epoch=time.time(),pid=os.getpid(),passed=True,source_sha256=sha(path),source_envs=20000,profile=mark['profile'],explicit_one_time_left_mean_std_initialization=False,same_left_branch_restored_exact=True,all_original_twelve_fullstate_contracts_precede_left_axis=True,actual_all20k_action_offset_and_defaultq=api,actual_left_actor_optimizer_metadata_CUDA_disk_roundtrip_exact=True,no_CPU_CUDA_RNG_draw_for_initializer=True,no_env_DR_command_or_history_mutation_by_initializer=True,initial_other_five_heads_critic_exact=True,initializer_not_live_action_coupling=True,source_episode_plus_one_checked_by_original_contract=True,PhysX_exact_resume_claimed=False,qualified50=False,second_sameidentity_block=True,full_actor_critic_allstd_optimizer_restored_exact=True,no_initializer_branch_exists=True)
        Path(log_dir,'LEFT_EXPLORATION_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(proof,indent=2))
        return original_proof
    def install(runner,env):
        old_install(runner,env);old_save=runner.save
        def save(path,*a,**k):
            old_save(path,*a,**k);c=torch.load(path,map_location='cpu',weights_only=False)
            c[KEY]=copy.deepcopy(runner._linux_left_exploration_mark);torch.save(c,path)
        runner.save=save
    module.resume_e1_new_episode=resume;module.install_e1_save_contract=install
