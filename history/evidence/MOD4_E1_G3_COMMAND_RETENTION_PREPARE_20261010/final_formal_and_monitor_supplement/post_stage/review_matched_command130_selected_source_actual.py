"""Read-only comparison of actual129 against its complete, selected_source364_129 behavioral source."""
from pathlib import Path
import hashlib,json,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010'))
import review_actual_schema_checked as common
SELECTED='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
def compact(x):
 return {k:x[k] for k in ('straight','pure4pi','passed','count','max_abs_cross','along_range','directions','closure_mm','original_flags') if k in x}
def main():
 q=sorted(R.glob('CANDIDATE_130_REVIEW_[0-9]*.json'))[-1];v=read(q)
 collection=read(Path(v['collection']));rows={};files=[]
 for kind,row in v['retention'].items():
  folder=R/'cases'/('clk2500-closure-episode-d3-129-e1-g3-command-retention-retention-'+kind)
  p,m,r=[read(folder/n) for n in ('probe.json','manifest.json','result.json')]
  assert r['phase']=='complete' and not r['exit_code'] and not r['errors'] and not r['error_files'] and not r['new_learning']
  assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==SELECTED
  assert r['runtime_archive_sha256']=='8a964c1d0cfa291ea8faf72d978464daa8b2a8e90834554c435d528ffb222871' and r['steps']==p['steps']==m['steps']==1500
  candidate=next(x['probe'] for x in collection['cases'].values() if x['manifest']['kind']==kind and 'full_route_raw' not in x['probe'])
  keys=('reset_root_before_physics','reset_joint_pos_before_physics','sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe','physical_action_initial_episode_assignments','spring_pressure_initial_episode_assignments','gas_damping_initial_episode_assignments','chassis_PD_initial_episode_assignments')
  for k in keys:assert p[k]==candidate[k],(kind,k)
  params=lambda x:x.get('initial_parameter_audit') or x.get('mild_initial_parameters')
  assert params(p)==params(candidate) and p['seed']==candidate['seed']==20261002
  source=common.facts(p,kind);current=row['candidate']
  rows[kind]=dict(selected_source364_129=source,candidate_source365=current,initial_root30q_parameters_recipes_assignments_exact=True)
  files.extend(dict(path=str(folder/n),bytes=(folder/n).stat().st_size,sha256=sha(folder/n),complete_valid_evidence_reused_no_replay=True) for n in ('probe.json','manifest.json','result.json'))
 terrain_source=None
 if v['terrain'] is not None:
  anchor_path=sorted(R.glob('CANDIDATE_129_REVIEW_[0-9]*.json'))[-1]
  anchor=read(anchor_path);assert anchor['review_complete'] and anchor['own']['checkpoint']['sha256']==SELECTED
  terrain_source=anchor['terrain']
  files.append(dict(path=str(anchor_path),bytes=anchor_path.stat().st_size,sha256=sha(anchor_path),complete_valid_evidence_reused_no_replay=True))
 out=dict(epoch=time.time(),trial_id='E1-G3-COMMAND-130-SOURCE364-MATCHED-01',actual_review=str(q),selected_checkpoint_SHA=SELECTED,candidate_checkpoint_SHA=v['own']['checkpoint']['sha256'],retention=rows,terrain_selected_source364_129_approach040=terrain_source,terrain_candidate_source365=v['terrain'],summary=dict(retention={k:{role:compact(x[role]) for role in ('selected_source364_129','candidate_source365')} for k,x in rows.items()},terrain_selected_source364_129=terrain_source['groups'] if terrain_source else None,terrain_candidate_source365=v['terrain']['groups'] if v['terrain'] else None),reused_files=files,review_complete=v['review_complete'] and set(rows)=={'flat','spin','world'} and terrain_source is not None,pending=v['pending'],full_original_signed_circle_rows_and_prefixes_preserved=True,original_false_flags_not_relabelled=True,no_permanent_anti_forgetting_or_RM70mm_or_E1_graduation=True,no_GPU_learning_queue_canonical_or_signal_action=True,new_budget_seconds=0)
 p=R/('CANDIDATE_130_SELECTED_SOURCE_REVIEW_'+str(int(out['epoch']))+'.json');assert not p.exists();p.write_bytes(json.dumps(out,indent=2).encode())
 print(json.dumps(dict(report=str(p),summary=out['summary'],review_complete=out['review_complete'],pending=out['pending'])))
if __name__=='__main__':
 try:main()
 except Exception:
  p=R/('CANDIDATE_130_SELECTED_SOURCE_REVIEW_ERROR_'+str(int(time.time()))+'.json');assert not p.exists();p.write_bytes(json.dumps(dict(epoch=time.time(),trial_id='E1-G3-COMMAND-130-SELECTED-SOURCE-CPU-READER-01',error=traceback.format_exc(),read_only_no_production_mutation=True),indent=2).encode());raise
