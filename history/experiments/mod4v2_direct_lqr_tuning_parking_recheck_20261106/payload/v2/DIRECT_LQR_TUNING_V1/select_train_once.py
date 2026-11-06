"""Small new-result comparison/selection, fixed score. Never replays or reads raw."""
from pathlib import Path
import json
D=Path(__file__).resolve().parent
def main():
 out=D/'TRAIN_SELECTION001'
 if out.exists():raise RuntimeError('Training selection already consumed')
 out.mkdir(exist_ok=False)
 names=['baseline','lqr_damped','lqr_compliant'];rows=[];metas=[]
 for name in names:
  folder=D/'runs'/f'direct_{name}_train_530300'
  r=json.loads((folder/'result.json').read_text(encoding='utf-8'));m=json.loads((folder/'meta.json').read_text(encoding='utf-8'));metas.append(m)
  rows.append(dict(name=name,complete=r['complete'],eligible=r['engineering_eligible'],score=r['tuning_score'],metrics=r['metrics'],contacts=r['contact_metrics'],
   strict_pass=r['case_screen_pass'],scope=r['new_scenario_scope_valid'],false_checks=[k for k,v in r['checks'].items()if v is False],
   actual_leg_kp=m['actual_leg_kp'],actual_leg_kd=m['actual_leg_kd'],tuning=m['actual_tuning'],K=m['actual_controller_K_6x14'],
   wall_s=r['total_case_wall_s'],controls=r['controls'],physics=r['physics_steps'],producer_receipts=r['producer_raw_receipts']))
 md=lambda x,y:max(abs(float(a)-float(b))for a,b in zip(sum(x,[]),sum(y,[])))
 equal_DR=all(m['dr_meta']==metas[0]['dr_meta']for m in metas)
 equal_qpos=all(m['initial_qpos37_grading']==metas[0]['initial_qpos37_grading']for m in metas)
 Kdiff=[md(m['actual_controller_K_6x14'],metas[0]['actual_controller_K_6x14'])for m in metas]
 if not equal_DR or not equal_qpos or Kdiff[1]<=0 or Kdiff[2]<=0:raise RuntimeError('Not a valid actual K/DR comparison')
 eligible=[r for r in rows if r['eligible']]
 best=min(eligible,key=lambda r:r['score'])if eligible else rows[0]
 candidate=best['name']if best['name']!='baseline'and best['score']<.95*rows[0]['score']else None
 result=dict(rows=rows,same_episode_DR=equal_DR,same_initial_qpos=equal_qpos,actual_K_maxdiff_vs_baseline=Kdiff,
  best_training_name=best['name'],candidate_for_fresh_validation=candidate,threshold_fixed_relative_score=.95,
  training_episodes=3,independent_training_DR_settings=1,old_raw_reads=0,new_raw_reads=0,models_or_physics_or_replay_in_selection=0,
  strict_gates_preserved=True,engineering_ranking_not_T01_pass=True,default_controller_changed=False)
 (out/'RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in result.items()if k!='rows'},indent=2))
 for r in rows:print(json.dumps({k:r[k]for k in('name','score','eligible','strict_pass','scope','metrics','contacts','actual_leg_kp','actual_leg_kd')},ensure_ascii=False))
 if candidate:
  vd=D/'VALIDATION';vd.mkdir(exist_ok=False);p=json.loads((D/'PROTOCOL.json').read_text(encoding='utf-8'))
  p['id']='MOD4V2_DIRECT_LQR_FRESH_VALIDATION_001';p['status']='frozen_before_new_validation_draw'
  p['formal_cases']=[dict(id='baseline',seed=530301,nominal=False,profile='slow',tuning_name='baseline',tuning={}),
   dict(id='selected',seed=530301,nominal=False,profile='slow',tuning_name=candidate,tuning=p['settings'][candidate])]
  p['execution_policy'].update(validation_criterion='Candidate score lower than baseline,hard/guide0,eligible;still no formal release from one validation draw')
  (vd/'PROTOCOL.json').write_text(json.dumps(p,indent=2),encoding='utf-8');(vd/'run_tuning_case.py').write_text((D/'run_tuning_case.py').read_text(encoding='utf-8'),encoding='utf-8')
  # Runner resolves ROOT as parents[1],so retain actual workspace root for nested validation only.
  script=vd/'run_tuning_case.py';s=script.read_text(encoding='utf-8');s=s.replace('ROOT = Path(__file__).resolve().parents[1]','ROOT = Path(__file__).resolve().parents[2]',1);script.write_text(s,encoding='utf-8')
  compile(s,str(script),'exec');print('FRESH_VALIDATION_READY '+candidate)
if __name__=='__main__':main()
