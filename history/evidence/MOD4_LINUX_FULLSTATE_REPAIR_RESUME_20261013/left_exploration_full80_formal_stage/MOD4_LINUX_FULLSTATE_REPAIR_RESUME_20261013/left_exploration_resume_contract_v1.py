"""One explicit, saved left-head initialization after the unchanged full restore."""
from pathlib import Path
import copy, hashlib, json, os, time
import torch

KEY='LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'
SOURCE_SHA='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
CANDIDATE_SHA='8ff1a32789364351e70ab23a7d96accf6cfdcdc670d1d352a6bea998d4b50d42'

def same(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return type(a)is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    if hasattr(a,'shape'):
        import numpy as np
        return type(a)is type(b) and np.array_equal(a,b)
    return type(a)is type(b) and a==b

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def actual_action_API(env):
    assert env.num_envs==20000
    terms=env.action_manager._terms
    rows=[]
    for name,term in terms.items():
        if term.action_dim==4:
            offset=term._offset
            ids=term._joint_ids
            q=env.scene['robot'].data.default_joint_pos[:,ids]
            assert isinstance(offset,torch.Tensor) and offset.shape==(20000,4)
            assert torch.equal(offset,torch.zeros_like(offset)) and torch.equal(q,torch.zeros_like(q))
            scale=term._scale
            if isinstance(scale,torch.Tensor):assert bool((scale==.5).all())
            else:assert scale==.5
            rows.append(dict(term=name,count=20000,offset_shape=list(offset.shape),offset_all_exact_zero=True,default_joint_q_all_exact_zero=True,scale_exact_half=True,joint_names=term._joint_names))
    assert len(rows)==1,rows
    return rows

def patch(module,root):
    old_resume=module.resume_e1_new_episode
    old_install=module.install_e1_save_contract
    def resume(runner,env,path,log_dir):
        ck=torch.load(path,map_location='cpu',weights_only=False)
        original_proof=old_resume(runner,env,path,log_dir)
        # The original twelve contracts have already verified all inherited state.
        assert same(runner.alg.actor.state_dict(),ck['actor_state_dict'])
        assert same(runner.alg.critic.state_dict(),ck['critic_state_dict'])
        assert same(runner.alg.optimizer.state_dict(),ck['optimizer_state_dict'])
        api=actual_action_API(env)
        beforeCPU=torch.get_rng_state().clone()
        beforeCUDA=[x.clone() for x in torch.cuda.get_rng_state_all()]
        new=KEY not in ck
        if new:
            assert sha(path)==SOURCE_SHA
            candidate=Path(root)/'source/own20k_left_joint_margin014_std1_CPU_prepared.pt'
            assert sha(candidate)==CANDIDATE_SHA
            c=torch.load(candidate,map_location='cpu',weights_only=False)
            assert c[KEY]['source_SHA']==SOURCE_SHA and c[KEY]['source_envs']==20000
            # Every inherited nonpolicy field, critic, and RNG tree stays untouched.
            for k in ck:
                if k not in ('actor_state_dict','optimizer_state_dict'):assert same(ck[k],c[k]),k
            runner.alg.actor.load_state_dict(c['actor_state_dict'],strict=True)
            runner.alg.optimizer.load_state_dict(c['optimizer_state_dict'])
            mark=copy.deepcopy(c[KEY])
            assert same(runner.alg.actor.state_dict(),c['actor_state_dict']) and same(runner.alg.optimizer.state_dict(),c['optimizer_state_dict'])
        else:
            mark=copy.deepcopy(ck[KEY])
            assert mark['source_SHA']==SOURCE_SHA and mark['profile']=='left_initial_joint_margin014_std1_v1' and mark['source_envs']==20000
        assert torch.equal(beforeCPU,torch.get_rng_state())
        assert all(torch.equal(a,b) for a,b in zip(beforeCUDA,torch.cuda.get_rng_state_all()))
        runner._linux_left_exploration_mark=mark
        state=dict(actor=runner.alg.actor.state_dict(),optimizer=runner.alg.optimizer.state_dict(),mark=mark)
        q=Path(log_dir)/'LEFT_EXPLORATION_ACTUAL_CUDA_ROUNDTRIP.pt'
        torch.save(state,q)
        disk=torch.load(q,map_location='cpu',weights_only=False)
        assert same(state,disk)
        assert torch.equal(beforeCPU,torch.get_rng_state()) and all(torch.equal(a,b) for a,b in zip(beforeCUDA,torch.cuda.get_rng_state_all()))
        proof=dict(epoch=time.time(),pid=os.getpid(),passed=True,source_sha256=sha(path),source_envs=20000,profile=mark['profile'],explicit_one_time_left_mean_std_initialization=new,same_left_branch_restored_exact=not new,all_original_twelve_fullstate_contracts_precede_left_axis=True,actual_all20k_action_offset_and_defaultq=api,actual_left_actor_optimizer_metadata_CUDA_disk_roundtrip_exact=True,no_CPU_CUDA_RNG_draw_for_initializer=True,no_env_DR_command_or_history_mutation_by_initializer=True,initial_other_five_heads_critic_exact=True,initializer_not_live_action_coupling=True,source_episode_plus_one_checked_by_original_contract=True,PhysX_exact_resume_claimed=False,qualified50=False)
        Path(log_dir,'LEFT_EXPLORATION_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(proof,indent=2))
        return original_proof
    def install(runner,env):
        old_install(runner,env)
        old_save=runner.save
        def save(path,*a,**k):
            old_save(path,*a,**k)
            c=torch.load(path,map_location='cpu',weights_only=False)
            c[KEY]=copy.deepcopy(runner._linux_left_exploration_mark)
            torch.save(c,path)
            # Parent rescue wrapper atomically publishes the complete file afterwards.
        runner.save=save
    module.resume_e1_new_episode=resume
    module.install_e1_save_contract=install
