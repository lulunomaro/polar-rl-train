"""Purestdlib fixture tests, NEVER actualskill/SDK/Torch results."""
from pathlib import Path
import ast,hashlib,json,math,traceback,time
from acceptance_predicates_sourceonly_v1 import *
B=Path(__file__).resolve().parent
checks=[]
def C(name,value):
 assert value,name;checks.append(name)
try:
 C('15physicalseconds policy50 not1500controls',physical_window(15)==dict(seconds=15.,controls=750,physics=6000,feedback=1500))
 C('20seconds E0',physical_window(20)['controls']==1000)
 C('24seconds E2',physical_window(24)['physics']==9600)
 C('native24only.48s',physical_window(.48)==dict(seconds=.48,controls=24,physics=192,feedback=48))
 C('Original1N support_new8substeps',abs(mean_positive_vertical_force([2.]*8)-2)<1e-12)
 C('No currentmimic censor misclassified oldfail',boundary_censor(old_boundary_hit=False,current_integration_hit=True)=='CURRENT_INTEGRATION_CENSORED_NOT_ORIGINAL_SKILL_FAILURE')
 C('Oldboundarylogicalcut first notstitch',boundary_censor(old_boundary_hit=True,current_integration_hit=False)=='FIRST_ORIGINAL_BOUNDARY_PREFIX_STOP_NOT_STITCHABLE')
 def row(c,u,ep=0,**kw):return dict(control=c,u=u,support=[True,True],episode=ep,**kw)
 C('Curb sameepisode beforeafter',route_prefix([row(0,[-.4,-.4]),row(1,[.4,.4])],0,.275)['contact_confirmed'])
 C('Curb standing noforcedcross',not route_prefix([row(0,[0,0])],2,.275)['crossing_required'])
 C('Curb resetcannotstitch',not route_prefix([row(0,[-.4,-.4]),row(1,[.4,.4],ep=1)],0,.275)['contact_confirmed'])
 C('Curb oldordinaryprefixcuts',not route_prefix([row(0,[-.4,-.4]),row(1,[.4,.4],original_boundary_hit=True)],0,.275)['contact_confirmed'])
 C('Slope completefullramp+bothsupports',route_prefix([row(0,[-1.3,-1.3]),row(1,[1.3,1.3])],0,1.2)['contact_confirmed'])
 C('Slope partialrampnotfull2m',not route_prefix([row(0,[-.9,-.9]),row(1,[.9,.9])],0,1.2)['contact_confirmed'])
 C('Downmirrored endpointorder',route_prefix([row(0,[1.3,1.3]),row(1,[-1.3,-1.3])],1,1.2)['contact_confirmed'])
 args=dict(seconds=2.,along_distance=1.,cross_distance=0.,turn=2*math.pi,commanded_yaw_integral=2*math.pi,sign=1,complete=True)
 C('E2originalsignedcyclefact',e2_signed_cycle(**args)['original_complete_cycle_fact'])
 C('E2timeoutatcompletefalse',not e2_signed_cycle(**dict(args,truncated=True))['original_complete_cycle_fact'])
 C('E2termatcompletefalse',not e2_signed_cycle(**dict(args,terminated=True))['original_complete_cycle_fact'])
 C('E2alongbadnotnewpopulationrule',not e2_signed_cycle(**dict(args,along_distance=1.2))['original_complete_cycle_fact'])
 C('E2currentcensorincomplete',not e2_signed_cycle(**dict(args,current_integration_censored=True))['valid_original_complete_skill_sample'])
 C('E2partialsignedspaninvalid',not e2_signed_cycle(**dict(args,complete=False))['valid_original_complete_skill_sample'])
 def hrow(**kw):
  v=dict(request=False,ground_ready=True,nonwheel_clean=True,wheel_N=[2,2],wheel_bottom_world_z=[0,0],wheel_contact_platform=[False,False],wheel_footprints_inside_top=[False,False],both_wheel_edge_crossed=False,root_vz=0.,planar_speed=0.,roll=0.,pitch=0.,heading_error=0.);v.update(kw);return v
 h=Step270Trace()
 for _ in range(80):h.physical(**hrow())
 for _ in range(16):h.physical(**hrow(request=True,ground_ready=False,wheel_N=[0,0],wheel_bottom_world_z=[.28,.28],root_vz=.1,both_wheel_edge_crossed=True))
 C('H1actualair16callbacks andedge270',h.launched and h.edge)
 for _ in range(12):h.physical(**hrow(request=True,wheel_bottom_world_z=[.27,.27],wheel_contact_platform=[True,True],wheel_footprints_inside_top=[True,True]))
 C('H1platformlanding12callbacks',h.landed)
 for _ in range(199):h.physical(**hrow(request=True,wheel_bottom_world_z=[.27,.27],wheel_contact_platform=[True,True],wheel_footprints_inside_top=[True,True]))
 C('H1fullrecovery200physicalcallbacks',h.success)
 bad=Step270Trace()
 for _ in range(80):bad.physical(**hrow())
 for _ in range(16):bad.physical(**hrow(request=True,ground_ready=False,wheel_N=[0,0],wheel_bottom_world_z=[.26,.26],root_vz=.1,both_wheel_edge_crossed=True))
 C('H1centerheightorbelowplatformnotedgeproof',not bad.edge)
 e=E3CreditTrace(0)
 for _ in range(24):z=e.control(-1,0,0)
 C('E3not.25snot24controls',not z['credited'] and z['stable100Hz']==48)
 z=e.control(-1,0,0);C('E3stable50age=.5s25controls',z['credited'] and z['stable100Hz']==50)
 for _ in range(125):e.control(-1,0,0)
 C('E3publicage300means3seconds',e.age==300 and not e.control(-1,0,0)['request'])
 C('E3normalrecipe12neverrescue',not E3CreditTrace(12).control(-1,0,0)['request'])
 C('Missingglobalrule remainsNone',no_saved_aggregate_rule()['aggregate_graduation'] is None)
 p=B/'acceptance_predicates_sourceonly_v1.py';ast.parse(p.read_bytes())
 with (B/'ACCEPTANCE_PREDICATE_SEMANTIC_MOCK_PROOF_V1.json').open('x',encoding='utf-8') as f:json.dump(dict(kind='STDLIB_SEMANTIC_MOCK_ONLY_NOT_REAL_TORCH_OR_SKILL',passed=True,checks=checks,check_count=len(checks),pure_module_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),float_semantics='Pythonfloat fixture notnewF32runtimeorbitwisefloatgate',original_metric_thresholds_retained=True,no_new_aggregatepassrate_or_MCI=True,PT_SSH_SDK_GPU_operations=0),f,indent=2)
 print(json.dumps(dict(MOCK_ONLY=True,passed=True,checks=len(checks),PT_SDK_operations=0),indent=2))
except BaseException:
 with (B/('PREDICATE_MOCK_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:json.dump(dict(error=traceback.format_exc(),PT_SDK_operations=0),f,indent=2)
 raise
