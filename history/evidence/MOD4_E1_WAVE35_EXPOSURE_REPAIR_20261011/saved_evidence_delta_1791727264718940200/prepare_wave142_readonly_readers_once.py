"""Prepare read-only future final/candidate readers; no GPU or queue operations."""
from wave_io import *
import ast

def put_local(name,code):
 p=D/name;assert not p.exists();compile(code,str(p),'exec');p.write_text(code,encoding='utf8');return dict(path=str(p),bytes=p.stat().st_size,sha256=H(p.read_bytes()))

def main():
 p=W/'MOD4_E1_CURB20_DIRECTION_REPAIR_20261011/collect_direction_exposure141_actual.py';s=p.read_text(encoding='utf8')
 s=s.replace('from direction_io import *','from wave_io import *')
 old="NEW=json.loads((R/'EXPOSURE_MATCHED_ACTIVE_ROOT.json').read_bytes())['root']";assert s.count(old)==1;s=s.replace(old,'NEW=ROOT')
 s=s.replace('E1_CURB_DIRECTION_ASYNC_PUBLISHED.json','E1_142-e1-wave35-exposure-repair_ASYNC_PUBLISHED.json').replace('e1_CURB20_direction_exposure_matched_observation_PASSED.json','e1_WAVE35_exposure_005_observation_PASSED.json').replace('CURB141','WAVE142')
 rows=[put_local('collect_wave142_actual.py',s)]
 p=W/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010/review_wave131_actual.py';s=p.read_text(encoding='utf8').replace('CANDIDATE_131','WAVE142').replace('131-CANDIDATE','142-CANDIDATE').replace('131-CANDIDATE-CPU','142-CANDIDATE-CPU')
 src=W/'MOD4_E1_CURB20_DIRECTION_REPAIR_20261011/review_direction_exposure141_final_sensor_schema_actual.py';node=next(x for x in ast.parse(src.read_text(encoding='utf8')).body if isinstance(x,ast.FunctionDef) and x.name=='final_sensor_receipt_pair')
 s=s.replace('def main():',ast.unparse(node)+'\n\ndef main():',1)
 needle="h=b['health'];";assert s.count(needle)==1
 s=s.replace(needle,"cpu=read(sorted(R.glob('WAVE_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1]);assert cpu['passed'] and cpu['actual_source_count']==368 and cpu['own_checkpoint']['sha256']==b['checkpoint']['sha256']\n h=b['health'];")
 needle="assert r['checkpoint']['sha256']==m['artifacts']['checkpoint']['sha256']==b['checkpoint']['sha256'] and r['checkpoint']['finite_tensors']==b['checkpoint']['finite_tensors']";assert s.count(needle)==1
 s=s.replace(needle,needle+"==cpu['actual_finite_tensor_count']==102\n  if 'full_route_raw' in p:assert p['checkpoint_sha256']==b['checkpoint']['sha256']\n  else:assert p['checkpoint'].replace('\\\\','/').lower()==('D:/MOD4_async_eval/closure_episode_clock2500_v15/jobs/'+jid+'/checkpoint.bin').lower()")
 needle="for k in ('initial','geometry','geometry_recipe','route_scope','sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==anchor[k],k";assert s.count(needle)==1
 s=s.replace(needle,needle.replace("'sensor_recipe',",'')+"\n   terrain['sensor_final_receipt_reference128']=final_sensor_receipt_pair(p,anchor)\n   source=read(W/'MOD4_E1_G3_COMMAND_RETENTION_PREPARE_20261010/reports/cases/clk2500-closure-episode-d3-129-e1-g3-command-retention-terrain-flat/probe.json')\n   for k in ('initial','geometry','geometry_recipe','route_scope','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names'):assert p[k]==source[k],('selected129',k)\n   terrain['sensor_final_receipt_selected129']=final_sensor_receipt_pair(p,source)")
 rows.append(put_local('review_wave142_actual.py',s))
 p=W/'MOD4_MOE_TERRAIN_SUBEXPERT_REVISION_20261010/review_wave131_selected_source_actual.py';s=p.read_text(encoding='utf8').replace('CANDIDATE_131','WAVE142').replace('candidate_wave366','candidate_wave368').replace('131-SOURCE364','142-SOURCE364').replace('131-SELECTED-SOURCE','142-SELECTED-SOURCE')
 rows.append(put_local('review_wave142_selected_source_actual.py',s))
 save('WAVE142_READONLY_READERS_PREPARED.json',dict(epoch=time.time(),prepared_files=rows,compile_only=True,future_142_not_collected_or_passed=True,actual_complete_errorfree_only=True,legacy_skill_result_manifest_own_SHA_and_exact_checkpoint_path=True,terrain_probe_SHA_contract_unchanged=True,original35mm_and115129_fullraw_contracts_reused=True,final_sensor_observation_schema_141_reused_no_tolerance_relaxation=True,no_GPU_queue_budget_or_old_once_replay=True))
 print(json.dumps(dict(prepared=len(rows),compile_passed=True,no_future_result_assumed=True)))

if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE142_READER_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),pre_evaluation_reader_only=True));raise
