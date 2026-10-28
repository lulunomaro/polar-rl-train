from pathlib import Path
import json,math,time
S=Path(__file__).resolve().parent;R=S/'reports'
def main():
 receipt=json.loads((R/'FROZEN105_CASE_FULL_TEXT_AND_NEW_RAW_TRANSFER_ACTUAL.json').read_bytes());paths={x['relative']:x['local_path'] for x in receipt['rows']};status=json.loads(Path(paths['case/episode/FROZEN_SINGLE_CASE_STATUS_ACTUAL.json']).read_bytes());names=status['body_names'];wi=[names.index(n) for n in ('left_wheel','right_wheel')];others=[i for i in range(31) if i not in wi];segments=[];current=[];allframes=[]
 def close():
  if current:
   segments.append(dict(start_callback=current[0]['callback'],end_callback=current[-1]['callback'],start_time_s=current[0]['callback']*.0025,end_time_s=current[-1]['callback']*.0025,callbacks=len(current),duration_s=len(current)*.0025,peak_simultaneous_clearance_m=max(x['bottom'] for x in current),maximum_each_wheel_contact_norm_N=max(x['wheel_force'] for x in current),maximum_nonwheel_contact_norm_N=max(x['nonwheel_force'] for x in current),positive_root_vz_seen=any(x['vz']>0 for x in current),actual_public_request_seen=any(x['request'] for x in current)));current.clear()
 with Path(paths['case/episode/ACTUAL_400HZ_31BODY_FRAMES.jsonl']).open(encoding='utf8') as f:
  for line in f:
   x=json.loads(line)
   if x['physics_callback']==0:continue
   s=x['state'];bottom=min(s['metrics']['wheel_bottom_above_floor_m']);forces=[math.sqrt(sum(v*v for v in row)) for row in s['body_contact_force31']];wf=max(forces[i] for i in wi);nf=max(forces[i] for i in others);row=dict(callback=x['physics_callback'],bottom=bottom,wheel_force=wf,nonwheel_force=nf,vz=s['root13_sdk_xyzw'][9],request=s['public_request']);allframes.append(row)
   if bottom>.005 and wf<=1 and nf<=1:current.append(row)
   else:close()
 close();qualified=[x for x in segments if x['callbacks']>=16 and x['positive_root_vz_seen']]
 value=dict(epoch=time.time(),scope='One additional necessary contact-evidence analysis of the SAME NEW105 recorded case to distinguish physical flight from mere lifted-wheel geometry; no old raw/model/physics replay',raw_source=paths['case/episode/ACTUAL_400HZ_31BODY_FRAMES.jsonl'],contact_force_basis='actual original31body contact-view net forces at2.5ms step callbacks, vector norm<=1N for both wheels and every nonwheel body',wheel_geometry_basis='original phase cached actual wheel mesh bottom above actual preedge floor',unloaded_no_nonwheel_over5mm_segments=segments,at_least40ms_and_positive_root_vz_segments=qualified,any_observed_short_actual_physical_flight=bool(qualified),peak_simultaneous_bothwheel_clearance_m=max(x['bottom'] for x in allframes),original270_counter_events=status['original270_terminal_physics_events'],not20cm_or270mm_or_stable_landing_success=True,not_real_robot_hardware_test=True,no_policy_model_reread_no_action_force_or_physics_change=True,exact_old_flat_counter_not_replayed_or_claimed=True)
 with (R/'NEW105_ACTUAL_SHORT_FLIGHT_WITH_ORIGINAL_CONTACT_EVIDENCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
 print(json.dumps(value))
if __name__=='__main__':main()
