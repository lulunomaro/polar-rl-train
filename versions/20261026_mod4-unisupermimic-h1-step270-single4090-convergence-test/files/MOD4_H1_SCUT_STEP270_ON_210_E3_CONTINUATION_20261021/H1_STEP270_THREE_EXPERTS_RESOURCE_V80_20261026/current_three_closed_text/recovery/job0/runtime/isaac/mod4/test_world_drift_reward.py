import json, math
import torch
from world_drift_reward import CycleCrossDrift


def run():
    torch.set_num_threads(1)
    # 72 exact kinematic cases, including both signs, world headings and phases.
    cases = [(v,w,a,p) for v in (.15,.3,.5) for w in (-2.,-1.,1.,2.)
             for a in (0.,math.pi/3,math.pi/2) for p in (0.,.73)]
    v,w,a,p = [torch.tensor(x,dtype=torch.float64) for x in zip(*cases)]
    normal = torch.stack((-a.sin(),a.cos()),1)
    along = torch.stack((a.cos(),a.sin()),1)
    max_ideal = 0
    output = {}
    for bias in (0., .06, -.06):
        t = CycleCrossDrift(len(cases),dtype=torch.float64)
        for k in range(1701):
            time=k*.01; phi=p+w*time
            netalong=v*time+v/(2*w)*(torch.sin(2*phi)-torch.sin(2*p))
            cross=-v/(2*w)*(torch.cos(2*phi)-torch.cos(2*p))+bias*time
            xy=netalong[:,None]*along+cross[:,None]*normal
            result=t.update(xy,torch.atan2(torch.sin(phi+a),torch.cos(phi+a)),a,w,v,
                            torch.ones(len(cases),dtype=torch.bool),torch.full_like(v,time),.01)
            if bias==0: max_ideal=max(max_ideal,float(result.abs().max()))
        assert bool((t.cycles>=2).all())
        assert float((result-bias).abs().max()) < 8e-6
        output[str(bias)]=float((result-bias).abs().max())
    assert max_ideal < 2e-5, max_ideal
    # Resampling, episode reset, inactive modes and clamped excessive drift.
    t.reset([0]);assert not t.valid[0] and t.net_cross[0]==0
    z=torch.zeros_like(v);active=torch.zeros(len(cases),dtype=torch.bool)
    assert torch.equal(t.update(xy,phi+a,a,w,v,active,z,.01),z)
    t.update(xy,phi+a,a,w,v,~active,z,.01)
    moved=xy+normal*100
    t.update(moved,phi+a,a,w,v,~active,z+.01,.01)
    assert t.cost().max()==4 and torch.isfinite(t.cost()).all()
    # A new command clock/direction discards old accumulation.
    assert torch.equal(t.update(moved,phi+a,a+1,w,v,~active,z,.01),z)
    output.update(pass_=True,ideal_72_max_speed_error=max_ideal,case_count=72,
                  known_bias_signs=True,resample_reset_inactive_clamp=True)
    print(json.dumps(output));return output

if __name__=='__main__':run()
