"""Preserve original strict native120-vs1500 counter failure; static recipe only."""
from pathlib import Path
import hashlib,json,time
D=Path(__file__).resolve().parent
s=(D/'yawpi_actual_reader_components.py').read_text();old=" for key in ('geometry','geometry_recipe','reason_names','declared_time_outs','body_names','sensor_recipe','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe'):exact_tree(br[key],report[key],key)"
assert s.count(old)==1
new=""" for key in ('geometry','geometry_recipe','reason_names','declared_time_outs','body_names','feedback_recipe','action_recipe','spring_recipe','gas_recipe','chassis_PD_recipe'):exact_tree(br[key],report[key],key)
 sensor=report['sensor_recipe'];base_sensor=br['sensor_recipe'];dynamic_sensor_fields={'noise_draw_counts','max_abs_actual_bias_rad','bias_finite'}
 assert set(sensor)==set(base_sensor) and sensor['episode_leg_encoder_bias_bound_rad']==.0075 and sensor['bias_finite'] is True and sensor['max_abs_actual_bias_rad']<=.0075
 for key in sensor:
  if key not in dynamic_sensor_fields:exact_tree(base_sensor[key],sensor[key],'sensor_static_recipe/'+key)
 assert set(sensor['noise_draw_counts'])=={'base_ang_vel','projected_gravity','leg_pos','leg_vel','wheel_vel'}
 assert len(set(sensor['noise_draw_counts'].values()))==1 and min(sensor['noise_draw_counts'].values())>=steps*80
"""
s=s.replace(old,new);p=D/'yawpi_actual_reader_components_v2.py';assert not p.exists();p.write_text(s,encoding='utf8')
for name in ('review_yawpi_own_native_or_full_actual_CPU','review_yawpi_direct_same_WORLD_prefix_actual_CPU'):
 s=(D/(name+'.py')).read_text().replace('import yawpi_actual_reader_components as m','import yawpi_actual_reader_components_v2 as m')
 p=D/(name+'_v2.py');assert not p.exists();p.write_text(s,encoding='utf8')
o=D/'reports/ACTUAL_READER_V2_DYNAMIC_FINAL_SENSOR_SCHEMA_REPAIR_PREPARED.json';assert not o.exists();o.write_text(json.dumps(dict(epoch=time.time(),original_V1_source_and_CPU_error_retained=True,why='Native120 final noise_draw_counts cannot equal baseline1500 final counts. They are actual runtime counters, not static recipe; final bias is dynamic and independently bound .0075. Same actual INITIAL captured RNG and queues remain strict exact and all original static recipe fields compare exact.',no_GPU_SSH_PPO=True,Git_pending_root=True),indent=2),encoding='utf8')
