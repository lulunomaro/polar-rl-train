"""DATA ONLY: parse existing four R04 traces, FK math and quadrature.
No parent/plant module imports, MuJoCo, physics steps, control replay or fitting.
Writes only this new directory; raw sources remain referenced and hashed.
"""
from pathlib import Path
import bisect,csv,hashlib,json,math,statistics,traceback
HERE=Path(__file__).resolve().parent
WORK=HERE.parents[1]
SEEDS=[202,203,205,208]
SKELETON=WORK.parent/'traditional_control_20261101/reports/model_manifest.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def add(a,b):return [x+y for x,y in zip(a,b)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
def wrap(x):return math.atan2(math.sin(x),math.cos(x))
def rotate(v,q):
 c,s=math.cos(q),math.sin(q);return [c*v[0]+s*v[1],-s*v[0]+c*v[1]]
def angle(v,w):return wrap(-(math.atan2(w[1],w[0])-math.atan2(v[1],v[0])))
def intersection(a,ra,b,rb,sgn):
 d=sub(b,a);n=math.hypot(*d)
 if not abs(ra-rb)+1e-7<n<ra+rb-1e-7:raise ValueError('Recorded encoder FK unreachable/singular')
 t=(ra*ra-rb*rb+n*n)/(2*n);h=math.sqrt(max(0,ra*ra-t*t));u=[d[0]/n,d[1]/n]
 return [a[0]+t*u[0]-sgn*h*u[1],a[1]+t*u[1]+sgn*h*u[0]]
def pose(p,h,c,side):
 L=lambda a,b:math.hypot(*sub(p[a],p[b]));q={k:rotate(v,h) for k,v in p.items()};q['A']=rotate(p['A'],c)
 q['B']=intersection(q['A'],L('A','B'),q['P'],L('B','P'),math.copysign(1,cross2(sub(p['P'],p['A']),sub(p['B'],p['A']))))
 rocker=angle(sub(p['B'],p['P']),sub(q['B'],q['P']));q['C']=add(q['P'],rotate(sub(p['C'],p['P']),rocker))
 q['D']=intersection(q['K'],L('K','D'),q['C'],L('C','D'),math.copysign(1,cross2(sub(p['C'],p['K']),sub(p['D'],p['K']))))
 shin=angle(sub(p['D'],p['K']),sub(q['D'],q['K']));w=add(q['K'],rotate(sub(p['W'],p['K']),shin))
 return [w[0],.4376/2 if side==0 else -.4376/2,w[1]],wrap(shin-h)
def wheel_forward(p,q,dq,spin,omega,side,radius):
 r,k=pose(p,*q,side);cols=[];eps=1e-5
 for j in range(2):
  qp=q[:];qm=q[:];qp[j]+=eps;qm[j]-=eps;rp,kp=pose(p,*qp,side);rm,km=pose(p,*qm,side)
  cols.append([(rp[i]-rm[i])/(2*eps) for i in range(3)]+[wrap(kp-km)/(2*eps)])
 relx=sum(cols[j][0]*dq[j] for j in range(2));kd=sum(cols[j][3]*dq[j] for j in range(2))
 return radius*(omega[1]+dq[0]+kd+spin)-relx-(omega[1]*r[2]-omega[2]*r[1]),r

def R(r,p,y):
 cr,sr=math.cos(r),math.sin(r);cp,sp=math.cos(p),math.sin(p);cy,sy=math.cos(y),math.sin(y)
 return [[cy*cp,cy*sp*sr-sy*cr,cy*sp*cr+sy*sr],[sy*cp,sy*sp*sr+cy*cr,sy*sp*cr-cy*sr],[-sp,cp*sr,cp*cr]]
def matvec(a,b):return [sum(x*y for x,y in zip(row,b)) for row in a]
def xyvel(yaw,vx,vy):return [math.cos(yaw)*vx-math.sin(yaw)*vy,math.sin(yaw)*vx+math.cos(yaw)*vy]
def integrate_trapezoid(times,values):
 out=[[0.,0.]]
 for i in range(1,len(times)):
  dt=times[i]-times[i-1];out.append([out[-1][j]+.5*dt*(values[i-1][j]+values[i][j]) for j in range(2)])
 return out
def error_path(est,truth):
 errs=[math.hypot(*(sub(a,b))) for a,b in zip(est,truth)]
 return {'endpoint_m':errs[-1],'trajectory_RMSE_m':math.sqrt(statistics.mean(x*x for x in errs)),'max_m':max(errs)}
def normxy(a):return math.hypot(a[0],a[1])
def quantile(x,p):
 s=sorted(x);q=p*(len(s)-1);i=int(q);return s[i]+(s[min(i+1,len(s)-1)]-s[i])*(q-i)
def compare(a,b):
 d=[x-y for x,y in zip(a,b)];ma=statistics.mean(a);mb=statistics.mean(b)
 va=sum((x-ma)**2 for x in a);vb=sum((x-mb)**2 for x in b)
 return {'count':len(a),'bias_m_s':statistics.mean(d),'RMSE_m_s':math.sqrt(statistics.mean(x*x for x in d)),
         'MAE_m_s':statistics.mean(abs(x) for x in d),'p95_abs_m_s':quantile([abs(x) for x in d],.95),
         'correlation':sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(va*vb) if va*vb>1e-24 else None,
         'true_RMS_m_s':math.sqrt(statistics.mean(x*x for x in b)),'pseudo_RMS_m_s':math.sqrt(statistics.mean(x*x for x in a))}
def nearest_truth(times,gt,t):
 j=bisect.bisect_left(times,t);candidates=[i for i in [j-1,j] if 0<=i<len(times)];i=min(candidates,key=lambda i:abs(times[i]-t))
 if abs(times[i]-t)>1e-7:raise ValueError(f'No exact recorded truth timestamp for packet {t}')
 return gt[i],i

def analyze(seed,pins):
 folder=WORK/'results'/f'r04_spin_gyro_{seed}';rp=folder/'result.json';tp=folder/'trace.jsonl';sp=folder/'SOURCE_MANIFEST.json'
 result=load(rp);manifest=load(sp);expected=result['trace_artifact'];raw=tp.read_bytes()
 assert len(raw)==expected['bytes'] and hashlib.sha256(raw).hexdigest()==expected['SHA']
 rows=[json.loads(line) for line in raw.splitlines()];assert len(rows)==800 and result['complete']
 inputs=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [rp,tp,sp]]
 producer=[]
 selected={'run_ground_case_v5.py','physics_bridge.py','physics_bridge_v3.py','sensor_core_v4.py'}
 for item in manifest['files']:
  if Path(item['path']).name in selected:
   p=Path(item['path']);actual=sha(p);assert actual==item['SHA'];producer.append({'path':str(p),'sha256':actual,'matches_producer':True})
 times=[float(x['ground_truth_before']['time']) for x in rows];gt=[x['ground_truth_before'] for x in rows]
 assert all(times[i+1]>times[i] for i in range(len(times)-1))
 continuity=max(normxy(sub(rows[i]['ground_truth']['xyz'],rows[i+1]['ground_truth_before']['xyz'])) for i in range(len(rows)-1))
 aftergap=max(abs(x['time']-x['estimate_time']-.01) for x in rows)
 estimate_gap=max(abs(x['estimate_time']-x['ground_truth_before']['time']) for x in rows)
 age_identity=max(abs(x['estimate_time']-x['sensor_timestamp_s']-x['sensor_age_s']) for x in rows)
 records=[]
 for i,row in enumerate(rows):
  t=times[i];ts=row['sensor_timestamp_s'];age=row['sensor_age_s'];e=row['estimated14'];omega=row['raw_gyro'];q=row['encoder4'];dq=row['encoder_rate4']
  mids=[];vfs=[]
  for side in range(2):
   vf,r=wheel_forward(pins[side],q[2*side:2*side+2],dq[2*side:2*side+2],row['wheel_rate2'][side],omega,side,result['collision_radius_m']);mids.append(r);vfs.append(vf)
  mid=[.5*(mids[0][j]+mids[1][j]) for j in range(3)]
  pseudo=-(omega[2]*mid[0]-omega[0]*mid[2]);sampletruth,j=nearest_truth(times,gt,ts)
  true=gt[i];by=true['body_velocity'];rs=R(true['roll_true'],true['pitch_true'],true['yaw_true']);worldv=matvec(rs,by)
  heading_true=(true['gyro_true'][1]*math.sin(true['roll_true'])+true['gyro_true'][2]*math.cos(true['roll_true']))/math.cos(true['pitch_true'])
  records.append({'line':i+1,'t':t,'t_after':row['time'],'ts':ts,'age':age,'root':true['xyz'][:2],'root_after':row['ground_truth']['xyz'][:2],
    'true_vy_now':by[1],'true_vx_now':by[0],'true_vy_sample':sampletruth['body_velocity'][1],
    'sample_truth_index':j,'sample_root':sampletruth['xyz'][:2],'pseudo_vy':pseudo,'estimated_vx':e[7],
    'yaw_est_now':e[1],'yaw_est_sample':e[1]-age*e[8],'heading_rate_est':e[8],
    'yaw_true':true['yaw_true'],'heading_rate_true':heading_true,'body_gyro_true_z':true['gyro_true'][2],
    'mid':mid,'omega':omega,'wheel_vf_difference':abs(vfs[0]-vfs[1]),'world_v_true':worldv[:2],
    'wheelmid_world':[(true['wheel_xyz'][0][j]+true['wheel_xyz'][1][j])*.5 for j in range(2)]})
 windows={}
 for name,start in [('all',0.),('active',1.),('tail',6.)]:
  a=[x for x in records if x['t']>=start-1e-8];T=[x['t'] for x in a];truth=[sub(x['root'],a[0]['root']) for x in a]
  vxonly=integrate_trapezoid(T,[xyvel(x['yaw_est_now'],x['estimated_vx'],0.) for x in a])
  pseudo=integrate_trapezoid(T,[xyvel(x['yaw_est_now'],x['estimated_vx'],x['pseudo_vy']) for x in a])
  oracle=integrate_trapezoid(T,[x['world_v_true'] for x in a])
  truevy=integrate_trapezoid(T,[xyvel(x['yaw_est_now'],x['estimated_vx'],x['true_vy_now']) for x in a])
  yawonlytrue=integrate_trapezoid(T,[xyvel(x['yaw_true'],x['true_vx_now'],x['true_vy_now']) for x in a])
  agreement=[x for x in a if x['wheel_vf_difference']<.05]
  windows[name]={'count':len(a),'interval_s':[T[0],T[-1]],'root_displacement_m':normxy(truth[-1]),
    'wheel_midpoint_world_displacement_m':normxy(sub(a[-1]['wheelmid_world'],a[0]['wheelmid_world'])),
    'vy_pseudo_vs_same_packet_truth':compare([x['pseudo_vy'] for x in a],[x['true_vy_sample'] for x in a]),
    'vy_pseudo_vs_current_truth':compare([x['pseudo_vy'] for x in a],[x['true_vy_now'] for x in a]),
    'odom_est_vx_only':error_path(vxonly,truth),'odom_est_vx_plus_pseudovy':error_path(pseudo,truth),
    'diagnostic_est_vx_plus_TRUE_vy_not_deployable':error_path(truevy,truth),
    'oracle_full_R_true_velocity_quadrature_floor':error_path(oracle,truth),
    'oracle_yaw_only_true_velocity':error_path(yawonlytrue,truth),
    'paired_low_wheel_disagreement_threshold_not_acceptance_m_s':.05,
    'paired_low_wheel_disagreement_count':len(agreement),
    'vy_residual_when_wheels_agree':compare([x['pseudo_vy'] for x in agreement],[x['true_vy_sample'] for x in agreement]) if agreement else None,
    'estimated_vx_vs_true_now':compare([x['estimated_vx'] for x in a],[x['true_vx_now'] for x in a]),
    'true_heading_rate_minus_body_gyro_z_RMS':math.sqrt(statistics.mean((x['heading_rate_true']-x['body_gyro_true_z'])**2 for x in a))}
 # Strict packet-time integration: rewind only the known linear age yaw predictor;
 # no truth correction or fitted rotation/scale is applied to any odometry.
 unique=[]
 for x in records:
  if not unique or abs(x['ts']-unique[-1]['ts'])>1e-8:unique.append(x)
 pT=[x['ts'] for x in unique];pTruth=[sub(x['sample_root'],unique[0]['sample_root']) for x in unique]
 pBase=integrate_trapezoid(pT,[xyvel(x['yaw_est_sample'],x['estimated_vx'],0) for x in unique])
 pSide=integrate_trapezoid(pT,[xyvel(x['yaw_est_sample'],x['estimated_vx'],x['pseudo_vy']) for x in unique])
 packet={'unique_count':len(unique),'interval_s':[pT[0],pT[-1]],'root_displacement_m':normxy(pTruth[-1]),
         'vx_only':error_path(pBase,pTruth),'vx_plus_pseudovy':error_path(pSide,pTruth)}
 # Causal left-held world velocity over each already-recorded control interval.
 zoh_base=[0.,0.];zoh_side=[0.,0.]
 for x in records:
  dt=x['t_after']-x['t'];v0=xyvel(x['yaw_est_now'],x['estimated_vx'],0);v1=xyvel(x['yaw_est_now'],x['estimated_vx'],x['pseudo_vy'])
  for j in range(2):zoh_base[j]+=dt*v0[j];zoh_side[j]+=dt*v1[j]
 true8=sub(records[-1]['root_after'],records[0]['root'])
 full8={'interval_s':[records[0]['t'],records[-1]['t_after']],'root_displacement_m':normxy(true8),
        'producer_result_displacement_m':result['xy_displacement_m'],
        'ZOH_vx_only_endpoint_error_m':normxy(sub(zoh_base,true8)),'ZOH_vx_plus_pseudovy_endpoint_error_m':normxy(sub(zoh_side,true8))}
 with (HERE/f'samples_{seed}.csv').open('w',newline='',encoding='utf-8') as stream:
  fields=['line','t','t_after','ts','age','true_vy_now','true_vy_sample','pseudo_vy','estimated_vx','yaw_est_now','yaw_est_sample','heading_rate_est','yaw_true','heading_rate_true','body_gyro_true_z','wheel_vf_difference']
  writer=csv.DictWriter(stream,fieldnames=fields+['mid_x','mid_y','mid_z','root_x','root_y']);writer.writeheader()
  for x in records:writer.writerow({**{k:x[k] for k in fields},'mid_x':x['mid'][0],'mid_y':x['mid'][1],'mid_z':x['mid'][2],'root_x':x['root'][0],'root_y':x['root'][1]})
 return {'seed':seed,'case':folder.name,'inputs':inputs,'producer_hash_checks':producer,'rows':len(rows),
  'timing':{'estimate_vs_GT_before_max_s':estimate_gap,'after_minus_before_minus_10ms_max_s':aftergap,
    'sample_age_identity_max_s':age_identity,'GT_after_to_next_before_max_xy_m':continuity,
    'age_min_s':min(x['age'] for x in records),'age_max_s':max(x['age'] for x in records),
    'first_duplicate_packet_count':len(records)-len(unique),
    'physics_stage_warning':'Producer mj_step then qpos/qvel vs cached xmat/xpos/sensor fields: 0.5ms mixed stage, no replay/resynchronization done',
    'boxcar_warning':'gyro/rates averaged over previous 20 physics ticks, encoder positions are end-of-window; D3 timestamp age excludes this filter group delay'},
  'windows':windows,'packet_time_odometry':packet,'full_recorded_8s_ZOH':full8,
  'DR':{'wheel_mu':result['DR']['D0']['wheel_sliding_mu'],'D3':result['DR']['D3']}}

def main():
 manifest=load(SKELETON);pins=[manifest['neutral_skeleton_xz_m'][s] for s in ('left','right')]
 results=[analyze(seed,pins) for seed in SEEDS]
 dump('metrics.json',{'mode':'RECORDED_DATA_AND_FK_ONLY_NO_SIMULATION','skeleton':{'path':str(SKELETON),'sha256':sha(SKELETON)},'results':results})
 table=[]
 for r in results:
  w=r['windows']['active'];vy=w['vy_pseudo_vs_same_packet_truth'];p=r['packet_time_odometry'];z=r['full_recorded_8s_ZOH']
  table.append({'seed':r['seed'],'root_drift_8s_m':z['root_displacement_m'],'vy_RMSE_same_packet_m_s':vy['RMSE_m_s'],'vy_correlation':vy['correlation'],
   'active_vx_only_odom_endpoint_m':w['odom_est_vx_only']['endpoint_m'],'active_pseudovy_odom_endpoint_m':w['odom_est_vx_plus_pseudovy']['endpoint_m'],
   'packet_consistent_pseudovy_odom_endpoint_m':p['vx_plus_pseudovy']['endpoint_m'],
   'ZOH_8s_vx_only_endpoint_m':z['ZOH_vx_only_endpoint_error_m'],'ZOH_8s_pseudovy_endpoint_m':z['ZOH_vx_plus_pseudovy_endpoint_error_m']})
 dump('summary_table.json',table)
 with (HERE/'summary_table.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
 print(json.dumps(table,ensure_ascii=False,indent=2))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'analysis_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
