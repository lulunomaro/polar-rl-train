"""Additional recorded-data ablations; imports ONLY our local pure math parser.
No original producer/plant code import, replay, new simulation or model fitting.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import csv,json,math,statistics,hashlib,traceback
from analyze_odom import HERE,WORK,SEEDS,xyvel,integrate_trapezoid,sub,normxy,error_path,wrap,dump

def main():
 metrics=json.loads((HERE/'metrics.json').read_text(encoding='utf-8'));brief=[];path_rows=[]
 for case in metrics['results']:
  seed=case['seed'];trace=WORK/'results'/case['case']/'trace.jsonl';raw=trace.read_bytes()
  expected=next(x for x in case['inputs'] if x['path']==str(trace));assert hashlib.sha256(raw).hexdigest()==expected['sha256']
  rows=[json.loads(x) for x in raw.splitlines()];csvrows=list(csv.DictReader((HERE/f'samples_{seed}.csv').open(encoding='utf-8')))
  assert len(rows)==len(csvrows)==800
  current=[]
  for rawrow,crow in zip(rows,csvrows):
   gt=rawrow['ground_truth_before'];e=rawrow['estimated14'];current.append({'t':gt['time'],'pos':gt['xyz'][:2],
    'yaw':e[1],'trueyaw':gt['yaw_true'],'vx':e[7],'truevx':gt['body_velocity'][0],'truevy':gt['body_velocity'][1],
    'pseudo':float(crow['pseudo_vy']),'scalar':e[0]})
  active=[x for x in current if x['t']>=1-1e-8];times=[x['t'] for x in active]
  truth=[sub(x['pos'],active[0]['pos']) for x in active];ablations={};vectors={}
  variants={
   'estimated_vx_only':[xyvel(x['yaw'],x['vx'],0) for x in active],
   'estimated_vx_plus_pseudo':[xyvel(x['yaw'],x['vx'],x['pseudo']) for x in active],
   'TRUEyaw_estvx_pseudo_DIAGNOSTIC':[xyvel(x['trueyaw'],x['vx'],x['pseudo']) for x in active],
   'estyaw_TRUEvx_pseudo_DIAGNOSTIC':[xyvel(x['yaw'],x['truevx'],x['pseudo']) for x in active],
   'estyaw_TRUEvx_TRUEvy_DIAGNOSTIC':[xyvel(x['yaw'],x['truevx'],x['truevy']) for x in active]}
  for name,vel in variants.items():
   curve=integrate_trapezoid(times,vel);ablations[name]=error_path(curve,truth);vectors[name]=curve[-1]
  truthend=truth[-1];estimateend=vectors['estimated_vx_plus_pseudo'];angle=None
  if normxy(truthend)*normxy(estimateend)>1e-12:angle=math.degrees(math.atan2(estimateend[0]*truthend[1]-estimateend[1]*truthend[0],sum(a*b for a,b in zip(estimateend,truthend))))
  yawerrors=[wrap(x['yaw']-x['trueyaw']) for x in active];w=case['windows']['active'];tail=case['windows']['tail']
  brief.append({'seed':seed,'timing':case['timing'],'active_interval_s':[times[0],times[-1]],'active_root_displacement_xy_m':truthend,
   'active_estimated_pseudo_displacement_xy_m':estimateend,'active_estimated_pseudo_displacement_norm_m':normxy(estimateend),
   'active_drift_direction_error_deg':angle,'active_scalar_forward_gauge_change_m':active[-1]['scalar']-active[0]['scalar'],
   'active_yaw_error_wrapped_RMSE_rad':math.sqrt(statistics.mean(v*v for v in yawerrors)),
   'active_yaw_error_bias_rad':statistics.mean(yawerrors),'active_wheel_midpoint_drift_m':w['wheel_midpoint_world_displacement_m'],
   'active_vy_comparison':w['vy_pseudo_vs_same_packet_truth'],
   'tail_vy_comparison':tail['vy_pseudo_vs_same_packet_truth'],
   'active_vx_comparison':w['estimated_vx_vs_true_now'],
   'active_low_wheel_disagreement_count':w['paired_low_wheel_disagreement_count'],
   'active_vy_residual_when_wheels_agree':w['vy_residual_when_wheels_agree'],
   'active_full_R_true_velocity_floor':w['oracle_full_R_true_velocity_quadrature_floor'],
   'active_yaw_only_true_velocity_floor':w['oracle_yaw_only_true_velocity'],
   'active_truth_vy_estvx_odom':w['diagnostic_est_vx_plus_TRUE_vy_not_deployable'],
   'active_headingrate_minus_bodygyroZ_RMS':w['true_heading_rate_minus_body_gyro_z_RMS'],
   'active_ablations_truth_marked_not_deployable':ablations})
  T=[x['t'] for x in current];truecurve=[sub(x['pos'],current[0]['pos']) for x in current]
  base=integrate_trapezoid(T,[xyvel(x['yaw'],x['vx'],0) for x in current]);side=integrate_trapezoid(T,[xyvel(x['yaw'],x['vx'],x['pseudo']) for x in current])
  for i,x in enumerate(current):path_rows.append({'seed':seed,'line':i+1,'GT_before_time':x['t'],'true_relative_world_x':truecurve[i][0],'true_relative_world_y':truecurve[i][1],
   'vx_only_world_x':base[i][0],'vx_only_world_y':base[i][1],'plus_proxy_world_x':side[i][0],'plus_proxy_world_y':side[i][1]})
 dump('TIMING_AND_ABLATIONS.json',brief)
 with (HERE/'world_paths.csv').open('w',newline='',encoding='utf-8') as stream:
  writer=csv.DictWriter(stream,fieldnames=list(path_rows[0]));writer.writeheader();writer.writerows(path_rows)
 print(json.dumps([{'seed':x['seed'],'tail_vy_RMSE':x['tail_vy_comparison']['RMSE_m_s'],'tail_vy_corr':x['tail_vy_comparison']['correlation'],
  'active_vx_RMSE':x['active_vx_comparison']['RMSE_m_s'],'active_yaw_RMSE':x['active_yaw_error_wrapped_RMSE_rad'],
  'wheel_agree_count':x['active_low_wheel_disagreement_count'],'wheel_agree_vy_RMSE':x['active_vy_residual_when_wheels_agree']['RMSE_m_s'],
  'truth_velocity_floor_endpoint':x['active_full_R_true_velocity_floor']['endpoint_m'],
  'estimated_drift_norm':x['active_estimated_pseudo_displacement_norm_m'],'direction_error_deg':x['active_drift_direction_error_deg'],
  'ablation_endpoints':{k:v['endpoint_m'] for k,v in x['active_ablations_truth_marked_not_deployable'].items()}} for x in brief],indent=2))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'refine_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
