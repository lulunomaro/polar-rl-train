"""NEW synthetic signal/time-contract checks; no robot/old QA/force replay."""
from pathlib import Path
from dataclasses import asdict,replace
import json,math,sys,time
from signal_alignment_v1 import ChannelSpec,ChannelSample,SignalAligner
R=Path(__file__).resolve().parent;D=R/'SENSOR_ALIGNMENT_V1/check001'
D.mkdir(parents=True,exist_ok=False)
PROTOCOL=dict(id='MOD4V2_BOUNDED_PUBLIC_SIGNAL_ALIGNMENT_001',
 purpose='actual weighted resampling, explicit sampled-window bias bounds, no packet-epoch relabeling',
 linear_absolute_tolerance=1e-11,bound_comparison_tolerance=1e-11,
 capacity=8,max_age_s=.03,max_bracket_gap_s=.02,
 source_offset_example_s=dict(encoder_q4=0.,encoder_qd4=-.00525,gyro_B=-.00525,proper_imu_B=-.00525,motor_tau6=-.0005),
 declarations='Noise/rate/curvature/clock bounds below are known NEW synthetic assumptions, not hardware calibration or DR estimates.',
 old_case_or_raw_reads=0,robot_models=0,forwards=0,physics_steps=0,force_model_calls=0)
(D/'protocol.json').write_text(json.dumps(PROTOCOL,indent=2),encoding='utf-8')
N=0;profiles=[]
def check(v,msg):
 global N
 N+=1
 if not v:raise AssertionError(msg)
DIMS=dict(encoder_q4=4,encoder_qd4=4,gyro_B=3,proper_imu_B=3,motor_tau6=6)

def functions(quadratic=False):
 acc=(.4,-.2,.3,-.1) if quadratic else (0.,)*4
 return dict(
  encoder_q4=lambda t:tuple(.2+.01*k+.2*t+.5*acc[k]*t*t for k in range(4)),
  encoder_qd4=lambda t:tuple(.2+acc[k]*t for k in range(4)),
  gyro_B=lambda t:tuple(.03*(k+1)+.01*t+(.1*t*t if quadratic else 0.) for k in range(3)),
  proper_imu_B=lambda t:(.1*t,.2*t,9.81+.05*t),
  motor_tau6=lambda t:tuple(.1*(k+1)+.05*t for k in range(6)))

def specs(quadratic=False,bounds=True):
 out=[]
 for name,n in DIMS.items():
  curve=tuple(abs(x) for x in (.4,-.2,.3,-.1)) if quadratic and name=='encoder_q4' else ((.2,)*n if quadratic and name=='gyro_B' else (0.,)*n)
  out.append(ChannelSpec(name,n,(10.,)*n if bounds else None,curve if bounds else None))
 return out

def sample(name,end,fns,unknown=False):
 point=name in ('encoder_q4','motor_tau6')
 if point:
  t=end if name=='encoder_q4' else end-.0005
  ts=(t,)
 else:ts=tuple(end-.01+i*.0005 for i in range(20));t=math.fsum(ts)/len(ts)
 values=tuple(math.fsum(fns[name](u)[k] for u in ts)/len(ts) for k in range(DIMS[name]))
 moment=math.fsum((u-t)**2 for u in ts)/len(ts)
 return ChannelSample(t,values,min(ts),max(ts),len(ts),'point'if point else'sampled_mean',
  'NEW exact synthetic observation window, not a measured robot',None if unknown else 0.,None if unknown else (0.,)*DIMS[name],moment)

def fill(a,fns,ends=(.10,.11),unknown=False):
 for end in ends:
  for name in DIMS:check(a.push(name,sample(name,end,fns,unknown))=='APPENDED','fresh synthetic append')


def run():
 start=time.perf_counter();linear=functions();a=SignalAligner(specs());fill(a,linear)
 result=a.query(.11);check(result.status=='ALIGNED_OBSERVATIONS_ONLY','linear common frame')
 f=result.frame;target=f.evaluation_epoch_s;linear_max=0.
 for name,c in f.channels.items():
  exact=linear[name](target)
  err=max(abs(x-y)for x,y in zip(c.values,exact));linear_max=max(linear_max,err)
  check(err<=PROTOCOL['linear_absolute_tolerance'],'linear exact interpolation')
  check(abs(sum(c.weights)-1.)<1e-14 and min(c.weights)>=0.,'convex weights')
  check(c.error_bound_abs is not None,'declared synthetic bound available')
 check(f.numeric_bounds_complete,'conditional bounds complete')
 check(f.force_input_ready is False and f.alpha_B_rad_s2 is None and f.hardware_sync_proven is False,'no invented force/alpha/sync')
 check(abs(target-(.11-.00525))<1e-14,'real common mean time, not endpoint')
 check(len(f.channels['encoder_q4'].source_epochs_s)==2,'q actually interpolated from two endpoint values')
 check(len(f.channels['gyro_B'].source_windows_s[0])==4,'original windows retained')
 profiles.append(dict(name='affine_public_signals',max_absolute_difference=linear_max,target_s=target,frame=asdict(f)))
 for name in DIMS:check(a.push(name,sample(name,.11,linear))=='HELD_IDENTICAL','held packet is not fresh')
 check(a.query(.111).status=='NO_NEW_COMMON_TIME','duplicate view does not create derivative sample')

 qfn=functions(True);a=SignalAligner(specs(True));fill(a,qfn);res=a.query(.11)
 check(res.status=='ALIGNED_OBSERVATIONS_ONLY','quadratic bounded frame')
 worst_ratio=0.;nonzero_window_bias=0.
 for name,c in res.frame.channels.items():
  exact=qfn[name](res.frame.evaluation_epoch_s)
  for measured,true,bound in zip(c.values,exact,c.error_bound_abs):
   err=abs(measured-true)
   check(err<=bound+PROTOCOL['bound_comparison_tolerance'],'quadratic interpolation plus mean-window bias bound')
   if bound>1e-12:worst_ratio=max(worst_ratio,err/bound)
   if name=='gyro_B':nonzero_window_bias=max(nonzero_window_bias,err)
 check(nonzero_window_bias>1e-7,'sampled mean curvature bias was not erased by timestamp changes')
 profiles.append(dict(name='constant_joint_acceleration_and_curved_gyro_window',worst_error_to_declared_bound=worst_ratio,gyro_window_bias=nonzero_window_bias))

 # Shared D3 delay changes arrival age, not any observed source value or epoch.
 a=SignalAligner(specs());fill(a,linear);r=a.query(.12)
 check(r.status=='ALIGNED_OBSERVATIONS_ONLY','10ms common arrival delay')
 check(abs(r.frame.arrival_age_s-.01525)<1e-14,'arrival delay retained')
 for name in DIMS:check(r.frame.channels[name].values==f.channels[name].values,'D3 is not canceled or values changed')
 profiles.append(dict(name='public_10ms_arrival_delay_retained',age_s=r.frame.arrival_age_s))

 a=SignalAligner(specs(bounds=False));fill(a,linear,unknown=True);r=a.query(.11)
 check(r.status=='ALIGNED_OBSERVATIONS_ONLY','unknown error bounds do not manufacture numeric ones')
 check(not r.frame.numeric_bounds_complete and not r.frame.force_input_ready,'unknown quality stays non-authoritative')
 for c in r.frame.channels.values():check(c.error_bound_abs is None and bool(c.bound_reasons),'unknown bounds None with reasons')
 a=SignalAligner(specs());fill(a,linear);check(a.push('gyro_B',None)=='UNKNOWN_TIME_METADATA','missing timestamp explicit')
 check(a.query(.11).status=='MISSING_TIME_METADATA_OR_HISTORY','do not copy packet epoch into missing channel')
 profiles.append(dict(name='missing_metadata_and_unknown_bounds',force_authority=False))

 # Changed duplicate and rollback latch; only explicit reset discards history.
 a=SignalAligner(specs());s=sample('encoder_q4',.10,linear)
 check(a.push('encoder_q4',s)=='APPENDED','fault prefix append')
 check(a.push('encoder_q4',replace(s,values=(9.,)*4)).startswith('CHANGED_DUPLICATE'),'changed same-epoch payload')
 check(a.query(.11).status=='LATCHED','duplicate latch')
 before=len(a.history['encoder_q4']);check(a.push('encoder_q4',sample('encoder_q4',.11,linear)).startswith('LATCHED'),'latched pushes stopped')
 check(len(a.history['encoder_q4'])==before,'history untouched after latch')
 a.reset();check(a.push('encoder_q4',s)=='APPENDED','explicit reset')
 check(a.push('encoder_q4',sample('encoder_q4',.09,linear)).startswith('CHANNEL_TIME_ROLLBACK'),'rollback latch')
 profiles.append(dict(name='conflicting_duplicate_rollback_latches',external_motion_or_disable_claim=False))

 a=SignalAligner(specs());fill(a,linear)
 check(a.query(.10).status=='FUTURE_SOURCE_SAMPLE','future observations not consumed')
 check(a.query(.151).status=='STALE_OR_FUTURE_COMMON_TIME','old common time not fresh')
 a=SignalAligner([ChannelSpec('x',1,(1.,),(0.,)),ChannelSpec('y',1,(1.,),(0.,))])
 def point(t):return ChannelSample(t,(t,),t,t,1,'point','new gap fixture',0.,(0.,),0.)
 a.push('x',point(.10));a.push('x',point(.14));a.push('y',point(.12))
 check(a.query(.14).status=='BRACKET_GAP_TOO_LARGE','bounded interpolation gap')
 a=SignalAligner(specs());fill(a,linear,ends=(.10,))
 check(a.query(.10).status=='NO_BRACKET_NO_EXTRAPOLATION','startup missing history does not extrapolate q backwards')
 profiles.append(dict(name='future_stale_large_gap_and_startup',extrapolation=False))

 a=SignalAligner(specs());fill(a,linear,ends=tuple(.10+.01*k for k in range(14)))
 check(all(len(h)==8 for h in a.history.values()),'bounded capacity')
 check(a.query(.23).status=='ALIGNED_OBSERVATIONS_ONLY','latest bracket retained in bounded history')
 # New malformed inputs, not old observer/robot QA.
 for bad in [replace(s,values=(math.nan,)*4),replace(s,window_start_s=.2),replace(s,sample_count=0),replace(s,noise_bound_abs=(-1.,)*4)]:
  a=SignalAligner(specs());check(a.push('encoder_q4',bad).startswith('INVALID_SAMPLE'),'invalid sample latched')
  check(a.query(.11).status=='LATCHED','invalid sample no frame')
 for kwargs in [dict(capacity=1),dict(max_age_s=-.1),dict(max_bracket_gap_s=.04)]:
  try:SignalAligner(specs(),**kwargs)
  except ValueError:check(True,'configuration guard')
  else:check(False,'invalid configuration accepted')
 profiles.append(dict(name='capacity_and_new_input_guards',capacity=8))
 return dict(status='NEW_SYNTHETIC_ALIGNMENT_CONTRACT_PASS_NOT_SENSOR_CALIBRATION',passed=True,
  assertions=N,profiles=profiles,linear_max_absolute_difference=linear_max,
  real_models=0,real_forwards=0,real_FK_calls=0,real_physics_steps=0,old_case_or_raw_reads=0,
  force_model_calls=0,controller_connections=0,hardware_transmissions=0,
  imports_mujoco='mujoco'in sys.modules,imports_numpy='numpy'in sys.modules,
  alpha_or_calibration_manufactured=False,default_proxy_skew_or_cap_changed=False,
  wall_s=time.perf_counter()-start)

try:out=run()
except BaseException as exc:
 (D/'result.json').write_text(json.dumps(dict(passed=False,assertions_before_failure=N,error=repr(exc),profiles_completed=profiles),indent=2),encoding='utf-8')
 raise
else:
 (D/'result.json').write_text(json.dumps(out,indent=2,allow_nan=False),encoding='utf-8')
 print(json.dumps({k:v for k,v in out.items()if k!='profiles'},indent=2),flush=True)
