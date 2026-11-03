"""Strict 4-raw one-pass work integration. Standard library only; no model/QA."""
from pathlib import Path
import json,math,struct,collections,hashlib,traceback,shutil
O=Path(__file__).resolve().parent;ROOT=O.parent
M=json.loads((O/'METHOD.json').read_bytes());S=json.loads((O/'SOURCE_LOCK.json').read_bytes());A=O/'extract_attempt_001';A.mkdir()
for n in('METHOD.json','SOURCE_LOCK.json','extract_once.py'):shutil.copyfile(O/n,A/n)
allowed=set(M['allowed_raw_paths']);opens={n:0 for n in allowed};readrows=0;caseout=[];compact={};error=None;current=None
DT=.0005;TOL=1e-8;LEGS=(0,1,3,4);WHEELS=(2,5)
SHAPES={'time_s':None,'command_time_s':None,'forward_command_m_s':None,'sensor_time_s':None,'sensor_age_s':None,'estimated14':14,'estimated_roll':None,'raw_gyro':3,'raw_proper':3,'encoder_q4':4,'encoder_qd4':4,'wheel_rate_mean2':2,'requested_tau6':6}

def num(x,label):
 if isinstance(x,bool)or not isinstance(x,(int,float))or not math.isfinite(x):raise ValueError('UNKNOWN_NONFINITE_OR_NONNUMERIC '+label)
 return float(x)
def vec(x,n,label):
 if not isinstance(x,list)or len(x)!=n:raise ValueError('UNKNOWN_BAD_SHAPE '+label)
 return[num(v,label)for v in x]
def near(x,y,label):
 e=abs(num(x,label)-num(y,label))
 if e>TOL:raise ValueError('UNKNOWN_STAGE_MISMATCH '+label+' '+repr((x,y)))
 return e
def raw(s):
 global readrows
 rel=s['relative'];p=(ROOT/rel).resolve()
 assert rel in allowed and str(p)==s['path']and opens[rel]==0
 opens[rel]+=1;st=p.stat();assert st.st_size==s['bytes']and st.st_mtime_ns==s['mtime_ns']
 with p.open('rb')as f:
  for i in range(s['expected_rows']):
   if readrows>=33600:raise ValueError('ROW_BUDGET')
   line=f.readline()
   if not line:raise ValueError('UNKNOWN_TRUNCATED_STREAM '+rel)
   readrows+=1;yield i,json.loads(line)
  # EOF proof by byte position: no extra line/row read and no raw hash.
  if f.tell()!=s['bytes']:raise ValueError('UNREAD_EXTRA_BYTES_OR_ROWS '+rel)
 st=p.stat();assert st.st_size==s['bytes']and st.st_mtime_ns==s['mtime_ns']
class Sum:
 def __init__(self):self.s=0.;self.c=0.
 def add(self,x):
  t=self.s+x
  self.c+=(self.s-t)+x if abs(self.s)>=abs(x)else(x-t)+self.s
  self.s=t
 def value(self):return self.s+self.c
class Work:
 def __init__(self):self.pos=[Sum()for _ in range(6)];self.neg=[Sum()for _ in range(6)];self.n=0;self.first=None;self.last=None;self.peak_positive_W=0.
 def add(self,p,t,post):
  self.n+=1;self.first=t if self.first is None else self.first;self.last=post
  self.peak_positive_W=max(self.peak_positive_W,math.fsum(max(v,0.)for v in p))
  for i,v in enumerate(p):self.pos[i].add(max(v,0.)*DT);self.neg[i].add(min(v,0.)*DT)
 def result(self):
  if not self.n:return None
  pos=[s.value()for s in self.pos];neg=[s.value()for s in self.neg];net=[p+n for p,n in zip(pos,neg)];duration=self.n*DT
  groups={}
  for name,ix in(('legs4',LEGS),('wheels2',WHEELS)):
   pp=math.fsum(pos[i]for i in ix);nn=math.fsum(neg[i]for i in ix);nw=pp+nn
   groups[name]=dict(net_work_J=nw,positive_work_J=pp,negative_work_J=nn,net_mean_power_W=nw/duration)
  return dict(samples=self.n,duration_s=duration,first_PRE_s=self.first,last_POST_s=self.last,axis_positive_work_J=pos,axis_negative_work_J=neg,axis_net_work_J=net,groups=groups,peak_positive_mechanical_power_W=self.peak_positive_W)
try:
 for src in S['cases']:
  current=dict(case=src['case'],complete=False,reported=src['reported']);caseout.append(current);ctrl=[];transitions=[];pc=collections.Counter();clockmax=0.;work={}
  for i,r in raw(src['streams'][0]):
   phase=r['phase']['phase']
   if not isinstance(phase,str):raise ValueError('UNKNOWN_PHASE_SCHEMA')
   pub={k:([num(r[k],k)]if n is None else vec(r[k],n,k))for k,n in SHAPES.items()}
   cmd=pub['command_time_s'][0];post=pub['time_s'][0];clockmax=max(clockmax,near(cmd,i*.01,'control command index'),near(post,cmd+.01,'control post'))
   if r['physical_sample_rows']!=(i+1)*20:raise ValueError('UNKNOWN_20_TO_1_CONTROL_COUNT')
   if not ctrl or phase!=ctrl[-1]['phase']:transitions.append(dict(phase=phase,control_index=i,command_time_s=cmd,first_control_root_POST_s=post))
   ctrl.append(dict(phase=phase,cmd=cmd,post=post,public=pub));pc[phase]+=1
  if len(ctrl)!=800:raise ValueError('control rows')
  pushes=[i for i,c in enumerate(ctrl)if c['phase']=='timed_push'];firstpush=pushes[0]if pushes else None
  current.update(control_phase_counts=dict(pc),phase_transitions=transitions,first_push_control_index=firstpush,first_push_command_s=None if firstpush is None else ctrl[firstpush]['cmd'])
  compact[src['case']]=ctrl;work={'whole_episode':Work()};qual=None;landing=None;peak=None;lastmeta=None;physical_counts=collections.Counter()
  current['physical_known_prefix_rows']=0
  for i,r in raw(src['streams'][1]):
   if r['schema']!='MINIHOP_PRIVATE_GRADE_V2'or r['sample_index']!=i:raise ValueError('UNKNOWN_PRIVATE_SCHEMA_INDEX')
   dp=r['drivepoint'];stage=num(r['stage_time_s'],'stage');post=num(r['root_post_time_s'],'post')
   if dp['physics_tick']!=i:raise ValueError('UNKNOWN_DRIVE_TICK')
   c=ctrl[i//20];clockmax=max(clockmax,near(dp['time_s'],stage,'drive PRE'),near(stage,i*DT,'physical index'),near(stage,c['cmd']+(i%20)*DT,'control sample'),near(post,stage+DT,'PRE POST interval'),near(r['cache_stages']['drive_s'],stage,'drive stage label'))
   if i%20==19:clockmax=max(clockmax,near(post,c['post'],'20th physics POST/control POST'))
   velocity=vec(dp['velocity6_rad_s'],6,'actual PRE dq');tau=vec(dp['actual_tau6_Nm'],6,'actual PRE tau');power=[num(a*b,'product power')for a,b in zip(tau,velocity)]
   phase=c['phase']
   if phase not in work:work[phase]=Work()
   work[phase].add(power,stage,post);work['whole_episode'].add(power,stage,post);physical_counts[phase]+=1
   qualified=r['air_qualified'];run=num(r['air_run_s'],'air run');total=num(r['all_world_normal_N'],'total normal')
   if type(qualified)is not bool:raise ValueError('UNKNOWN_AIR_FLAG')
   if qual is None and qualified:qual=dict(interval_start_PRE_s=post-run,confirmation_PRE_s=stage,confirmation_POST_s=post,sample_index=i,control_phase=phase)
   if qual is not None and landing is None and total>1.:
    contacts=r['contacts'];landing=dict(stage_PRE_s=stage,root_POST_s=post,sample_index=i,control_phase=phase,all_world_normal_N=total,contacts=[dict(robot_geom=x['robot_geom'],environment_geom=x['environment_geom'],normal_N=num(x['normal_N'],'contact normal'))for x in contacts])
   z=vec(r['main_mesh_min_z_world2_m'],2,'main mesh minZ')
   if qualified and(peak is None or min(z)>peak['clearance_m']):peak=dict(clearance_m=min(z),cache_PRE_s=stage,root_POST_s=post,control_phase=phase)
   current['physical_known_prefix_rows']=i+1;lastmeta=dict(last_sample_index=i,last_PRE_s=stage,last_POST_s=post,last_control_phase=phase)
  current.update(complete=True,work={k:w.result()for k,w in work.items()},physics_phase_counts=dict(physical_counts),clock_max_abs_error_s=clockmax,observed_first_qualified_air=qual,observed_first_landing=landing,observed_all_qualified_air_main_mesh_peak=peak,last_cell=lastmeta)
  if any(physical_counts[k]!=n*20 for k,n in pc.items()):raise ValueError('UNKNOWN_PHASE_SAMPLE_PARTITION')
  current['reported_peak_power_minus_observed_W']=src['reported']['reported_peak_positive_mechanical_power_W']-current['work']['whole_episode']['peak_positive_mechanical_power_W']
 # Bounded paired100Hz public prefix; no physical-row pairwise identity claim.
 old,new=[compact[c['case']]for c in S['cases']];cuts=[c['first_push_control_index']for c in caseout];cut=None if None in cuts else min(cuts)
 prefix=dict(rows=cut,domain='13 shared100Hz public sensor/estimate/request fields, before either actual first timed_push; not2k identity',fields={},phase_mismatches=0)
 if cut is None:prefix.update(status='UNKNOWN_NO_OBSERVED_PUSH')
 else:
  for k in SHAPES:prefix['fields'][k]=dict(scalar_values=0,max_abs_difference=0.,binary64_value_mismatches=0,first_difference_control_index=None)
  for i in range(cut):
   if old[i]['phase']!=new[i]['phase']:prefix['phase_mismatches']+=1
   for key in SHAPES:
    d=prefix['fields'][key]
    for a,b in zip(old[i]['public'][key],new[i]['public'][key]):
     d['scalar_values']+=1;d['max_abs_difference']=max(d['max_abs_difference'],abs(a-b))
     if struct.pack('<d',a)!=struct.pack('<d',b):d['binary64_value_mismatches']+=1;d['first_difference_control_index']=i if d['first_difference_control_index']is None else d['first_difference_control_index']
  prefix.update(status='OBSERVED_ONLY_NOT_A_QUALIFICATION_GATE',last_prefix_command_s=None if cut==0 else old[cut-1]['cmd'],scalar_values=sum(x['scalar_values']for x in prefix['fields'].values()),max_abs_difference=max(x['max_abs_difference']for x in prefix['fields'].values()),binary64_value_mismatches=sum(x['binary64_value_mismatches']for x in prefix['fields'].values()))
 assert readrows==33600 and all(n==1 for n in opens.values())
 status='PASS_SINGLE_RAW_PASS_STAGE_CHECKED_MECHANICAL_WORK_ANALYSIS_ONLY'
except Exception:
 status='PARTIAL_UNKNOWN_INSTRUMENTATION_PREFIX_NOT_FULL_WORK';error=traceback.format_exc();prefix=None
 if current is not None:
  current['complete']=False
  current['partial_known_prefix_work_only']={k:w.result()for k,w in work.items()}if work else None
out=dict(status=status,error=error,raw_opens=opens,rows_read=readrows,cases=caseout,prepush_public_prefix=prefix,integral_units='work J; average/instantaneous power W',negative_work_sign='negative value, per-axis split before grouping',method_SHA=hashlib.sha256((O/'METHOD.json').read_bytes()).hexdigest(),source_SHA=hashlib.sha256((O/'SOURCE_LOCK.json').read_bytes()).hexdigest(),raw_SHA_recomputed=False,raw_archived=False,model_driver_FK_PHY_QA_executed=False,old_scores_modified=False)
with(O/'SUMMARY.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(out,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(json.dumps(dict(status=status,error=error,rows_read=readrows,raw_opens=opens,prepush=prefix,cases=[dict(case=c['case'],complete=c['complete'],phase_counts=c.get('control_phase_counts'),work=c.get('work'),air=c.get('observed_first_qualified_air'),landing=c.get('observed_first_landing'),peak=c.get('observed_all_qualified_air_main_mesh_peak'))for c in caseout]),indent=2))
if error:raise SystemExit(1)
