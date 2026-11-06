"""One small-artifact final summary. Raw traces are never opened here."""
from pathlib import Path
import csv,json
D=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
 out=D/'FINAL_SUMMARY001'
 if out.exists():raise RuntimeError('Final summary already consumed')
 folders=[D/'runs'/f'direct_{n}_train_530300'for n in('baseline','lqr_damped','lqr_compliant')]
 folders += [D/'THIRD_GAIN_CANDIDATE/runs/direct_lqr_effort4_train_530300',D/'STOP_RECHECK/runs/direct_baseline_stop_recheck_530301',D/'STOP_RECHECK/runs/direct_effort4_stop_recheck_530301']
 r=[read(p/'result.json')for p in folders];m=[read(p/'meta.json')for p in folders]
 if any(not x['complete']or x['controls']!=1200 or x['physics_steps']!=24000 for x in r):raise RuntimeError('Incomplete nativecase;preserve actualprefix')
 if m[4]['dr_meta']!=m[5]['dr_meta']or m[4]['initial_qpos37_grading']!=m[5]['initial_qpos37_grading']:raise RuntimeError('Independentrecheck mismatch')
 if not all(x['dr_meta']==m[0]['dr_meta']and x['initial_qpos37_grading']==m[0]['initial_qpos37_grading']for x in m[:4]):raise RuntimeError('Training comparisons mismatch')
 rows=[]
 for p,x in zip(folders,r):
  rows.append(dict(case=p.name,score=x['tuning_score'],strict_pass=x['case_screen_pass'],scope=x['new_scenario_scope_valid'],eligible=x['engineering_eligible'],
   pitch_rms=x['metrics']['pitch_rms_rad'],roll_rms=x['metrics']['roll_rms_rad'],velocity_rmse=x['metrics']['slow_vx_rmse_m_s'],
   stop_rms=x['metrics']['final_stop_body_vx_rms_m_s'],whole_points=x['contact_metrics']['whole_body_unsupported_ticks'],
   supports=x['contact_metrics']['mainwheel_support_duty2'],tuning=x['actual_tuning'],wall_s=x['total_case_wall_s'],producer_receipts=x['producer_raw_receipts']))
 flat=[]
 for name in('flat_baseline_530302_001','flat_effort4_530302_001'):
  p=D/'FLAT_SPEED_BENCH'/name;flat.append(dict(case=name,**read(p/'result.json')))
 trainratio=r[3]['tuning_score']/r[0]['tuning_score'];valratio=r[5]['tuning_score']/r[4]['tuning_score']
 stop_train=1-r[3]['metrics']['final_stop_body_vx_rms_m_s']/r[0]['metrics']['final_stop_body_vx_rms_m_s']
 stop_val=1-r[5]['metrics']['final_stop_body_vx_rms_m_s']/r[4]['metrics']['final_stop_body_vx_rms_m_s']
 result=dict(rows=rows,flat_benchmark=flat,training_score_ratio=trainratio,training_fixed5percent_selection_met=trainratio<.95,
  independent_recheck_score_ratio=valratio,parking_relative_reductions=[stop_train,stop_val],
  additional_DR_parameter_settings=2,full_CAD_simulations=6,full_CAD_controls=7200,full_CAD_physics=144000,
  flat_simulations=len(flat),flat_physics=sum(x['physics_steps']for x in flat),
  adopted_as_formal_default=False,parking_priority_trial=dict(effort_weight=4.),all_original_failures_retained=True,
  note='R4 parking improvement reproduced on second setting,butstrictCADscreen not complete;initial5percenttrainingrule stillUNMET. Flat2m/s is extra fixture notCADqualification.',
  raw_reads=0,extra_model_or_physics_or_old_QA=0)
 out.mkdir(exist_ok=False);(out/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 with(out/'comparison.csv').open('x',newline='',encoding='utf-8-sig')as f:
  keys=['case','score','strict_pass','scope','pitch_rms','roll_rms','velocity_rmse','stop_rms','whole_points'];w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(rows)
 recipe=dict(name='parking_priority_R4_experimental',config=dict(effort_weight=4.),source_model='MOD4v2-HW300N60',
  observer='original unchanged,noE1',pitchrate_and_velocity_weights='original',leg_kp=120.,leg_kd=4.,
  training_relative_parking_improvement=stop_train,independent_relative_parking_improvement=stop_val,
  hardware_or_full_CAD_robust_qualified=False,formal_default_changed=False,actual_K_reference=m[3]['actual_controller_K_6x14'])
 (D/'PARKING_TRIAL_RECIPE.json').write_text(json.dumps(recipe,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in result.items()if k not in('rows','flat_benchmark')},indent=2))
 for x in flat:print(json.dumps({k:x[k]for k in('variant','complete','controls','physics_steps','forward','reverse','stop1','stop2','pitch_peak_rad','roll_peak_rad')},ensure_ascii=False))
if __name__=='__main__':main()
