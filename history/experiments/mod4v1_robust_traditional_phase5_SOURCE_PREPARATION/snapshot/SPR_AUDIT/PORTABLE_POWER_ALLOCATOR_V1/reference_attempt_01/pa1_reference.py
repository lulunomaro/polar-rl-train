"""Independent exact rational electrical-envelope reference; no core/physics import."""
from fractions import Fraction as F
import math

def q(v):return v if isinstance(v,F)else F.from_float(float(v))
def metrics(tau,d):
    t=list(map(q,tau));current=[abs(x)/q(k)for x,k in zip(t,d['K'])]
    positive=q(d['Pe']);charge=F(0)
    for i,x in enumerate(t):
        pos=max(F(0),x*q(d['wlo'][i]),x*q(d['whi'][i]))
        neg=max(F(0),-x*q(d['wlo'][i]),-x*q(d['whi'][i]))
        positive+=pos/q(d['drive'][i])+q(d['Cbus'][i])*current[i]**2
        charge+=neg*q(d['regen'][i])
    return[positive,charge,positive/q(d['Vlo']),charge/q(d['Vlo'])]+current

def limits(d):return list(map(q,[d['Pmax'],d['Gmax'],d['Idis'],d['Ichg']]+d['Imax']))
def inside_box(tau,d):return all(q(a)<=q(t)<=q(b)for a,t,b in zip(d['lo'],tau,d['hi']))
def feasible(tau,d):return inside_box(tau,d)and all(a<=b for a,b in zip(metrics(tau,d),limits(d)))
def line(d,s):return[q(a)+s*(q(b)-q(a))for a,b in zip(d['reserve'],d['request'])]
def normalized(tau,d):
    vals=metrics(tau,d);caps=limits(d)
    return max((a/b for a,b in zip(vals,caps)if b>0),default=F(0))
def oracle(d):
    if not feasible(d['reserve'],d):return dict(reserve_feasible=False)
    if feasible(d['request'],d):lo=hi=F(1)
    else:
        lo=F(0);hi=F(1)
        for _ in range(80):
            mid=(lo+hi)/2
            if feasible(line(d,mid),d):lo=mid
            else:hi=mid
    center=(lo+hi)/2;h=F(1,2**20);a=max(F(0),center-h);b=min(F(1),center+h)
    slope=(normalized(line(d,b),d)-normalized(line(d,a),d))/(b-a)
    return dict(reserve_feasible=True,s_lo=lo,s_hi=hi,well_conditioned=slope>=F(1,10000),slope=float(slope))
