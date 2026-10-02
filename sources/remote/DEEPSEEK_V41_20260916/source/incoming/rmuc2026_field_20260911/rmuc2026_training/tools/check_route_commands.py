"""Meaningful route-gate regressions: reject floor shortcuts and fake jump goals."""
from pathlib import Path
import sys,json,math
import torch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'isaac'))
from route_commands import RouteCommands

def main():
    manager=RouteCommands(torch.tensor([[0.,0.,0.],[34.,0.,0.],[68.,0.,0.],[102.,0.,0.]]),.336)
    names=[r['id'] for r in manager.routes]
    chosen=[names.index(n) for n in ['fly_jump','flat_jump','slope_spin','flat_run']]
    state=manager.reset(torch.arange(4),chosen)
    yaw=torch.zeros(4);rate=torch.zeros(4);contact=torch.ones(4,dtype=torch.bool);stable=contact.clone()
    p=state[:,:3].clone()
    p[0,:2]=manager.origins[0,:2]+manager.goals[chosen[0],:2];p[0,2]=.154
    r=manager.update(p,yaw,rate,contact,stable,.02)
    assert not r['success'][0], 'Driving through the trench must not count as a fly jump.'
    assert not r['success'][1], 'A jump route may not complete just by standing at its goal.'
    assert not r['success'][2], 'A spin route must accumulate an actual turn.'
    p[3,:]=manager.origins[3]+manager.goals[chosen[3]]+torch.tensor([0.,0.,.336])
    r=manager.update(p,yaw,rate,contact,stable,.02)
    assert r['success'][3], 'The flat route should finish at a supported goal.'
    r=manager.update(p,yaw,rate,contact,stable,.02)
    assert not r['success'][3], 'Success bonus must only be delivered once.'
    p[0]=torch.tensor([-.35,-6.94,.70]);contact[0]=True
    manager.update(p,yaw,rate,contact,stable,.02)
    contact[0]=False
    for _ in range(5):manager.update(p,yaw,rate,contact,stable,.02)
    p[0]=manager.goals[chosen[0]]+torch.tensor([0.,0.,.336]);contact[0]=True
    r=manager.update(p,yaw,rate,contact,stable,.02)
    assert r['success'][0], 'A launch, airborne interval and supported far goal should pass.'
    spin_sign=torch.sign(manager.spin_speed[2])
    # Repeated +/- yaw motion is not a complete revolution.
    for i in range(200):
        rate[2]=4.*spin_sign*(1 if i%2==0 else -1)
        r=manager.update(p,yaw,rate,contact,stable,.02)
    assert not r['completed'][2], 'Oscillation may not count as a full spin.'
    rate[2]=4.*spin_sign
    for _ in range(90):r=manager.update(p,yaw,rate,contact,stable,.02)
    assert r['completed'][2]
    tunnel_id=names.index('tunnel')
    state=manager.reset(torch.tensor([0]),[tunnel_id]);p[0]=manager.goals[tunnel_id]+torch.tensor([0.,0.,.336])
    r=manager.update(p,yaw,rate,contact,stable,.02)
    assert not r['success'][0], 'Crossing above the highway may not count as passing below it.'
    p[0]=torch.tensor([.925,-5.95,.040]);manager.update(p,yaw,rate,contact,stable,.02)
    p[0]=manager.goals[tunnel_id]+torch.tensor([0.,0.,.336])
    r=manager.update(p,yaw,rate,contact,stable,.02)
    assert r['success'][0], 'An under-roof crossing followed by a supported goal should pass.'
    report=dict(status='PASS_ROUTE_GATES',cases=10,scope='Synthetic event inputs, not learned robot behavior.')
    (ROOT/'reports/route_gate_tests.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(report)

if __name__=='__main__':main()
