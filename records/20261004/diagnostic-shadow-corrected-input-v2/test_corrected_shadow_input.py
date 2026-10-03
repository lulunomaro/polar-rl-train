"""CPU reference checks for accepting corrected input and retaining legacy stats."""
import ast,types
from pathlib import Path
import torch
tree=ast.parse(Path(__file__).with_name('slip_shadow_corrected_input_v2.py').read_text())
cl=next(v for v in tree.body if isinstance(v,ast.ClassDef) and v.name=='SlipShadow')
method=next(v for v in cl.body if isinstance(v,ast.FunctionDef) and v.name=='read')
ns={'torch':torch,'tensor':lambda v:v,'quat_apply':lambda q,v:v}
exec(compile(ast.Module(body=[method],type_ignores=[]),'<shadow_input_cpu>','exec'),ns)
def case(offset):
 n=1;points=torch.tensor([[[[0.,.01,-.0637]],[[0.,-.01,-.0637]]]])
 w=torch.tensor([[[0.,20.,6.],[0.,-20.,6.]]]);com=torch.tensor([[[0.,offset,0.],[0.,-offset,0.]]])
 link=torch.tensor([[[1.274,0.,0.],[-1.274,0.,0.]]]);comvel=link+torch.cross(w,com,dim=-1)
 q=torch.tensor([[[1.,0.,0.,0.],[1.,0.,0.,0.]]]);pos=torch.zeros(1,2,3)
 data=types.SimpleNamespace(body_quat_w=q,body_ang_vel_w=w,body_lin_vel_w=comvel,body_link_lin_vel_w=link,body_link_pos_w=pos,body_com_lin_vel_w=comvel,body_com_pos_w=com)
 s=types.SimpleNamespace(robot=types.SimpleNamespace(data=data),env=types.SimpleNamespace(num_envs=1),ids=[0,1],points=points[0],geometry=types.SimpleNamespace(vertices=points),com_body=com,axes=torch.tensor([[[0.,1.,0.],[0.,1.,0.]]]),centers=torch.zeros(1,2,3),sums={},loaded_sums={},peaks={},counts=torch.zeros(1,2),loaded_counts=torch.zeros(1,2),trace_ids=None)
 arm=points[:,:,0];correct=(link+torch.cross(w,arm,dim=-1))[:,:,:2].norm(dim=-1)
 legacy=(comvel+torch.cross(w,arm,dim=-1))[:,:,:2].norm(dim=-1)
 ns['read'](s,correct,torch.ones(1,2)*20,torch.ones(1,dtype=torch.bool),0)
 assert torch.equal(s.sums['legacy_slip'],legacy) and torch.equal(s.sums['input_mesh_slip'],correct)
 assert float(s.sums['link_vs_com_local_error'].max())<1e-6
 return s,correct,legacy
s,correct,legacy=case(.001668);assert not torch.allclose(correct,legacy)
try:ns['read'](s,legacy,torch.ones(1,2)*20,torch.ones(1,dtype=torch.bool),1)
except AssertionError:pass
else:raise AssertionError('Mixed legacy input must not pass the corrected reference assertion')
s,correct,legacy=case(0.);assert torch.equal(correct,legacy)
print('Three shadow CPU checks passed: corrected link input accepted, legacy statistic preserved; mixed input rejected; zero COM offset consistent.')
