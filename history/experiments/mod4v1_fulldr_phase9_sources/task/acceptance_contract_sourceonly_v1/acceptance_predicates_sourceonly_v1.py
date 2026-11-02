"""Stdlibsemantic MOCK of pinnedoriginal predicates; not Torch/SDK/birth evidence.
Reference IDs resolve fullpath/SHA/originalfunction in contractmatrix. No actor,
state setter/RNG/reset/physics APIs, no originalmodel/raw content access.
"""
import math
from fractions import Fraction


def physical_window(seconds,policy_hz=50,feedback_hz=100,physics_hz=400):
    sec=Fraction(str(seconds));counts=[sec*r for r in (policy_hz,physics_hz,feedback_hz)]
    if any(x.denominator!=1 for x in counts):raise ValueError('Windowdoesnotalign withoriginalphysicalclocks')
    return dict(seconds=float(sec),controls=int(counts[0]),physics=int(counts[1]),feedback=int(counts[2]))


def boundary_censor(*,old_boundary_hit,current_integration_hit):
    """Parentexplicit old.002/.05 vscurrent.01/.01, no hotpatch/comparable-rateclaim."""
    if old_boundary_hit:return 'FIRST_ORIGINAL_BOUNDARY_PREFIX_STOP_NOT_STITCHABLE'
    if current_integration_hit:return 'CURRENT_INTEGRATION_CENSORED_NOT_ORIGINAL_SKILL_FAILURE'
    return 'KEEP_ORIGINAL_PREFIX'


def mean_positive_vertical_force(physical_force_N,physics_dt=.0025,control_dt=.02):
    """CURB*_PREDICATE +SLOPE135_PREDICATE: controlimpulse/dt >1N support."""
    if not physical_force_N or len(physical_force_N)!=round(control_dt/physics_dt):raise ValueError('Needallphysicalcallbacks inthiscontrol')
    return sum(max(0.,float(f)) for f in physical_force_N)*physics_dt/control_dt


def route_prefix(rows,group,edge):
    """OriginalCurbedge.275/Slopeedge1.2; no cross-episode stitching.
    rows: episode,u(left/rightcanonicalwheelx),support(left/right),ordinary,
    original_boundary_hit,current_integration_hit,control. Truncation alone
    doesnoteraseprefix; a changedepisode separatessegments.
    """
    if group==2:return dict(crossing_required=False,contact_confirmed=False,prefixes=[],status='STAND_NO_CROSS_REQUIREMENT')
    episodes={};status='OBSERVED_PREFIX';first_failure=None
    for r in rows:
        old=r.get('original_boundary_hit',False) or r.get('ordinary',False)
        state=boundary_censor(old_boundary_hit=old,current_integration_hit=r.get('current_integration_hit',False))
        if state!='KEEP_ORIGINAL_PREFIX':status=state;first_failure=r['control'];break
        e=episodes.setdefault(r['episode'],dict(before=[],after=[],controls=[]));u=r['u'];both=all(r['support']);e['controls'].append(r['control'])
        before=max(u)<-edge if group==0 else min(u)>edge
        after=min(u)>edge if group==0 else max(u)<-edge
        if before and both:e['before'].append(r['control'])
        if after and both:e['after'].append(r['control'])
    prefixes=[]
    for ep,e in episodes.items():prefixes.append(dict(episode=ep,first=min(e['controls']),last=max(e['controls']),contact_confirmed=bool(e['before'] and e['after'] and min(e['before'])<max(e['after']))))
    return dict(crossing_required=True,contact_confirmed=any(p['contact_confirmed'] for p in prefixes),prefixes=prefixes,status=status,first_boundary_control=first_failure)


def e2_signed_cycle(*,seconds,along_distance,cross_distance,turn,commanded_yaw_integral,sign,complete,terminated=False,truncated=False,same_uid_episode_direction_sign=True,contiguous_substeps=True,current_integration_censored=False):
    """E2_CYCLES.E2Cycles213.observe/emit exactoriginal factsemantics.
    No populationpassrate; phasecrossing not a spanbreak, no interpolation.
    """
    if not same_uid_episode_direction_sign or not contiguous_substeps:raise ValueError('Originalspanschema continuitybroken')
    safe=seconds if seconds>0 else 1.;along=along_distance/safe;cross=cross_distance/safe;yaw=(turn-commanded_yaw_integral)/safe
    sampled_complete=bool(complete and turn*sign>=2*math.pi)
    kinematic=abs(along-.5)<=.05 and abs(cross)<=.05 and abs(yaw)<=.2
    valid=seconds>0 and sampled_complete and not terminated and not truncated and not current_integration_censored
    return dict(along_speed=along,cross_speed=cross,yaw_error=yaw,original_kinematic_bounds_met=kinematic,valid_original_complete_skill_sample=valid,original_complete_cycle_fact=bool(valid and kinematic),current_integration_censored=current_integration_censored,aggregate_graduation=None)


class Step270Trace:
    """H1_GOAL.Step270Events.physical at400Hz; semanticfixture only."""
    def __init__(self):
        self.ready_ticks=self.air_ticks=self.land_ticks=self.stable_ticks=0
        self.was_ready=self.attempt=self.positive_vz=self.launched=self.edge=self.landed=self.success=False
    def physical(self,*,request,ground_ready,nonwheel_clean,wheel_N,wheel_bottom_world_z,wheel_contact_platform,wheel_footprints_inside_top,both_wheel_edge_crossed,root_vz,planar_speed,roll,pitch,heading_error):
        self.ready_ticks=self.ready_ticks+1 if ground_ready and not request else 0;ready=self.ready_ticks>=80
        self.attempt|=request and self.was_ready;self.was_ready=self.was_ready if request else ready
        self.positive_vz|=self.attempt and root_vz>.05
        air=self.attempt and self.positive_vz and all(f<=1 for f in wheel_N) and nonwheel_clean
        self.air_ticks=self.air_ticks+1 if air else 0;self.launched|=self.air_ticks>=16
        self.edge|=self.launched and air and both_wheel_edge_crossed and all(z>=.270 for z in wheel_bottom_world_z)
        on_top=all(f>1 for f in wheel_N) and all(wheel_contact_platform) and all(wheel_footprints_inside_top) and all(z>=.269 for z in wheel_bottom_world_z) and nonwheel_clean
        self.land_ticks=self.land_ticks+1 if self.edge and on_top else 0;self.landed|=self.land_ticks>=12
        yaw=math.atan2(math.sin(heading_error),math.cos(heading_error));good=self.landed and on_top and abs(root_vz)<=.03 and planar_speed<=.03 and abs(roll)<.17453292519943295 and abs(pitch)<.17453292519943295 and abs(yaw)<.2
        self.stable_ticks=self.stable_ticks+1 if good else 0;self.success|=self.stable_ticks>=200
        return dict(launched=self.launched,edge=self.edge,landed=self.landed,success=self.success)


class E3CreditTrace:
    """E3_PHASE.RecoveryPhase.update: 100Hzpublicage increment2 at50Hz."""
    def __init__(self,recipe):
        if recipe not in range(13):raise ValueError('Own13recipecohort only')
        self.recipe=recipe;self.age=0;self.stable=0;self.credited=False
    def control(self,gravity_z,root_speed,angular_speed):
        request=self.recipe!=12 and self.age<300;good=gravity_z<-.984807753 and root_speed<.03 and angular_speed<.2 and request
        self.stable=self.stable+2 if good else 0;event=self.stable>=50 and not self.credited;self.credited|=event;self.age+=2
        return dict(request=request,age100Hz=self.age,stable100Hz=self.stable,credited=self.credited,event=event)


def no_saved_aggregate_rule():
    return dict(skill_status='PENDING_ORIGINAL_ACCEPTANCE_NOT_GRADUATED',aggregate_graduation=None,reason='No originalnumericalglobalrule saved; diagnosticMAE/frozenformat are notskillpass')
