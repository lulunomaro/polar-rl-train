"""Necessary source-only mathematical checks; no checkpoint, raw, CUDA or physics."""
from pathlib import Path
import hashlib,json,math,time,traceback
import torch
from direct_wheel_height_command_reward_v1 import CommandReward,modes,evaluate,height_score
H=Path(__file__).resolve().parent;R=H/'reports';R.mkdir(exist_ok=True)
p=CommandReward();checks=[]
def require(v,description):
    value=bool(v);checks.append(dict(passed=value,description=description))
    if not value:raise AssertionError(description)
def packet(n=1):
    return dict(wheel_bottom2=torch.zeros(n,2),world_velocity3=torch.zeros(n,3),world_angular_velocity3=torch.zeros(n,3),request_active=torch.ones(n),heading_cos=torch.ones(n),upright_cos=torch.ones(n),root_y=torch.zeros(n))
def direct(m,near=1.,P=0.,base=.5):
    n=len(m['request_active']);mode=dict(near=torch.full((n,),near),top_support=torch.full((n,),P),base_command_vx=torch.full((n,),base))
    return evaluate(m,mode,torch.full((n,),.023),torch.ones(n))
def main():
    torch.set_num_threads(2)
    require(not torch.cuda.is_initialized(),'CPU only; no local neural GPU')
    # No airborne/force input is accepted by evaluate: zero forces alone cannot pay.
    z=torch.tensor([0.,.005,.01,.012,.05,.1,.2,.269,.27,.271,.35,.5,.54])
    m=packet(len(z));m['wheel_bottom2']=z[:,None].repeat(1,2)
    idle=direct(m)
    require(torch.equal(idle['selected_terms']['both_wheel_height_270_with_forward_command'],torch.zeros_like(z)),'stationary repeated small/high hop gets zero jump-height bonus')
    require(torch.equal(idle['total'],idle['total'][0].expand_as(z)),'stationary height changes do not improve total through flight/height farming')
    m['world_velocity3'][:,0]=.5;moving=direct(m)
    require(bool((height_score(m['wheel_bottom2'])[:9][1:] > height_score(m['wheel_bottom2'])[:9][:-1]).all()),'actual both-wheel height score rises to .27, no early plateau')
    require(float(height_score(torch.tensor([[.27,.27]])))==1.,'both wheel bottoms at270mm are height target')
    require(float(height_score(torch.tensor([[.27,0.]])))==0.,'one wheel at270mm and one on floor earns no both-wheel height score')
    require(float(height_score(torch.tensor([[.35,.35]])))<1.,'height score decreases above target, not .507-.798 body plateau')
    require(float(moving['total'][2])<float(moving['total'][8]),'1cm crossing hop scores less than true270mm at same correct world velocity')
    # The command tracking term has no per-term clipping platform.
    m=packet(4);m['world_velocity3'][:,0]=torch.tensor([.182,.2,.4,.5]);velocity=direct(m,near=0.)
    vterm=velocity['selected_terms']['command_world_velocity']
    require(bool((vterm[1:]>vterm[:-1]).all()),'world speed .182,.2,.4,.5 strictly improve command tracking')
    # General landing monotonicity: |d exp(-e/sigma²)/dP| <= speed sqrt(2/e)/sigma.
    D=p.speed*math.sqrt(2/math.e)/p.velocity_sigma
    margin=p.supported_landing_coefficient-D-p.height_coefficient
    require(margin>0,'top support gain exceeds worst global command-switch and height-bonus loss')
    grid=torch.linspace(0,1,1001);results=[]
    for vx in (-3.5,-.5,0.,.15,.5,1.,3.5):
        m=packet(len(grid));m['wheel_bottom2'][:]=.27;m['world_velocity3'][:,0]=vx
        mode=dict(near=torch.ones_like(grid),top_support=grid,base_command_vx=torch.full_like(grid,.5))
        out=evaluate(m,mode,torch.zeros_like(grid),torch.ones_like(grid))
        require(bool((out['total'][1:]-out['total'][:-1]>=-1e-7).all()),'landing support monotonically improves score at fixed geometry/vx '+str(vx))
        if vx==.15:landing15=[float(out['total'][0]),float(out['total'][-1]),float(out['quiet'][0])]
        results.append(out['total'])
    require(landing15[1]>landing15[0],'at .15m/s, landing supported scores above identical unsupported state')
    # Requested fixed-floor approach counterexample, including low velocity.
    x=torch.linspace(.01,.349,2049);low=torch.stack((torch.stack((x-.24,torch.full_like(x,-.22),torch.zeros_like(x)),-1),torch.stack((x-.24,torch.full_like(x,.22),torch.zeros_like(x)),-1)),1)
    high=low+torch.tensor([.36,.08,.36]);force=torch.full((len(x),2),100.)
    for vx in (0.,.15,.2,.5):
        m=packet(len(x));m['world_velocity3'][:,0]=vx
        mo=modes(low,high,force,x);out=evaluate(m,mo,torch.full_like(x,.023),torch.ones_like(x))
        require(bool((out['total'][1:]-out['total'][:-1]>=-1e-7).all()),'fixed supported-floor approach does not lower reward vx='+str(vx))
    # Far from both wheel front edges: airborne history does not unlock height bonus.
    low=torch.tensor([[[-.3,-.22,.01],[-.3,.22,.01]]]);high=low+torch.tensor([.36,.08,.36]);mo=modes(low,high,torch.zeros(1,2),torch.tensor([.01]));m=packet();m['wheel_bottom2'][:]=.01;m['world_velocity3'][:,0]=.5
    require(float(mo['near'])==0. and float(direct(m,near=0.)['selected_terms']['both_wheel_height_270_with_forward_command'])==0.,'unloaded one-cm hop far from edge cannot unlock jump score')
    # Off-request behavior passes through the original recovery scalar literally.
    m=packet(257);m['request_active'].zero_();legacy=torch.linspace(-.1,.12,257)
    o=evaluate(m,dict(near=torch.ones(257),top_support=torch.zeros(257),base_command_vx=torch.full((257,),.5)),legacy,torch.ones(257))
    require(torch.equal(o['total'],legacy),'nonrequest original recovery preserved literally')
    # Structured independent domain; finite derivatives and exact optimized-term logging.
    n=8192;g=torch.Generator().manual_seed(116)
    z=(torch.rand(n,2,generator=g)*.65-.05).requires_grad_();v=(torch.rand(n,3,generator=g)*7-3.5).requires_grad_();m=packet(n);m['wheel_bottom2']=z;m['world_velocity3']=v
    mo=dict(near=torch.rand(n,generator=g),top_support=torch.rand(n,generator=g),base_command_vx=torch.rand(n,generator=g)-.5)
    out=evaluate(m,mo,torch.zeros(n),torch.full((n,),.9));dz,dv=torch.autograd.grad(out['total'].sum(),(z,v))
    require(bool(torch.isfinite(dz).all() and torch.isfinite(dv).all()),'finite gradients across declared height/velocity/support domain')
    require(torch.equal(out['total'],sum(out['selected_terms'].values())),'logged selected terms sum EXACTLY to optimized total')
    require(bool((out['total']>=0).all() and (out['total']<=.160001).all()),'nonnegative request reward bounded by original max_step_reward.16')
    upper=p.score_scale*p.dt*(1+p.supported_landing_coefficient+p.quiet_coefficient)
    require(abs(upper-.16)<1e-12,'analytic global request upper bound .16')
    report=dict(passed_source_CPU=True,epoch=time.time(),checks=checks,check_count=len(checks),source_SHA=hashlib.sha256((H/'direct_wheel_height_command_reward_v1.py').read_bytes()).hexdigest(),parameters=p.__dict__,
        stationary_height_total=float(idle['total'][0]),moving_1cm_height_term=float(moving['selected_terms']['both_wheel_height_270_with_forward_command'][2]),moving270mm_height_term=float(moving['selected_terms']['both_wheel_height_270_with_forward_command'][8]),
        velocity_points=[.182,.2,.4,.5],velocity_rewards=vterm.tolist(),landing_at_point15=landing15,global_landing_monotonic_margin_before_dt=margin,analytic_request_upper=.16,
        assumptions='structured states may be dynamically inconsistent; instantaneous force surrogate not whole-body airborne truth; no physical feasibility or global optimality proof',
        no_model_or_raw_reads=True,no_runtime_or_SDK_or_GPU_GO=True,adapter_and_actual_readback_pending=True,source_only_not_training=True)
    with (R/'DIRECT_COMMAND_WHEEL_HEIGHT_COUNTEREXAMPLES_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2,allow_nan=False)
    print(json.dumps(dict(passed=True,checks=len(checks),velocity_rewards=vterm.tolist(),landing15=landing15,landing_monotonic_margin=margin)))
if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('ORIGINAL_SOURCE_CPU_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(traceback=traceback.format_exc(),checks=checks),f,indent=2);raise
