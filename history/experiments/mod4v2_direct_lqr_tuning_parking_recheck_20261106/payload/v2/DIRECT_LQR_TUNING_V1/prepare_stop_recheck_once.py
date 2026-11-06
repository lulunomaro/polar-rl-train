"""Fresh independent diagnostic of restored parking gate,not claiming5% selection met.
R4 fixed; no new candidate/parameter search. Original rule and failed trial retained.
"""
from pathlib import Path
import json
D=Path(__file__).resolve().parent;out=D/'STOP_RECHECK'
if out.exists():raise RuntimeError('Recheck prefix exists')
a=json.loads((D/'TRAIN_SELECTION001/RESULT.json').read_text(encoding='utf-8'))
r=json.loads((D/'THIRD_GAIN_CANDIDATE/runs/direct_lqr_effort4_train_530300/result.json').read_text(encoding='utf-8'))
base=a['rows'][0];ratio=r['tuning_score']/base['score']
if not(ratio>=.95 and r['metrics']['final_stop_body_vx_rms_m_s']<=.05 and base['metrics']['final_stop_body_vx_rms_m_s']>.05):raise RuntimeError('Not observed parking-gate restoration branch')
m=json.loads((D/'THIRD_GAIN_CANDIDATE/runs/direct_lqr_effort4_train_530300/meta.json').read_text(encoding='utf-8'))
bm=json.loads((D/'runs/direct_baseline_train_530300/meta.json').read_text(encoding='utf-8'))
if m['dr_meta']!=bm['dr_meta']or m['initial_qpos37_grading']!=bm['initial_qpos37_grading']:raise RuntimeError('TrainingC not same setting')
p=json.loads((D/'PROTOCOL.json').read_text(encoding='utf-8'))
p.update(id='MOD4V2_DIRECT_LQR_R4_PARKING_RECHECK_001',status='frozen_before_new_validation_draw',
 scope='R4 missed fixed5percent aggregate selection but restored original parking gate in training. Independent diagnostic of reproducibility,not retrospective winner/adoption/criterion relaxation.',
 formal_cases=[dict(id='baseline',seed=530301,nominal=False,profile='slow',tuning_name='baseline',tuning={}),
  dict(id='effort4',seed=530301,nominal=False,profile='slow',tuning_name='lqr_effort4',tuning=dict(effort_weight=4.))],
 training_record=dict(original5percent_selection_met=False,score_ratio=ratio,baseline_stop=base['metrics']['final_stop_body_vx_rms_m_s'],R4_stop=r['metrics']['final_stop_body_vx_rms_m_s']),
 independent_diagnostic_criteria=dict(primary='Compare fixed9-12s parkingRMS and original.05gate;retain both regardless of outcome',
  also_report='originalallchecks/scope/velocity/pitch/roll/support/unchangedaggregateScore',no_more_tuning=True,no_automatic_default_promotion=True))
s=(D/'run_tuning_case.py').read_text(encoding='utf-8');old='ROOT = Path(__file__).resolve().parents[1]'
if s.count(old)!=1:raise RuntimeError('Unknown root anchor')
s=s.replace(old,'ROOT = Path(__file__).resolve().parents[2]',1);compile(s,str(out/'run_tuning_case.py'),'exec')
out.mkdir(exist_ok=False);(out/'run_tuning_case.py').write_text(s,encoding='utf-8');(out/'PROTOCOL.json').write_text(json.dumps(p,indent=2),encoding='utf-8')
(out/'TRAINING_C_COMPARISON.json').write_text(json.dumps(dict(same_episode_DR=True,same_initial_qpos=True,score_ratio=ratio,old_selection_met=False,
 R4_score=r['tuning_score'],R4_metrics=r['metrics'],R4_contacts=r['contact_metrics'],R4_scope=r['new_scenario_scope_valid'],
 R4_actual_K=m['actual_controller_K_6x14'],R4_tuning=m['actual_tuning'],models=0,physics=0,raw_reads=0),indent=2),encoding='utf-8')
print('INDEPENDENT_PARKING_RECHECK_FROZEN new530301,old5percentrule remainsUNMET,R4unchanged')
