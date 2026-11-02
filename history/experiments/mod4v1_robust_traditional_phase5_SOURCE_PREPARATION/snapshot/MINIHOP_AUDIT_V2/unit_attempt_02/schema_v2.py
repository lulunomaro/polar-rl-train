"""Strict finite private-row schema; no simulation or controller imports."""
import math
import numbers
import numpy as np

SCHEMA='MINIHOP_PRIVATE_GRADE_V2'
PHYSICS_DT_S=.0005
AIR_NORMAL_LIMIT_N=1.
AIR_MINIMUM_S=.02
CLOCK_EPS_S=1e-8

class InstrumentationError(RuntimeError):
    def __init__(self,code,field,observed=None):
        self.code=str(code);self.field=str(field);self.observed_repr=repr(observed)
        super().__init__(self.code+': '+self.field+' = '+self.observed_repr)
    def receipt(self):
        return dict(kind='MINIHOP_V2_INSTRUMENTATION_ERROR',code=self.code,field=self.field,observed_repr=self.observed_repr,invalid_values_not_replaced_by_zero=True)

def finite(value,field):
    if isinstance(value,(bool,np.bool_)) or not isinstance(value,numbers.Real):
        raise InstrumentationError('BAD_SCALAR',field,value)
    v=float(value)
    if not math.isfinite(v):raise InstrumentationError('NONFINITE',field,value)
    return v

def vector(value,shape,field):
    try:
        raw=np.asarray(value)
        if raw.dtype.kind not in ('f','i','u'):raise InstrumentationError('BAD_VECTOR_TYPE',field,str(raw.dtype))
        a=np.asarray(raw,dtype=float)
    except (ValueError,TypeError,OverflowError) as e:raise InstrumentationError('BAD_VECTOR',field,repr(e)) from e
    if a.shape!=shape:raise InstrumentationError('BAD_SHAPE',field,a.shape)
    if not np.isfinite(a).all():raise InstrumentationError('NONFINITE',field,a.tolist())
    return a.copy()

def integer(value,field,minimum=0):
    if isinstance(value,(bool,np.bool_)) or not isinstance(value,numbers.Integral) or int(value)<minimum:
        raise InstrumentationError('BAD_INTEGER',field,value)
    return int(value)

def finite_sum(values,field):
    try:v=math.fsum(values)
    except (OverflowError,ValueError) as e:raise InstrumentationError('AGGREGATE_OVERFLOW',field,repr(e)) from e
    return finite(v,field)

def require(condition,field,value=None):
    if not condition:raise InstrumentationError('BAD_SCHEMA',field,value)

def validate_grade_row(r):
    required={'schema','sample_index','stage_time_s','root_post_time_s','root_xyz_post_m','drivepoint','cache_stages','main_normal_N2','guide_normal_N','hard_normal_N','all_world_normal_N','air_run_s','air_qualified','main_mesh_min_z_world2_m','contacts','environment_contacts','environment_contact_count','environment_nonpositive_contact_count','self_contact_count','world_world_contact_count','private_contact_diagnostic'}
    require(isinstance(r,dict)and set(r)==required,'row.keys',None if not isinstance(r,dict)else sorted(r))
    require(r['schema']==SCHEMA,'schema',r['schema'])
    integer(r['sample_index'],'sample_index');t=finite(r['stage_time_s'],'stage_time_s');post=finite(r['root_post_time_s'],'root_post_time_s')
    require(t>=0 and abs(post-t-PHYSICS_DT_S)<=CLOCK_EPS_S,'stage_interval',(t,post))
    vector(r['root_xyz_post_m'],(3,),'root_xyz_post_m')
    dp=r['drivepoint'];require(set(dp)=={'time_s','physics_tick','velocity6_rad_s','actual_tau6_Nm','root_xyz_pre_m'},'drivepoint.keys')
    require(finite(dp['time_s'],'drivepoint.time')==t,'drivepoint.time')
    integer(dp['physics_tick'],'drivepoint.tick');vector(dp['velocity6_rad_s'],(6,),'drivepoint.velocity6');vector(dp['actual_tau6_Nm'],(6,),'drivepoint.tau6');vector(dp['root_xyz_pre_m'],(3,),'drivepoint.root')
    stages=r['cache_stages'];require(set(stages)=={'force_s','contact_geometry_s','mesh_s','drive_s','root_post_s'},'cache_stages.keys')
    for k in ('force_s','contact_geometry_s','mesh_s','drive_s'):require(finite(stages[k],'cache.'+k)==t,'cache.'+k)
    require(stages['root_post_s']==post,'cache.root_post_s')
    main=vector(r['main_normal_N2'],(2,),'main_normal_N2');vector(r['main_mesh_min_z_world2_m'],(2,),'main_mesh_min_z_world2_m')
    guide=finite(r['guide_normal_N'],'guide_normal_N');hard=finite(r['hard_normal_N'],'hard_normal_N');total=finite(r['all_world_normal_N'],'all_world_normal_N');duration=finite(r['air_run_s'],'air_run_s')
    require(min(*main,guide,hard,total,duration)>=0,'nonnegative_aggregates')
    require(type(r['air_qualified'])is bool and r['air_qualified']==(duration>=AIR_MINIMUM_S),'air_qualified')
    require(total<=AIR_NORMAL_LIMIT_N or duration==0,'air_duration_under_support')
    require(isinstance(r['environment_contacts'],list)and isinstance(r['contacts'],list),'contact_lists')
    normals=[];forces=[];classified=[[],[],[],[]]
    for c in r['environment_contacts']:
        fields={'contact_index','robot_geom_id','robot_geom','robot_body_id','robot_body','environment_geom_id','environment_geom','robot_is_geom2','kind','main_index','normal_signed_N','normal_N','position_world_m','normal_geom1_to_geom2_world','local_force6','force_on_robot_world_N3'}
        require(isinstance(c,dict)and set(c)==fields,'contact.keys')
        for k in ('contact_index','robot_geom_id','robot_body_id','environment_geom_id'):integer(c[k],k)
        require(type(c['robot_is_geom2'])is bool,'robot_is_geom2')
        for k in ('robot_geom','robot_body','environment_geom'):require(c[k]is None or isinstance(c[k],str),k)
        n=finite(c['normal_N'],'contact.normal');signed=finite(c['normal_signed_N'],'contact.normal_signed');require(n==max(0.,signed),'positive_normal')
        force=vector(c['local_force6'],(6,),'local_force6');require(force[0]==signed,'force_normal')
        vector(c['position_world_m'],(3,),'contact.position');vector(c['normal_geom1_to_geom2_world'],(3,),'contact.normal_axis');world=vector(c['force_on_robot_world_N3'],(3,),'force_on_robot_world_N3')
        if c['kind']=='main_wheel':require(c['main_index']in (0,1),'main_index');j=c['main_index']
        elif c['kind']=='guide_roller':require(c['main_index']is None,'guide.main_index');j=2
        else:require(c['kind']=='hard_other'and c['main_index']is None,'contact.kind');j=3
        classified[j].append(n);normals.append(n);forces.append(world)
    require(r['contacts']==[c for c in r['environment_contacts']if c['normal_N']>0.],'full_positive_contacts')
    require(total==finite_sum(normals,'normal_sum'),'all_world_normal_N')
    expected=[finite_sum(v,'class_sum') for v in classified]
    require(expected==[float(main[0]),float(main[1]),guide,hard],'partition_sums')
    for k in ('environment_contact_count','environment_nonpositive_contact_count','self_contact_count','world_world_contact_count'):integer(r[k],k)
    require(r['environment_contact_count']==len(normals),'environment_contact_count')
    require(r['environment_nonpositive_contact_count']==sum(c['normal_N']==0. for c in r['environment_contacts']),'nonpositive_count')
    diag=r['private_contact_diagnostic']
    require(set(diag)=={'visibility','meaning','stage_time_s','contact_external_force_world_N3','actual_model_body_mass_sum_kg','root_rotation_world_from_body33_pre','chassis_subtree_com_world_m3_pre'},'private.keys')
    require(diag['visibility']=='private_physics_only'and diag['meaning']=='contact_only_not_complete_trueCOMproper','private.meaning')
    require(diag['stage_time_s']==t,'private.stage')
    vec=vector(diag['contact_external_force_world_N3'],(3,),'private.external_force')
    require(vec.tolist()==[finite_sum((f[i]for f in forces),'world_force_sum')for i in range(3)],'private.external_force_sum')
    require(finite(diag['actual_model_body_mass_sum_kg'],'private.mass')>0,'private.mass_positive')
    if diag['root_rotation_world_from_body33_pre']is not None:vector(diag['root_rotation_world_from_body33_pre'],(3,3),'private.rotation')
    if diag['chassis_subtree_com_world_m3_pre']is not None:vector(diag['chassis_subtree_com_world_m3_pre'],(3,),'private.subtree_com')
    return r
