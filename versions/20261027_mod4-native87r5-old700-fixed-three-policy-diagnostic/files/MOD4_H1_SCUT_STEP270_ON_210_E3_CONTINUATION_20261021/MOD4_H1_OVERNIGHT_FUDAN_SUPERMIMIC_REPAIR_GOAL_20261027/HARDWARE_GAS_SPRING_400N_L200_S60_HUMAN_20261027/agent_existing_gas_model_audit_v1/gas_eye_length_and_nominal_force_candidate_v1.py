"""Pure source-derived gas-eye geometry and UNADMITTED nominal force proposals.

No SDK, asset/model load, actor, physical forward, force write or training.
The400N label is a force, never stiffness. Hardware force/stroke/friction curves
are unknown. Functions below are quasistatic source math, not a calibration.
"""
from dataclasses import dataclass
import math

def require(v,message):
 if not v:raise ValueError(message)
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def mul(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):return math.sqrt(dot(a,a))
def mv(R,v):return tuple(dot(row,v) for row in R)
def tr(R):return tuple(zip(*R))
def mm(A,B):return tuple(tuple(dot(a,b) for b in tr(B)) for a in A)
def quaternion_matrix_wxyz(q):
 length=norm(q);require(length>0 and math.isfinite(length),'finite nonzero authored quaternion')
 w,x,y,z=(v/length for v in q)
 return ((1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)),(2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)),(2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)))

@dataclass(frozen=True)
class GasEyeMap:
 side:str
 d:tuple
 u:tuple
 original_q_limits_m:tuple
 original_target_q_m:float
 original_stiffness_N_per_m:float
 original_damping_Ns_per_m:float
 def length_m(self,q):return norm(add(self.d,mul(self.u,float(q))))
 def dlength_dq(self,q):return dot(add(self.d,mul(self.u,float(q))),self.u)/self.length_m(q)
 def q_for_length_m(self,length):
  require(math.isfinite(length) and length>0,'positive finite hole-centre length')
  a=dot(self.u,self.u);b=2*dot(self.d,self.u);c=dot(self.d,self.d)-length*length
  disc=b*b-4*a*c;require(disc>=0,'requested length has no recorded-frame solution')
  q=(-b+math.sqrt(disc))/(2*a)
  require(self.dlength_dq(q)>0,'only same monotone extension branch')
  return q
 def old_quasistatic_joint_effort_N(self,q,k_factor=1.):return self.original_stiffness_N_per_m*k_factor*(self.original_target_q_m-q)

def from_import_contract(contract,side):
 require(side in ('left','right'),'named side required')
 pin=contract['joints'][side+'_gas_pin'];slide=contract['joints'][side+'_gas_slide'];closure=contract['closures'][side+'_gas_closure'];law=contract['gas_springs'][side+'_gas_slide']
 require(pin['child']==slide['parent']==side+'_gas_inner' and slide['child']==closure['body0']==side+'_gas_barrel','actual pin/slide/gas-end topology')
 require(pin['type']=='hinge' and slide['type']=='slide','recorded hinge and prismatic required')
 # PinA is its child-side anchor in inner coordinates. Gas closure's body0
 # anchor is the barrel-end eye; body1 is the coincident shin mounting point
 # only when the original physical closure is satisfied.
 R0=quaternion_matrix_wxyz(slide['local_rot0']);R1=quaternion_matrix_wxyz(slide['local_rot1'])
 d=sub(add(slide['local_pos0'],mv(mm(R0,tr(R1)),sub(closure['anchor0_m'],slide['local_pos1']))),pin['local_pos1'])
 u=tuple(row[0] for row in R0) # Actual pinned exporter uses Prismatic axis X.
 return GasEyeMap(side,d,u,tuple(slide['limits_si']),float(law['target_position_m']),float(law['stiffness_n_m']),float(law['damping_n_s_m']))

def constant400_nominal_quasistatic_candidate(mapping,q):
 """Unadmitted axial400N approximation, no invented progressivity/friction.

 Constant force is a deliberately declared approximation. Generalized
 prismatic effort = F_axial*dL/dq by virtual work; never400 N/m.
 No velocity law/SDK actuator setter or physical travel limit is implemented.
 """
 return dict(axial_force_N=400.,joint_effort_N=400.*mapping.dlength_dq(q),
  status='UNADMITTED_NOMINAL_QUASISTATIC_APPROXIMATION_NOT_HARDWARE_CURVE',
  damping_friction_hysteresis_temperature_and_force_measurement='UNKNOWN')
def linear400_anchor_candidate(mapping,anchor_length_m=.2,slope_N_per_m=3500.):
 """Optional engineering-slope line anchored to400N at an ASSUMED length.

 The label's measurement position is not supplied, so .2 is an explicit
 approximation convention, not an observed F1 point.3500 is retained only
 for a sensitivity comparison; no measured slope/ratio is inferred.
 """
 require(slope_N_per_m>0 and math.isfinite(slope_N_per_m),'positive stiffness in N/m')
 q=mapping.q_for_length_m(anchor_length_m);target=q+400./slope_N_per_m
 return dict(assumed_400N_anchor_eye_length_m=anchor_length_m,anchor_q_m=q,
  engineering_stiffness_N_per_m=slope_N_per_m,proposed_virtual_target_q_m=target,
  target_eye_length_m=mapping.length_m(target),hardware_calibrated=False,
  nominal_only_not_admitted=True,force_label_measurement_position='NOT_PROVIDED',
  requires_separate_new_source_admission_before_any_runtime_change=True)
