from direction_io import *
import ast
from prepare_direction140_decision_and_exposure_continuation_once import ROOT,OLDROOT

def main():
 def replace_once(t,a,b):
  assert t.count(a)==1,a
  return t.replace(a,b)
 source=D/'read_direction_own_formal_cpu_actual.py';t=source.read_text()
 t=replace_once(t,"R/'DIRECTION_STARTUP_ACTIVE_ROOT.json'","R/'EXPOSURE_MATCHED_ACTIVE_ROOT.json'")
 t=t.replace('e1_CURB20_direction_repair_observation_PASSED.json','e1_CURB20_direction_exposure_matched_observation_PASSED.json')
 t=replace_once(t,"direction['explicit_new_episode_direction_scope']","not direction['explicit_new_episode_direction_scope'] and direction['predecessor_direction_state_restored_exact']")
 t=replace_once(t,"(D/'fresh_same_scope').glob",f"(Path({OLDROOT!r})/'fresh_same_scope').glob")
 t=replace_once(t,'import supervise_curb20_direction_startup_reviewed_once as ctrl','import supervise_curb20_direction_exposure_matched_once as ownctrl\nctrl=ownctrl.prior')
 t=replace_once(t,".replace('SOURCE_SHA',repr(SHA))",".replace('SOURCE_SHA',repr('e6df067ada011e06cb6fcb4989c3d32007680bf6926340e313f94ed305871e16'))")
 t=t.replace('DIRECTION_OWN_FORMAL_CPU_ACTUAL_','EXPOSURE_MATCHED_OWN_FORMAL_CPU_ACTUAL_').replace('explicit_new_geometry_entry_direction_disclosed=True','same_geometry_entry_direction_restored_exact=True')
 files={D/'read_direction_exposure_own_formal_cpu_actual.py':t}
 source=D/'collect_direction140_actual.py';t=source.read_text().replace('CURB140','CURB141')
 t=replace_once(t,"R/'DIRECTION_STARTUP_ACTIVE_ROOT.json'","R/'EXPOSURE_MATCHED_ACTIVE_ROOT.json'")
 t=t.replace('e1_CURB20_direction_repair_observation_PASSED.json','e1_CURB20_direction_exposure_matched_observation_PASSED.json')
 files[D/'collect_direction_exposure141_actual.py']=t
 source=D/'review_direction140_actual.py';t=source.read_text().replace('CURB140','CURB141').replace('DIRECTION_OWN_FORMAL_CPU_ACTUAL_','EXPOSURE_MATCHED_OWN_FORMAL_CPU_ACTUAL_')
 t=replace_once(t,"ownCPU['actual_source_count']==423","ownCPU['actual_source_count']==424")
 anchor="   retention[kind]=dict(candidate=common.facts(p,kind),source364=common.facts(source,kind),baseline32053=common.facts(baseline,kind),initial30q_parameters_recipes_assignments_pair_exact=True,reset_audit=resets,feedback_age_pair_exact=age)"
 added=anchor+"\n   selected140=read(R/'cases'/('clk2500-closure-episode-d3-140-e1-curb20-direction-repair-retention-'+kind)/'probe.json')\n   assert all(p[k]==selected140[k] for k in keys) and params(p)==params(selected140)\n   retention[kind]['source423']=common.facts(selected140,kind)"
 t=replace_once(t,anchor,added)
 t=replace_once(t,"('source364','candidate','baseline32053')","('source364','source423','candidate','baseline32053')")
 anchor="   for k in ('initial','geometry','geometry_recipe','route_scope','sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==anchor[k],k"
 added=anchor+"\n   selected140=read(R/'cases/clk2500-closure-episode-d3-140-e1-curb20-direction-repair-terrain-flat/probe.json')\n   for k in ('initial','geometry','geometry_recipe','route_scope','sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==selected140[k],k\n   terrain['selected_source140_complete_review']=str(R/'CURB140_SCHEMA_REVIEW_1791718216726562600.json')"
 t=replace_once(t,anchor,added);files[D/'review_direction_exposure141_actual.py']=t
 indices=[]
 for p,t in files.items():
  assert not p.exists();ast.parse(t);p.write_bytes(t.encode());indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=H(p.read_bytes())))
 save('EXPOSURE_FINAL_AND141_READERS_PREPARED.json',dict(epoch=time.time(),root=ROOT,source_count=424,own_finite_tensors_bound_to_actual_CPU104=True,read_only_files=indices,source140_e6df_direct_matched_comparison_plus_source129_preserved=True,no_GPU_eval_PPO_or_budget_write=True))
 print(json.dumps(dict(readers=len(files),own_final_pending=True,candidate141_pending=True)))

if __name__=='__main__':main()
