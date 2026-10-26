"""Reject corrupt or incomplete new state before launch; no CUDA initialization."""
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
