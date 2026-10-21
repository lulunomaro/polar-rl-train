"""Enclose original saved GPU support arithmetic, without changing a physical guard.

Inputs and geometry constants are rounded as in the original float32 implementation.
Every scalar operation is enclosed by |fl(x)-x| <= eps32*|x| + tiny32.
Dot reductions use gamma(2*n+1)*sum(abs(products)), covering FMA and order.
This deliberately uses eps32 rather than unit roundoff for a conservative enclosure.
Float64 work is outward padded with nextafter. No simulation or CUDA is invoked.
"""
import numpy as np
EPS = float(np.finfo(np.float32).eps)
TINY = float(np.finfo(np.float32).tiny)

def rounded(lo, hi):
    delta = EPS * np.maximum(np.abs(lo), np.abs(hi)) + TINY
    return I(np.nextafter(lo-delta, -np.inf), np.nextafter(hi+delta, np.inf))

class I:
    def __init__(self, lo, hi=None):
        self.lo = np.asarray(lo, dtype=np.float64)
        self.hi = self.lo if hi is None else np.asarray(hi, dtype=np.float64)
    def __add__(self, other):
        o = as_i(other); return rounded(self.lo+o.lo, self.hi+o.hi)
    def __sub__(self, other):
        o = as_i(other); return rounded(self.lo-o.hi, self.hi-o.lo)
    def __mul__(self, other):
        o=as_i(other)
        z=np.stack(np.broadcast_arrays(self.lo*o.lo,self.lo*o.hi,self.hi*o.lo,self.hi*o.hi))
        return rounded(z.min(0),z.max(0))
    def absolute(self):
        lo=np.where(self.lo>=0,self.lo,np.where(self.hi<=0,-self.hi,0))
        return I(lo,np.maximum(abs(self.lo),abs(self.hi)))
    def square(self):
        a=self.absolute();return rounded(a.lo*a.lo,a.hi*a.hi)
    def sqrt_nonnegative(self):
        return rounded(np.sqrt(np.maximum(0,self.lo)),np.sqrt(np.maximum(0,self.hi)))
    def part(self, k): return I(self.lo[...,k],self.hi[...,k])

def as_i(v):
    return v if isinstance(v,I) else I(np.asarray(v,dtype=np.float32).astype(np.float64))

def reduction_sum(a):
    n=a.lo.shape[-1]; gamma=(2*n+1)*EPS/(1-(2*n+1)*EPS)
    lo=a.lo.sum(-1);hi=a.hi.sum(-1)
    delta=gamma*np.maximum(abs(a.lo),abs(a.hi)).sum(-1)+n*TINY
    return I(np.nextafter(lo-delta,-np.inf),np.nextafter(hi+delta,np.inf))

def stack(a):return I(np.stack([x.lo for x in a],-1),np.stack([x.hi for x in a],-1))

def enclose_original_support(pos, quat, shapes):
    assert pos.dtype==quat.dtype==np.float32
    outputs=[]
    for s in shapes:
        q=I(quat[...,s['body_index'],:]);x,y,z,w=[q.part(k) for k in range(4)]
        rz=stack([(x*z-w*y)*2,(y*z+w*x)*2,as_i(1)-(x.square()+y.square())*2])
        L=np.asarray(s['linear_body_from_shape'],dtype=np.float32)
        row=stack([reduction_sum(rz*L[:,k]) for k in range(3)])
        center=I(pos[...,s['body_index'],2])+reduction_sum(rz*np.asarray(s['origin_body_m'],dtype=np.float32))
        kind=s['type']
        if kind=='Cube':extent=reduction_sum(row.absolute())*s['size']*.5
        elif kind in ('Capsule','Cylinder'):
            axial=row.part(s['axis']).absolute();norm2=reduction_sum(row.square())
            radial=(norm2-axial.square()).sqrt_nonnegative()
            extent=axial*s['height']*.5+(norm2.sqrt_nonnegative() if kind=='Capsule' else radial)*s['radius']
        elif kind=='Sphere':extent=reduction_sum(row.square()).sqrt_nonnegative()*s['radius']
        elif kind=='Mesh':
            points=np.asarray(s['points'],dtype=np.float32)
            values=[reduction_sum(row*v) for v in points]
            low=np.stack([v.lo for v in values],-1).min(-1)
            high=np.stack([v.hi for v in values],-1).min(-1)
            outputs.append(center+I(low,high));continue
        else:raise ValueError('Unknown authored collider: '+kind)
        outputs.append(center-extent)
    final=stack(outputs)
    return final.lo, final.hi
