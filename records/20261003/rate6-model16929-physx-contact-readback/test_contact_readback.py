"""CPU checks for frame, weighted speed, unloaded coverage, and buffer rejection."""
from types import SimpleNamespace as NS
import torch
from physx_contact_readback import PhysXContactReadback

class View:
    sensor_count=2;filter_count=1
    def __init__(self):
        self.values=(torch.tensor([20.,20.,0.]),torch.tensor([[0.,0.,-.1],[0.,0.,-.1],[0.,0.,0.]]),torch.tensor([[0.,0.,1.],[0.,0.,1.],[0.,0.,1.]]),torch.zeros(3),torch.tensor([[2],[0]]),torch.tensor([[0],[2]]))
    def get_contact_data(self,dt):assert dt==.0005;return self.values
v=View();sensor=NS(body_names=['left_wheel','right_wheel'],contact_view=v,cfg=NS(filter_prim_paths_expr=['/World/ground/geometry/mesh']))
data=NS(body_link_pos_w=torch.zeros(1,2,3),body_link_lin_vel_w=torch.tensor([[[1.,0.,0.],[9.,0.,0.]]]),body_ang_vel_w=torch.tensor([[[0.,10.,0.],[0.,0.,0.]]]))
env=NS(scene={'robot':NS(data=data)},device='cpu',num_envs=1,physics_dt=.0005,step_dt=.01)
env.scene=NS(__getitem__=None,sensors={'wheel_contact_scut':sensor}) if False else env.scene
class Scene(dict):pass
env.scene=Scene(env.scene);env.scene.sensors={'wheel_contact_scut':sensor}
x=PhysXContactReadback(env,NS(ids=[0,1]));x.read(torch.tensor([[.2,.2]]),torch.tensor([[40.,0.]]),torch.tensor([True]),50)
r=x.result();assert r['loaded_samples']==[[1.,0.]] and r['loaded_contact_sample_fraction']==[[1.,0.]]
assert r['per_environment_loaded_mean']['individual_contact_force_weighted_tangent_speed'][0][0]<1e-6
assert r['buffer_metadata']['body_names']==['left_wheel','right_wheel']
data.body_link_lin_vel_w[0,0,0]=1.2
x=PhysXContactReadback(env,NS(ids=[0,1]));x.read(torch.tensor([[.2,.2]]),torch.tensor([[40.,0.]]),torch.tensor([True]),50)
assert abs(x.result()['per_environment_loaded_mean']['individual_contact_force_weighted_tangent_speed'][0][0]-.2)<1e-6
data.body_link_lin_vel_w.zero_();data.body_ang_vel_w.zero_();data.body_ang_vel_w[0,0,2]=2.
v.values=(torch.tensor([20.,20.,0.]),torch.tensor([[.1,0.,0.],[-.1,0.,0.],[0.,0.,0.]]),v.values[2],v.values[3],v.values[4],v.values[5])
x=PhysXContactReadback(env,NS(ids=[0,1]));x.read(torch.tensor([[.2,.2]]),torch.tensor([[40.,0.]]),torch.tensor([True]),50)
r=x.result()['per_environment_loaded_mean'];assert abs(r['individual_contact_force_weighted_tangent_speed'][0][0]-.2)<1e-6 and r['contact_resultant_tangent_speed'][0][0]==0
original=v.values;v.values=original[:4]+(torch.tensor([[65],[0]]),original[5])
try:PhysXContactReadback(env,NS(ids=[0,1])).read(torch.zeros(1,2),torch.zeros(1,2),torch.tensor([True]),0)
except AssertionError:pass
else:raise AssertionError('Did not reject truncated buffers')
print('Five CPU contact readback checks passed; no physics claim.')
