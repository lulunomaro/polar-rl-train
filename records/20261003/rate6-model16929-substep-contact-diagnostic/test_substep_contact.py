"""Physical-point GPU-kernel arithmetic checked on Warp CPU, no simulator."""
import torch,warp as wp
from substep_contact_readback import aggregate,COLUMNS
wp.init()
def run(forces,points,vel,com=(0.,0.,0.),count=2,steps=20):
    def arr(x,dtype=None):return wp.from_torch(torch.tensor(x,dtype=torch.float32),dtype=dtype)
    f=arr(forces);p=arr(points,wp.vec3);norm=arr([[0.,0.,1.]]*len(forces),wp.vec3);sep=arr([0.]*len(forces))
    ct=wp.from_torch(torch.tensor([[count],[0]],dtype=torch.int32));st=wp.from_torch(torch.tensor([[0],[count]],dtype=torch.int32))
    lp=arr([[[0.,0.,0.,0.,0.,0.,1.],[0.,0.,0.,0.,0.,0.,1.]]],wp.transform)
    cp=arr([[[*com,0.,0.,0.,1.],[0.,0.,0.,0.,0.,0.,1.]]],wp.transform)
    vc=arr([[vel,[0.]*6]],wp.spatial_vector)
    lin=torch.tensor(vel[:3])-torch.cross(torch.tensor(vel[3:]),torch.tensor(com),dim=0)
    vl=arr([[[*lin.tolist(),*vel[3:]],[0.]*6]],wp.spatial_vector)
    ids=wp.from_torch(torch.tensor([0,1],dtype=torch.int32));v=arr([[[0.,0.,-.1]],[[0.,0.,-.1]]],wp.vec3)
    axis=arr([[0.,-1.,0.],[0.,-1.,0.]],wp.vec3);valid=wp.from_torch(torch.tensor([1],dtype=torch.int32))
    stat=torch.zeros(1,2,len(COLUMNS));runs=torch.zeros(1,2,dtype=torch.int32);err=torch.zeros(2,dtype=torch.int32)
    for i in range(steps):wp.launch(aggregate,dim=(1,2),inputs=[f,p,norm,sep,ct,st,lp,cp,vc,vl,ids,v,axis,valid,wp.from_torch(stat),wp.from_torch(runs),wp.from_torch(err),.0005,int(i==steps-1),len(forces)],device='cpu')
    return stat,err
x,e=run([20.,20.],[[0.,0.,-.1],[0.,0.,-.1]],[1.,0.,0.,0.,10.,0.]);assert not e.any() and x[0,0,5]<1e-5 and x[0,0,1]==20 and x[0,1,1]==0
x,e=run([20.,20.],[[.1,0.,0.],[-.1,0.,0.]],[0.,0.,0.,0.,0.,2.]);assert abs(float(x[0,0,5]/20)-.2)<1e-5
x,e=run([20.,0.],[[0.,0.,0.],[10.,0.,0.]],[.1,0.,0.,0.,0.,2.]);assert abs(float(x[0,0,6])-.1)<1e-5 # zero-force point excluded from peak
x,e=run([20.,20.],[[0.,0.,-.1],[0.,0.,-.1]],[1.02,0.,0.,0.,10.,0.],com=(0.,0.,.002));assert x[0,0,19]<1e-5
x,e=run([0.,0.],[[0.,0.,0.],[0.,0.,0.]],[1.,0.,0.,0.,0.,0.]);assert x[0,0,1]==0 and abs(float(x[0,0,8])*.0005-.01)<1e-7
x,e=run([20.,20.],[[0.,0.,0.],[0.,0.,0.]],[0.]*6,count=65,steps=1);assert e[0]>0
print('Six Warp CPU checks passed: rolling cancellation, per-point norm, zero-force peak exclusion, COM/link equivalence, unloaded time, capacity rejection.')
