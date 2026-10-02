"""Build constraint-consistent MOD4 reset configurations from the USD contract.

No guessed link lengths: evaluate the authored joint frames and closure anchors.
Only poses on the same branch as q=0, within authored limits, are accepted.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation


def rot(q):
    return Rotation.from_quat(np.roll(q, -1)).as_matrix()


class Leg:
    def __init__(self, contract, side):
        self.c, self.side = contract, side
        self.js = {n: s for n, s in contract['joints'].items() if n.startswith(side+'_')}
        self.frames = {n:(rot(s['local_rot0']),rot(s['local_rot1']),np.array(s['local_pos0']),np.array(s['local_pos1'])) for n,s in self.js.items()}
        self.names = [n for n in self.js if n not in contract['mimics'] and 'wheel_spin' not in n]
        self.bounds = np.array([self.js[n]['limits_si'] or [-3.14,3.14] for n in self.names]).T
        self.closures = [s for s in contract['closures'].values() if s['body0'].startswith(side+'_')]

    def fk(self, x):
        q = dict(zip(self.names,x))
        for n,s in self.c['mimics'].items():
            if n.startswith(self.side+'_'):
                q[n] = -s['gearing']*q[s['reference_joint']]+s['offset']
        poses = {'chassis':(np.zeros(3),np.eye(3))}
        todo = dict(self.js)
        while todo:
            changed=False
            for n,s in list(todo.items()):
                if s['parent'] not in poses: continue
                p,R=poses[s['parent']]; r0,r1,a,b=self.frames[n]; v=q.get(n,0.)
                if s['type']=='hinge':
                    cv,sv=np.cos(v),np.sin(v)
                    rx=np.array([[1,0,0],[0,cv,-sv],[0,sv,cv]])
                    childR=R@r0@rx@r1.T
                    childp=p+R@a-childR@b
                else:
                    childR=R@r0@r1.T
                    childp=p+R@(a+r0[:,0]*v)-childR@b
                poses[s['child']] = (childp,childR)
                del todo[n];changed=True
            if not changed: raise ValueError('not a tree')
        return poses,q

    def closure(self, poses):
        residual=[]
        for s in self.closures:
            p0,r0=poses[s['body0']];p1,r1=poses[s['body1']]
            residual.extend(p0+r0@np.array(s['anchor0_m'])-p1-r1@np.array(s['anchor1_m']))
        return np.array(residual)

    def solve(self, height, wheel_x, seed=None):
        target=np.array([wheel_x,-height+0.0625])
        def fun(x):
            poses,_=self.fk(x)
            wheel=poses[self.side+'_wheel'][0]
            return np.r_[self.closure(poses),wheel[[0,2]]-target]
        ans=least_squares(fun,np.zeros(len(self.names)) if seed is None else seed,
            bounds=(self.bounds[0]+1e-7,self.bounds[1]-1e-7),xtol=1e-11,ftol=1e-11,gtol=1e-11,max_nfev=250)
        poses,q=self.fk(ans.x)
        return ans,poses,q


def main():
    a=argparse.ArgumentParser();a.add_argument('--contract',default='target_contract.json');a.add_argument('--output',default='reset_bank.json');args=a.parse_args()
    path=Path(args.contract);c=json.loads(path.read_text(encoding='utf8'))
    legs=[Leg(c,s) for s in ['left','right']]
    for leg in legs:
        poses,_=leg.fk(np.zeros(len(leg.names)))
        assert np.max(np.abs(leg.closure(poses)))<1e-8
        for n,(p,R) in poses.items():
            assert np.linalg.norm(p-np.array(c['bodies'][n]['neutral_position_m']))<1e-8,n
            assert np.linalg.norm(R-rot(c['bodies'][n]['neutral_quat_wxyz']))<1e-8,n
    bank=[];fail=[]
    for h in np.linspace(.23,.29,13):
        for wx in np.linspace(-.04,.01,11):
            row={};err=0.;closures=0.
            for leg in legs:
                ans,poses,q=leg.solve(float(h),float(wx))
                err=max(err,float(np.max(np.abs(ans.fun))))
                closures=max(closures,float(np.linalg.norm(leg.closure(poses).reshape(-1,3),axis=1).max()))
                row.update(q)
            if err<1e-6:
                bank.append({'joint_pos':row,'root_height_m':float(h+.002),'wheel_x_m':float(wx),'closure_m':closures,'ik_max_residual_m':err})
            else: fail.append({'height':float(h),'wheel_x':float(wx),'residual':err})
    out={'contract_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'radius_m':.0625,'notes':'Symmetric flat resets, 2 mm wheel-ground gap. Full 22-coordinate closed-loop state. Wheels/rollers start at zero. Authored frames checked at neutral.','poses':bank,'rejected':fail}
    Path(args.output).write_text(json.dumps(out,indent=2),encoding='utf8')
    print('accepted',len(bank),'rejected',len(fail))
    if bank:
        print('height range',min(x['root_height_m'] for x in bank),max(x['root_height_m'] for x in bank))
        print('max closure',max(x['closure_m'] for x in bank))
        print('sample',bank[len(bank)//2])
    else: print('best',sorted(fail,key=lambda x:x['residual'])[:4])


if __name__=='__main__':main()
