"""Merge valid fixed-size landing batches, checking common startup inputs exactly."""
from pathlib import Path
import json
import numpy as np
T=Path(__file__).resolve().parent;E=T/'evidence'
batches=[f'paired_landing_r2_b{i:02d}' for i in (1,2,3)]
reports=[json.loads((E/(name+'_RESULT.json')).read_text(encoding='utf8')) for name in batches]
inputs=[json.loads((E/(name+'_INITIAL_DR.json')).read_text(encoding='utf8')) for name in batches]
fields=['materials','effort_scale','body_mass_scale','total_mass_scale','mass','com','friction','leg_gain','wheel_gain','kp_scale','kd_scale','native_damping','action_delay_ticks','sensor_delay_ticks','initial_root_relative','initial_joint_position','initial_commands']
pairing={}
for field in fields:
 reference=np.asarray(inputs[0][field]);n=min(320,len(reference));error=0.
 for data in inputs[1:]:
  actual=np.asarray(data[field]);assert actual.shape==reference.shape,(field,actual.shape,reference.shape)
  error=max(error,float(np.abs(actual[:n]-reference[:n]).max()))
 assert error==0.,(field,error)
 pairing[field]=error
for name in batches:
 logfile=E/(name+'.log')
 text=logfile.read_text(encoding='utf8',errors='replace')
 assert 'miss interactions' not in text and 'foundLostAggregatePairsCapacity' not in text, name+' has invalid physics capacity warning'
merged=dict(reports[0]);merged['rows']=[row for report in reports for row in report['rows']];
for row in merged['rows']:
 row['total_reset_events_over8s']=row['resets_over8s']+row['reason_events_over8s'].get('timeout',0)
 row['raw_resets_over8s_semantics']='termination-only counter; boundary/time-limit timeouts are separately recorded in reason_events and included in total_reset_events_over8s'
merged['input_sha256']={k:v for report in reports for k,v in report['input_sha256'].items()};merged['wall_seconds']=sum(report['wall_seconds'] for report in reports);merged['num_envs']=960;merged['total_model_condition_initial_episodes']=2880;merged['batches']=batches;merged['common_input_max_difference']=pairing;merged['protocol']+='; fixed3model batches960env, identical startup properties/pose/command/draw dimensions across batches; no physics capacity warnings; original overcrowded2880env assessment INVALID and retained'
(E/'paired_landing_r2_RESULT.json').write_text(json.dumps(merged,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(E/'paired_landing_r2_INITIAL_DR.json').write_text(json.dumps(dict(batches=batches,fields_checked=pairing,raw_input_files=[name+'_INITIAL_DR.json' for name in batches]),indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(merged_models=len(merged['input_sha256']),input_pairing=pairing),ensure_ascii=False))
