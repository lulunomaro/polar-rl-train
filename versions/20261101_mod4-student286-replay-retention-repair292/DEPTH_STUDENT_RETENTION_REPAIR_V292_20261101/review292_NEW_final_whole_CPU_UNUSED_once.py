"""One newly qualified292 final full-tree CPU purpose; no old once/model replay."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import argparse,hashlib,io,json,math,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
sys.path.insert(0,str(N))
from teacher_task292 import validate_task,validate_final
def put(n,v):
    with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--caller-index-SHA',required=True);a=p.parse_args()
    index=N/'INDEX292_NEW_FINAL_CPU_READER_FROZEN.json';assert H(index)==a.caller_index_SHA
    for row in json.loads(index.read_bytes())['files']:
        f=Path(row['path']);assert f.stat().st_size==row['bytes'] and H(f)==row['SHA']
    j=json.loads((R/'ROOT292_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())
    assert j['passed_collection'] and j['owner_closed']['canonical_None'] and j['owner_closed']['shared_locks_free']
    assert set(j['formals'])=={'jump_72'}
    role=j['roles']['jump_72'];f=j['formals']['jump_72'];path=Path(f['path'])
    assert role['qualified_formal'] and role['private_EX_free'] and role['actual_material_limit_error_count']==0
    assert f['transfers']==1 and f['two_host_SHA_equal']
    assert path.resolve().is_relative_to((N/'current_closed292_models/jump_72/formal').resolve())
    task=json.loads((N/'TASK292_FROZEN.json').read_bytes());validate_task(task)
    go=role['final']['original_finite_owner_GO'];validate_final(role['final'],task,go)
    put('ROOT292_NEW_FINAL_CPU_PURPOSE_CONSUMED_BEFORE_READ.json',dict(epoch=time.time(),maximum_NEW292_formal_byte_hash_decode=1,
      all_old_models_raw_reads=0,SDK_GPU_CUDA=False,purpose='all three optimizers/teacher/STD/DR/full-save final validation'))
    import torch
    assert not torch.cuda.is_initialized()
    raw=path.read_bytes();assert len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['SHA']
    ck=torch.load(io.BytesIO(raw),map_location='cpu',weights_only=False);del raw
    finite_count=0
    def finite(v):
        nonlocal finite_count
        if torch.is_tensor(v):
            finite_count+=1
            if v.is_floating_point()or v.is_complex():assert torch.isfinite(v).all()
        elif isinstance(v,(float,complex)):assert math.isfinite(v.real) and math.isfinite(v.imag)
        elif isinstance(v,dict):
            for x in v.values():finite(x)
        elif isinstance(v,(list,tuple)):
            for x in v:finite(x)
    finite(ck)
    assert ck['kind']=='LQR_MPC_DEPTH_TEACHER_STUDENT292_COMPLETE'
    assert ck['source_carrier_SHA']=='4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d'
    validate_task(ck['typed_TEACHER292_task']);assert ck['original_finite_owner_GO']==go
    pi=ck['actual_new_Pi_updates'];critic=ck['actual_new_critic_updates'];wm=ck['total_WM_updates']
    assert pi==critic>0 and wm==7087+ck['actual_new_WM_updates']
    assert ck['actual_new_PPO_updates']==ck['actual_new_STD_updates']==0
    teacher=ck['teacher_full_PPO_state'];assert teacher['iter']==2135 and ck['teacher_saved_iteration']==2135
    steps=[int(v['step'])for v in teacher['optimizer_state_dict']['state'].values()]
    assert len(steps)==17 and min(steps)==max(steps)==42940
    assert teacher['optimizer_state_dict']['param_groups'][0]['lr']==.0019461950683593758
    student=ck['student'];assert student['Pi_updates']==pi and student['critic_updates']==critic
    assert student['actor_state_dict']['mlp.0.weight'].shape==(128,44)
    assert student['critic_state_dict']['mlp.0.weight'].shape==(128,47)
    assert torch.equal(student['actor_state_dict']['distribution.std_param'],teacher['actor_state_dict']['distribution.std_param'])
    identities=student['identity']['targets'];counts={}
    for scope,count,updates in (('actor',9,pi),('critic',8,critic)):
        optimizer=student[scope+'_optimizer'];assert len(optimizer['state'])==count
        bindings=identities[scope]['parameter_bindings'];byid={r['optimizer_id']:r for r in bindings}
        assert set(byid)==set(optimizer['state']) and len(bindings)==count
        for pid,slot in optimizer['state'].items():
            key=byid[pid]['state_key'];expected=42940 if key=='distribution.std_param' else 42940+updates
            assert int(slot['step'])==expected
            weight=student[scope+'_state_dict'][key]
            assert slot['exp_avg'].shape==slot['exp_avg_sq'].shape==weight.shape
        assert all(g['lr']==(1e-5 if scope=='actor' else 1e-4) for g in optimizer['param_groups']);counts[scope]=count
    world=ck['world_model'];assert world['world_updates']==wm
    assert all(int(v['step'])==wm for v in world['world_optimizer']['state'].values())
    assert world['world_model']['net.0.weight'].shape==(512,273) and world['world_model']['net.9.weight'].shape==(223,512)
    # The nested reused273 kernel's descriptive flags remain WM-module scope;
    # parent292 contains the actual student and three-optimizer runtime evidence.
    assert ck['complete_three_optimizer_conversion'] and ck['actual_Pi_runtime_qualified']
    assert ck['full_physics_resume_claimed'] is False and ck['replay_saved'] is False
    assert set(ck['target_DR_state']['components'])=={'sensor','feedback','physics_action_queue','spring','damping','COM','PD'}
    assert ck['current_measured_state224'].shape==(80,224) and ck['current_static31'].shape==(80,31)
    assert ck['teacher_target_layout'].shape==(80,4) and ck['previous_clipped_action'].shape==(80,6)
    assert ck['mixed_ground_JUMP_state']['flat_mask'].sum()==8
    memory=ck['original_jump_reward_memory'];assert memory['last_actions'].shape==(80,6,2)
    assert memory['last_contacts'].shape==(80,2) and memory['base_air_time'].shape==(80,)
    assert ck['controls']*80==ck['own_transitions'] and ck['controls']*8==ck['physics_callbacks'] and ck['controls']*2==ck['feedback_samples']
    assert role['formal']['save_epoch']>=go['save_deadline']
    row=dict(passed=True,epoch=time.time(),path=str(path),bytes=f['bytes'],SHA=f['SHA'],finite_tensors=finite_count,
      actual_new_Pi_updates=pi,actual_new_critic_updates=critic,total_WM_updates=wm,new_WM_updates=wm-7087,
      student_optimizer_partition=counts,teacher_Adam17=42940,source_teacher_and_STD_preserved=True,
      three_optimizer_full_tree=True,controls=ck['controls'],own_transitions=ck['own_transitions'],
      NEWformal_reads=1,old_model_raw_reads=0,CUDA_initialized=torch.cuda.is_initialized(),
      student270mm_skill_not_inferred=True)
    put('ROOT292_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json',row);print(json.dumps(row))
if __name__=='__main__':
    try:main()
    except BaseException:put('ROOT292_NEW_FINAL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_replay=True));raise
