"""MOD4v2 P0 kinematic chart and original projected 14state DARE, never integrates.
Only q_from/q_from_full are needed when binding into parent's V2Plant; they use
self.m,self.tmp,self.wheels,self.radius and this module's actual P0 kin_v2 only.
No original asset/legacy source edits, old operating window, or physical reset here.
"""
from pathlib import Path
import importlib.util
import math,sys
import numpy as np
import mujoco
from scipy.optimize import brentq

PACKAGE=Path(r'F:\RMPOLAR-RL\mod4v2_p0_mechanical_limits_20261105\candidates\HW300N60\package')
OLD=Path(r'F:\RMPOLAR-RL\traditional_control_20261101')
sys.path.insert(0,str(OLD))
from full_lqr import AsymmetricPlant
from control_core import ORDER,PAIRS
_spec=importlib.util.spec_from_file_location('mod4v2_public_kinematics',PACKAGE/'kinematics_v2.py')
kin_v2=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=kin_v2;_spec.loader.exec_module(kin_v2)

class V2LinearPlant(AsymmetricPlant):
    """Takes already compiled P0-compatible MjModel; no old Plant/model factory call."""
    def __init__(self,model):
        self.m=model;self.d=mujoco.MjData(model);self.tmp=mujoco.MjData(model)
        self.qids=np.array([int(model.joint(n).qposadr[0])for n in ORDER]);self.vids=np.array([int(model.joint(n).dofadr[0])for n in ORDER])
        self.chassis=model.body('chassis').id;self.wheels=[model.body(s+'_wheel').id for s in('left','right')]
        self.tires=[model.geom(s+'_tire').id for s in('left','right')]
        radii=[float(model.geom_size[i,0])for i in self.tires]
        if not all(int(model.geom_type[i])==int(mujoco.mjtGeom.mjGEOM_CYLINDER)for i in self.tires)or not np.isfinite(radii).all()or radii[0]<=0 or abs(radii[0]-radii[1])>1e-12:
            raise ValueError('Expected the actual equal-radius P0 cylinder tires, not v1 mesh radius')
        self.radius=radii[0];self.mass=float(model.body_mass.sum())
        self.pairs=[(model.site(a).id,model.site(b).id)for a,b in PAIRS]
        self.KP=60.;self.KD=2.;self.wKD=.6;self.dt=float(model.opt.timestep);self.substeps=20
        self.max_tau=np.maximum(np.abs(model.actuator_ctrlrange[:,0]),np.abs(model.actuator_ctrlrange[:,1]))
        self.stall=np.array([53.3333333333333,53.3333333333333,28.18532894736838]*2)
        self.no_load=np.array([16.755160819145562,16.755160819145562,55.3557]*2)
        self.history=[];self.applied=[];self.dr=None;self.observed=None;self.tick_phys=0
        self._equilibrium_cache={}
        if model.nu!=6 or not np.array_equal(model.actuator_trnid[:,0],[model.joint(n).id for n in ORDER])or not np.array_equal(model.actuator_gear[:,0],np.ones(6)):
            raise ValueError('Original projected torque matrix requires actual six gear1 joint actuators')

    def q_from_full(self,q):
        q=np.asarray(q,float)
        if q.shape!=(7,)or not np.isfinite(q).all():raise ValueError('finite seven-coordinate chart required')
        x,yaw,theta,hl,dl,hr,dr=q;d=self.tmp;m=self.m
        mujoco.mj_resetData(m,d)
        # API ABSOLUTE hip/crank. Keep public mechanical-domain checking enabled.
        kin_v2.set_configuration(m,d,left=(hl,hl+dl),right=(hr,hr+dr),check_limits=True)
        pL=d.xpos[self.wheels[0]]-d.qpos[:3];pR=d.xpos[self.wheels[1]]-d.qpos[:3]
        roll=-math.atan2(float(pL[2]-pR[2]),float(pL[1]-pR[1]))
        cr,sr=math.cos(roll/2),math.sin(roll/2);cp,sp=math.cos(theta/2),math.sin(theta/2);cy,sy=math.cos(yaw/2),math.sin(yaw/2)
        d.qpos[:3]=[x,0.,0.];d.qpos[3:7]=[cr*cp*cy+sr*sp*sy,sr*cp*cy-cr*sp*sy,cr*sp*cy+sr*cp*sy,cr*cp*sy-sr*sp*cy]
        mujoco.mj_forward(m,d)
        d.qpos[2]=self.radius-float(np.mean(d.xpos[self.wheels,2]))
        for side,h,lat in(('left',hl,float(pL[1])),('right',hr,float(pR[1]))):
            wc=d.xpos[m.body(side+'_wheel').id];knee=float(d.joint(side+'_knee').qpos[0])
            # Original local no-slip rolling chart, exact at zero yaw; not all-terrain contact.
            d.joint(side+'_wheel_spin').qpos[0]=(x+(wc[0]-x)*math.cos(yaw)+wc[1]*math.sin(yaw)-lat*yaw)/self.radius-theta-h-knee
        mujoco.mj_forward(m,d)
        return d.qpos.copy()

    def q_from(self,q,derivative=False):
        q=np.asarray(q,float)
        if q.shape!=(4,)or not np.isfinite(q).all():raise ValueError('finite symmetric chart4 required')
        x,theta,h,delta=q
        return V2LinearPlant.q_from_full(self,[x,0.,theta,h,delta,h,delta])

    def equilibrium(self,delta=-.2):
        delta=float(delta)
        if delta in self._equilibrium_cache:
            q,t,res=self._equilibrium_cache[delta];return q.copy(),t.copy(),res
        def misalign(h):
            self.chart([0.,0.,h,delta]);return float(self.tmp.subtree_com[self.chassis,0]-np.mean(self.tmp.xpos[self.wheels,0]))
        # Selected upright COM-alignment root bracket, NOT an actuator hard window.
        lo,hi=-math.pi/2,math.pi/2;fl,fh=misalign(lo),misalign(hi)
        if fl*fh>=0.:raise ValueError('Upright COM root not bracketed; no legacy window/fallback pose invented')
        h=brentq(misalign,lo,hi,xtol=1e-12);q=np.array([0.,0.,h,delta])
        M,f,B=self.reduced(q);tau=np.linalg.lstsq(B,-f,rcond=None)[0];res=float(np.linalg.norm(B@tau+f))
        self._equilibrium_cache[delta]=(q.copy(),tau.copy(),res)
        return q,tau,res
