"""Build a new isolated combined course, retaining all265 D6 source bytes."""
from pathlib import Path
import ast,json,hashlib,shutil,time
PREP=Path(__file__).resolve().parent;OLD=PREP.parent/'MOD4_D6_FULL_CONTRACT_20261009';D=PREP.parent/'MOD4_D7_FULL_CONTRACT_20261009';R=D/'reports'
assert not D.exists();R.mkdir(parents=True)
read=lambda p:json.loads(p.read_text(encoding='utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(f)==265
for n,h in f.items():
 assert sha(OLD/n)==h,n
 p=D/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OLD/n,p)
new=[]
def put(n,t):
 p=D/n;assert not p.exists();ast.parse(t);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf8');new.append(n)
for n in ('chassis_com_component.py','chassis_com_pose_roundtrip_sdk_adapter.py','chassis_pd_nominal_readback.py','explicit_pd_component.py','explicit_pd_sdk_adapter.py'):
 put('isaac/mod4/'+n,(PREP/n).read_text(encoding='utf8'))
put('isaac/mod4/chassis_pd_training_env.py','''"""Approved D7 chassis-only COM and explicit motor PD; all D0-D6 retained."""
import os
from gas_damping_training_env import GasDampingMod4Env
from chassis_com_component import PROFILE as COM_PROFILE
from explicit_pd_component import PROFILE as PD_PROFILE
from chassis_com_pose_roundtrip_sdk_adapter import ChassisCOMSDK
from explicit_pd_sdk_adapter import ExplicitPDSDK
class ChassisPDMod4Env(GasDampingMod4Env):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        com=os.environ.get('RM_CHASSIS_COM_PROFILE','off');pd=os.environ.get('RM_EXPLICIT_PD_PROFILE','off')
        if com not in ('off',COM_PROFILE) or pd not in ('off',PD_PROFILE):raise ValueError('Unapproved D7 scope')
        self._chassis_com=ChassisCOMSDK(self,com==COM_PROFILE,int(self.cfg.seed))
        self._explicit_pd=ExplicitPDSDK(self,pd==PD_PROFILE,int(self.cfg.seed))
    def chassis_pd_recipe(self):
        return dict(version=1,COM_profile=COM_PROFILE if self._chassis_com.component.enabled else 'off',PD_profile=PD_PROFILE if self._explicit_pd.component.enabled else 'off',
                    chassis_link_local_delta_m=[-.005,.005],chassis_only=True,PD_factor=[.95,1.05],leg_kp_nominal=60.,leg_kd_nominal=2.,wheel_kd_nominal=.6,wheel_kp0=True,
                    independent_COM_xyz_and_PD_groups=True,motor_implicit_drive_zero=True,complete_D0_D6_retained=True,engineering_pressure_not_hardware_calibration=True)
    def chassis_pd_audit(self):
        return dict(COM=self._chassis_com.audit(),PD=self._explicit_pd.audit(),parameter_auditor=self._mild_dr.audit())
''')
put('isaac/mod4/chassis_pd_checkpoint.py','''"""Complete D7 state on top of actual D6 saved contract; one fresh episode."""
from pathlib import Path
import os,json,time,torch
from chassis_com_component import PROFILE as COM_PROFILE
from explicit_pd_component import PROFILE as PD_PROFILE
from gas_damping_checkpoint import validate_saved_damping
from spring_pressure_checkpoint import exact
def validate_saved_chassis_pd(state,n):
    assert state['version']==1 and state['rng_device_type']=='cuda'
    com=state['COM'];pd=state['PD']
    for st,profile in ((com,COM_PROFILE),(pd,PD_PROFILE)):
        assert st['version']==1 and st['profile']==profile and st['num_envs']==n and st['enabled']
        assert st['episode'].shape==(n,) and st['episode'].dtype==torch.long and bool((st['episode']>=0).all())
    delta=com['delta_m'];assert delta.shape==(n,3) and torch.isfinite(delta).all() and bool((delta.abs()<=.005001).all())
    assert len(com['private_xyz_RNG'])==3
    assert set(pd['factor'])==set(pd['private_group_RNG'])=={'leg_kp','leg_kd','wheel_kd'}
    for k,width in (('leg_kp',4),('leg_kd',4),('wheel_kd',2)):
        v=pd['factor'][k];assert v.shape==(n,width) and torch.isfinite(v).all() and bool(((v>=.949999)&(v<=1.050001)).all())
    for rng in list(com['private_xyz_RNG'])+list(pd['private_group_RNG'].values()):assert rng.dtype==torch.uint8 and rng.ndim==1 and rng.numel()>0
    return True
def current_state(env):
    return dict(version=1,rng_device_type=env.device.split(':')[0] if isinstance(env.device,str) else env.device.type,COM=env._chassis_com.state_dict(),PD=env._explicit_pd.state_dict())
def install_chassis_pd_save_contract(runner,env):
    from gas_damping_checkpoint import install_damping_save_contract
    install_damping_save_contract(runner,env);original=runner.save
    def save(path,*args,**kw):
        original(path,*args,**kw);ck=torch.load(path,map_location='cpu',weights_only=False);state=current_state(env);validate_saved_chassis_pd(state,env.num_envs)
        ck['chassis_PD_state']=state;ck['chassis_PD_recipe']=env.chassis_pd_recipe();ck['chassis_PD_resume_contract']='Restore full D1-D6 and COM/PD private CUDA streams, then one fresh physics episode; not PhysX exactresume.';torch.save(ck,path)
    runner.save=save
def resume_chassis_pd_new_episode(runner,env,path,log_dir):
    from gas_damping_checkpoint import resume_damping_new_episode
    ck=torch.load(path,map_location='cpu',weights_only=False);has='chassis_PD_state' in ck
    if has:
        validate_saved_chassis_pd(ck['chassis_PD_state'],env.num_envs);assert ck['chassis_PD_recipe']==env.chassis_pd_recipe()
        env._chassis_com.load_state_dict(ck['chassis_PD_state']['COM']);env._explicit_pd.load_state_dict(ck['chassis_PD_state']['PD']);assert exact(current_state(env),ck['chassis_PD_state'])
    else:
        assert os.environ.get('RM_CHASSIS_PD_INITIAL_ADMISSION')=='D6_to_D7';validate_saved_damping(ck['gas_damping_state'],env.num_envs)
    saved=current_state(env);tmp=Path(log_dir)/'CHASSIS_PD_ACTUAL_CUDA_STARTUP_ROUNDTRIP.pt';torch.save(saved,tmp);loaded=torch.load(tmp,map_location='cpu',weights_only=False)
    env._chassis_com.load_state_dict(loaded['COM']);env._explicit_pd.load_state_dict(loaded['PD']);assert exact(current_state(env),saved)
    ce=env._chassis_com.component.episode.clone();pe=env._explicit_pd.component.episode.clone()
    row=resume_damping_new_episode(runner,env,path,log_dir)
    assert torch.equal(env._chassis_com.component.episode,ce+1) and torch.equal(env._explicit_pd.component.episode,pe+1)
    audit=env.chassis_pd_audit()
    proof=dict(epoch=time.time(),pid=os.getpid(),source_sha256=row['source_sha256'],predecessor_had_chassis_PD_state=has,COM_PD_factors_episodes_six_CUDA_RNG_restored_exact=has,
               explicitly_new_D7_groups=not has,actual_CUDA_chassis_PD_disk_roundtrip_exact=True,COM_PD_episode_incremented_once=True,complete_D1_D6_optimizer_global_named_streams_verified=True,
               actual_chassis_PD_audit=audit,new_physical_episode=True,PhysX_exact_resume_claimed=False)
    Path(log_dir,'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json').write_text(json.dumps(proof,indent=2));return proof
''')
snapshot_names=['chassis_com_component.py','chassis_com_pose_roundtrip_sdk_adapter.py','chassis_pd_nominal_readback.py','explicit_pd_component.py','explicit_pd_sdk_adapter.py','chassis_pd_training_env.py','chassis_pd_checkpoint.py']
for fresh in (False,True):
 old='train_gas_fresh_preflight_ppo.py' if fresh else 'train_gas_resume_ppo.py';name='train_chassis_pd_fresh_preflight_ppo.py' if fresh else 'train_chassis_pd_resume_ppo.py'
 t=(OLD/'isaac/mod4'/old).read_text(encoding='utf8')
 t=t.replace('from gas_damping_training_env import GasDampingMod4Env as Mod4Env','from chassis_pd_training_env import ChassisPDMod4Env as Mod4Env')
 t=t.replace('from gas_damping_checkpoint import install_damping_save_contract','from chassis_pd_checkpoint import install_chassis_pd_save_contract').replace('install_damping_save_contract(runner,env)','install_chassis_pd_save_contract(runner,env)')
 if not fresh:t=t.replace('from gas_damping_checkpoint import resume_damping_new_episode','from chassis_pd_checkpoint import resume_chassis_pd_new_episode').replace('resume_damping_new_episode(runner,env,args.init_checkpoint,log_dir)','resume_chassis_pd_new_episode(runner,env,args.init_checkpoint,log_dir)')
 anchor='    manifest["src_sha256"] = snapshot';assert t.count(anchor)==1
 t=t.replace(anchor,'    manifest["chassis_PD_recipe"]=env.chassis_pd_recipe()\n    for name in '+repr(tuple(snapshot_names+[name]))+':\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n'+anchor)
 put('isaac/mod4/'+name,t)
t=(OLD/'native_d6_gas_probe.py').read_text(encoding='utf8').replace('from gas_damping_training_env import GasDampingMod4Env as Mod4Env','from chassis_pd_training_env import ChassisPDMod4Env as Mod4Env')
t=t.replace("RM_GAS_DAMPING_PROFILE='gas_damping_independent_episode_090_110_v1'","RM_GAS_DAMPING_PROFILE='gas_damping_independent_episode_090_110_v1',RM_CHASSIS_COM_PROFILE='chassis_link_local_independent_xyz_5mm_v1',RM_EXPLICIT_PD_PROFILE='explicit_motor_PD_independent_095_105_v1'")
anchor=" gas_damping_audit=env._gas_damping.audit()" # actual result uses keyword below
assert "gas_damping_audit=env._gas_damping.audit()" in t
t=t.replace('gas_damping_audit=env._gas_damping.audit()','chassis_PD_audit=env.chassis_pd_audit(),gas_damping_audit=env._gas_damping.audit()')
put('native_d7_chassis_pd_probe.py',t)
t=(OLD/'supervise_d6_gas_full_contract.py').read_text(encoding='utf8').replace('D6','D7').replace('d6','d7')
t=t.replace("MOD4_D5_FULL_CONTRACT_20261008","MOD4_D6_FULL_CONTRACT_20261009").replace('SELECTED_D5_BEHAVIOR_SOURCE','SELECTED_D6_BEHAVIOR_SOURCE').replace('D5_STATE.json','D6_STATE.json').replace('D5_ATTENTION.json','D6_ATTENTION.json').replace('D5_GUARDIAN_STARTED.json','D6_GUARDIAN_STARTED.json').replace('D5_REVIEW_READY.json','D6_REVIEW_READY.json').replace('E0_D5_saved_review_ready','E0_D6_saved_review_ready').replace('waiting_existing_D5','waiting_existing_D6')
t=t.replace('D7_GAS_DAMPING_ACTUAL_SDK_REVIEW.json','D7_COM_PD_ACTUAL_SDK_REVIEW.json').replace("['SDK_limited_damping_parameter_lifecycle_scope_accepted']","['COM_PD_separate_actual_SDK_scope_accepted']")
t=t.replace('train_gas_resume_ppo.py','train_chassis_pd_resume_ppo.py').replace('train_gas_fresh_preflight_ppo.py','train_chassis_pd_fresh_preflight_ppo.py').replace('native_d7_gas_probe.py','native_d7_chassis_pd_probe.py')
t=t.replace("    return e\n","    e['RM_CHASSIS_COM_PROFILE']='chassis_link_local_independent_xyz_5mm_v1'\n    e['RM_EXPLICIT_PD_PROFILE']='explicit_motor_PD_independent_095_105_v1'\n    e['RM_CHASSIS_PD_INITIAL_ADMISSION']='D6_to_D7'\n    return e\n",1)
t=t.replace('from gas_damping_checkpoint import validate_saved_damping','from gas_damping_checkpoint import validate_saved_damping\nfrom chassis_pd_checkpoint import validate_saved_chassis_pd')
t=t.replace('require_gas=True):','require_gas=True,require_d7=True):')
anchor='    return info\n';assert t.count(anchor)==1
t=t.replace(anchor,"    if require_d7:\n        validate_saved_chassis_pd(ck['chassis_PD_state'],count);assert ck['chassis_PD_recipe']['COM_profile']=='chassis_link_local_independent_xyz_5mm_v1' and ck['chassis_PD_recipe']['PD_profile']=='explicit_motor_PD_independent_095_105_v1'\n    else:assert 'chassis_PD_state' not in ck\n"+anchor)
t=t.replace('require_gas=False','require_d7=False')
anchor="    assert r['gas_damping_audit']['actual_PhysX_buffer_implicit_model_exact']";assert anchor in t
t=t.replace(anchor,"    assert r['chassis_PD_audit']['COM']['actual_PhysX_local_pose_and_buffer_exact'] and r['chassis_PD_audit']['PD']['motor_implicit_drive_stiffness_and_damping_zero']\n"+anchor)
anchor="        gas=read(run/'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json');";assert anchor in t
t=t.replace(anchor,"        cp=read(run/'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json');assert cp['source_sha256']==s.q.base.sha(init) and cp['actual_CUDA_chassis_PD_disk_roundtrip_exact'] and cp['COM_PD_episode_incremented_once'] and cp['complete_D1_D6_optimizer_global_named_streams_verified'] and not cp['PhysX_exact_resume_claimed']\n"+anchor)
t=t.replace("bounded_E0_D7_gas_damping_learning","bounded_E0_D7_chassis_COM_explicit_PD_learning").replace('85-d7-gas-anchor','98-d7-com-pd-anchor').replace('86-d7-gas-b','99-d7-com-pd-b')
t=t.replace("role='Actual D7 gas damping engineering pressure closedloop with complete D0-D5 retained; friction not included'","role='Actual D7 chassis COM+explicit PD engineering pressure closedloop with complete D0-D6 retained'")
t=t.replace("gas_damping_profile='gas_damping_independent_episode_090_110_v1',physics_dt_s", "gas_damping_profile='gas_damping_independent_episode_090_110_v1',chassis_COM_profile='chassis_link_local_independent_xyz_5mm_v1',explicit_PD_profile='explicit_motor_PD_independent_095_105_v1',physics_dt_s")
t=t.replace("next='Actual gas-damping retention/event review, then approved D7 COM-PD; D7 friction remains pending measured bounds'","next='Actual COM-PD retention/event review, then approved available D9 grouping or experts; D6 friction and D8 measured load bounds remain pending'")
put('supervise_d7_chassis_pd_full_contract.py',t)
cpu='''"""Reject corrupt or incomplete new state before launch; no CUDA initialization."""
import copy,json,torch
from chassis_com_component import ChassisCOM
from explicit_pd_component import ExplicitPD
from chassis_pd_checkpoint import validate_saved_chassis_pd
def main():
    com=ChassisCOM(4,'cpu',7,True);pd=ExplicitPD(4,'cpu',8,True);ids=torch.arange(4);com.reset(ids);pd.reset(ids)
    state=dict(version=1,rng_device_type='cuda',COM=com.state_dict(),PD=pd.state_dict());assert validate_saved_chassis_pd(state,4)
    changes=[lambda x:x.update(version=2),lambda x:x.update(rng_device_type='cpu'),lambda x:x['COM'].update(enabled=False),lambda x:x['COM'].update(num_envs=5),
             lambda x:x['COM'].update(delta_m=torch.ones(4,3)),lambda x:x['COM'].update(delta_m=torch.full((4,3),float('nan'))),lambda x:x['COM'].update(episode=torch.zeros(4)),
             lambda x:x['COM'].update(private_xyz_RNG=[]),lambda x:x['PD'].update(profile='wrong'),lambda x:x['PD']['factor'].update(leg_kp=torch.ones(4,3)),
             lambda x:x['PD']['factor'].update(wheel_kd=torch.zeros(4,2)),lambda x:x['PD']['private_group_RNG'].update(leg_kd=torch.zeros(0,dtype=torch.uint8))]
    for mutation in changes:
        v=copy.deepcopy(state);mutation(v)
        try:validate_saved_chassis_pd(v,4)
        except (AssertionError,ValueError):pass
        else:raise AssertionError('Corrupt full state accepted')
    assert not torch.cuda.is_initialized();return dict(passed=True,count=13,new_group_schema_and_corruption_rejections=True,CPU_fixture_not_actual_CUDA_rng_restore=True,CUDA_initialized=False,Torch=torch.__version__)
if __name__=='__main__':print(json.dumps(main()))
'''
put('test_chassis_pd_checkpoint_cpu.py',cpu)
(R/'NEW_SOURCE_NAMES.json').write_text(json.dumps(new,indent=2))
actual=read(OLD/'reports/D6_CURRENT_ACTUAL.json');selected=actual['completed']['d6_stable_block1_PASSED']
selected.update(behavior_scope_accepted=True,actual_matched_evidence='D6_ACTUAL_BASELINE_SCOPE_REVIEW.json',source_selection_basis='Actual independently reviewed D6 first-block full three-skill pairing; not directory maximum/preflight')
(R/'SELECTED_D6_BEHAVIOR_SOURCE.json').write_text(json.dumps(selected,indent=2))
for name in ('D6_ACTUAL_BASELINE_SCOPE_REVIEW.json',):shutil.copy2(OLD/'reports'/name,R/name)
(R/'LOCAL_D7_BUILD.json').write_text(json.dumps(dict(epoch=time.time(),all265_predecessor_exact=True,new_sources=new,learning_or_canonical_transactions=0),indent=2))
print(json.dumps(dict(root=str(D),predecessor_sources=len(f),added=len(new),source=selected['checkpoint']['sha256'],no_GPU=True)))
