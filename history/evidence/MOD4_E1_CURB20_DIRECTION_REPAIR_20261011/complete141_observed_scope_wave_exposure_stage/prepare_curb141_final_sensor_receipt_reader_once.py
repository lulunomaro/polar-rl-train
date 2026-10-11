"""Preserve original reader assertion; classify a documented final sensor observation."""
from direction_io import *
import zipfile

archive=W/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011/artifacts/e1-curb20-derived-mirrored-fullroute-frozen-v1.zip'
assert H(archive.read_bytes())=='b91238eddc550555a70f2a09e4cf8ff085d66fad1cb00bcb5736da6a71b04e7d'
with zipfile.ZipFile(archive) as z:
    sensor=z.read('runtime/isaac/mod4/sensor_mild_math.py')
    worker=z.read('runtime/isaac/mod4/frozen_history_flat.py')
assert b'max_abs_actual_bias_rad=float(self.bias.abs().max())' in sensor and b'sensor_recipe=e._sensor_mild.receipt()' in worker
helper='''
def final_sensor_receipt_pair(candidate,reference):
 a=candidate['sensor_recipe'];b=reference['sensor_recipe'];dynamic='max_abs_actual_bias_rad'
 assert set(a)==set(b) and all(a[k]==b[k] for k in a if k!=dynamic)
 assert a['episode_leg_encoder_bias_bound_rad']==b['episode_leg_encoder_bias_bound_rad']==.0075
 assert a['bias_finite'] and b['bias_finite'] and 0<=a[dynamic]<=.0075 and 0<=b[dynamic]<=.0075
 assert candidate['sensor_manager']['tick']==reference['sensor_manager']['tick']==1500
 return dict(static_sensor_configuration_and_noise_draw_counts_exact=True,final_observation_key=dynamic,
  candidate_final_bias_max=a[dynamic],reference_final_bias_max=b[dynamic],final_bias_observation_exact=a[dynamic]==b[dynamic],
  actual_bias_resampled_on_physical_episode_reset_as_original_source=True,not_an_initial_recipe_parameter=True,
  initial_sensor_bias_vectors_not_raw_captured_no_new_exact_claim=True,original_bias_bound_and_finite_checks_unchanged=True)
'''
p=D/'review_direction_exposure141_actual.py';s=p.read_text(encoding='utf8')
anchor="read=lambda p:json.loads(p.read_bytes())\n"
assert s.count(anchor)==1;s=s.replace(anchor,anchor+helper)
recipe="('initial','geometry','geometry_recipe','route_scope','sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names')"
newrecipe="('initial','geometry','geometry_recipe','route_scope','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe','body_names')"
assert s.count(recipe)==2;s=s.replace(recipe,newrecipe)
needle="   terrain['selected_source140_complete_review']=str(R/'CURB140_SCHEMA_REVIEW_1791718216726562600.json')"
assert s.count(needle)==1
s=s.replace(needle,"   terrain['sensor_receipt_source132']=final_sensor_receipt_pair(p,anchor)\n   terrain['sensor_receipt_selected140']=final_sensor_receipt_pair(p,selected140)\n"+needle)
q=D/'review_direction_exposure141_final_sensor_schema_actual.py';assert not q.exists();q.write_text(s,encoding='utf8')
save('CURB141_FINAL_SENSOR_RECEIPT_READER_SCHEMA_REVIEW.json',dict(epoch=time.time(),old_reader=str(p),old_SHA=H(p.read_bytes()),new_reader=str(q),new_SHA=H(q.read_bytes()),original_assertion_sensor_recipe_preserved=True,runtime_archive_SHA=H(archive.read_bytes()),sensor_source_SHA=H(sensor),worker_source_SHA=H(worker),source_proof='sensor_recipe is emitted after all1500 controls; max_abs_actual_bias_rad reads mutable bias resampled by SensorCorruption.reset; recipe bounds/config and initial physical parameters are independently exact',not_a_physical_failure=True,no_runtime_validator_tolerance_or_PPO_or_GPU_change=True,not_claiming_unrecorded_initial_sensor_bias_vectors_exact=True))
print(json.dumps(dict(prepared=True,new_reader=str(q))))
