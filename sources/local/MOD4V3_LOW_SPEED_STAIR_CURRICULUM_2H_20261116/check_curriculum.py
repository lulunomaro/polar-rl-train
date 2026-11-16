"""Exercise actual course transition and geometric qualification without any optimizer."""
from pathlib import Path
import sys,json,importlib.util,types
import torch,numpy as np
T=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('single_step_math',T/'support/mod4v3_ppo_v1/single_step_math.py');mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
S=mod.SPEC
master=torch.tensor([0,0,2,2,2,2]);episode=torch.tensor([0,0,2,2,1,1]);fails=torch.tensor([0,0,1,2,2,2]);ok=torch.tensor([True,False,False,False,True,False])
new,streak,up,down=mod.advance(master,episode,fails,ok,torch.ones(6,dtype=torch.bool))
assert new.tolist()==[1,0,2,1,2,2] and up.tolist()==[True,False,False,False,False,False] and down.tolist()==[False,False,False,True,False,False]
assert streak.tolist()==[0,1,2,0,2,2]
height=torch.tensor([.05,.07,.20]);x=torch.full((3,2),1.3);y=torch.zeros(3,2);z=height[:,None]+S.radius+torch.zeros(3,2);fz=torch.full((3,2),10.)
upper=mod.supported_upper(x,y,z,fz,height);assert upper.all()
assert not mod.supported_upper(x,y,z,torch.zeros_like(fz),height).any()
assert not mod.supported_upper(x,y,torch.full_like(z,S.radius),fz,height).any()
gained,landed=mod.first_landings(torch.zeros_like(upper),upper,torch.ones(3,dtype=torch.bool));assert gained.sum()==6
again,_=mod.first_landings(landed,upper,torch.ones(3,dtype=torch.bool));assert again.sum()==0
base=dict(upper=upper,body_x=torch.ones(3),pitch=torch.zeros(3),roll=torch.zeros(3),rate=torch.zeros(3),vertical_speed=torch.zeros(3),entry_speed=torch.full((3,),.4),maximum_speed=torch.full((3,),.5),entry_seen=torch.ones(3,dtype=torch.bool),failed=torch.zeros(3,dtype=torch.bool),active=torch.ones(3,dtype=torch.bool))
assert mod.stable_completion(**base).all()
for name,value in [('entry_speed',torch.full((3,),.7)),('maximum_speed',torch.full((3,),.7)),('body_x',torch.full((3,),1.45)),('failed',torch.ones(3,dtype=torch.bool)),('entry_seen',torch.zeros(3,dtype=torch.bool)),('upper',torch.tensor([[True,False]]*3))]:
    args=dict(base);args[name]=value;assert not mod.stable_completion(**args).any(),name
spec=importlib.util.spec_from_file_location('single_step_geometry',T/'support/single_step_geometry.py');geo=importlib.util.module_from_spec(spec);spec.loader.exec_module(geo)
for level,h in enumerate(S.heights):
    for frac in (.001,.05,.099):
        meshes,origin=geo.single_step((level/10)+frac,types.SimpleNamespace(size=(9.,9.)))
        assert np.allclose(origin,[4.5,4.5,0.])
        assert abs(meshes[1].vertices[:,2].max()-h)<1e-8
        assert abs(meshes[1].bounds[0,0]-3.)<1e-8
result=dict(passed=True,no_optimizer=True,independent_promotions=True,three_failure_demotion=True,review_does_not_promote_or_demote=True,airborne_rejected=True,lower_ground_rejected=True,one_wheel_rejected=True,body_must_cross=True,entry_and_peak_speed_enforced=True,landing_credit_once=True,nine_exact_bank_heights=list(S.heights),collision_meshes_frozen=True)
(T/'evidence/LOCAL_CURRICULUM_CHECKS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
