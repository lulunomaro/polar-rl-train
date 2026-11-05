"""Derive ONE new reverse-profile diagnostic runner, not a parameter search.
All anchors/AST checked before creating output; old runner/physics stay unchanged.
"""
from pathlib import Path
import ast,json
R=Path(__file__).resolve().parent;D=R/'T01_OBSERVABILITY_V1'
source=(R/'T01_V2/run_t01_v2.py').read_text(encoding='utf-8')
protocol=json.loads((R/'T01_V2/T01_PROTOCOL_V1.json').read_text(encoding='utf-8'))
route_path=Path('C:/Users/lulu/Desktop/claude/mjcf/MOD4_LOCAL_LATEST_MOE_PLAYER_REQUESTED_20261023/player/routes.json')
routes=json.loads(route_path.read_text(encoding='utf-8'));route=next(x for x in routes if x['id']=='flat_run')
points=route['waypoints_m']
if len(points)!=2 or points[0][:2]!=[-9.,-1.]or points[1][:2]!=[-5.5,-1.]or route['spawn_yaw_rad']!=0.:
 raise RuntimeError('Public reverse route differs; do not invent free space')
protocol.update(id='MOD4V2_HW300N60_T01_REVERSE_OBSERVABILITY_001',status='frozen_before_one_new_diagnostic_case',
 scope='new reverse route profile + actual private actuator/time observation;not matched old-forward comparison or wholeT01 qualification',
 formal_cases=[dict(id='nominal_reverse_observe',seed=520130,nominal=True,profile='slow')],direction_sign=-1.,
 public_route=dict(source=str(route_path),id='flat_run',start_ground_m=points[1],goal_ground_m=points[0],yaw_rad=0.,
  change='Initial supported pose at published other endpoint BEFORE physics,not after-step teleport or natural rise'),
 observer=dict(motor_2khz=True,source_time=True,public_signal_adapter=True,force_or_FSM_or_controller_connection=False,
  original_engine_tick=True,original_PD_D4_DC_order=True,old_raw_or_QA_reread=False))
protocol['slow_command']['forward_m_s']=-.3

def change(old,new):
 global source
 if source.count(old)!=1:raise RuntimeError('Expected unique source anchor: '+repr(old[:100]))
 source=source.replace(old,new,1)
change('# Derived scoring-only runner for MOD4v2; original frozen gates unchanged.',
 '# ONE new reverse route diagnostic; old thresholds retained,progress projects along public reverse direction.')
change('import traceback\n','import traceback\nfrom dataclasses import asdict\n')
change("from RM_ROBUSTNESS_V1.run_t01 import safe, dump\n", "from RM_ROBUSTNESS_V1.run_t01 import safe, dump\nfrom diagnostic_stream_v1 import HashText,MotorAudit\nfrom public_signal_adapter_v1 import PublicSignalAdapter\n")
change("D/'T01_PROTOCOL_V1.json'","D/'PROTOCOL.json'")
change("    trace = (out/'trace.jsonl').open('x', encoding='utf-8', buffering=1)\n    contact_trace = (out/'contact_trace.jsonl').open('x', encoding='utf-8', buffering=1)",
 "    trace=HashText(out/'trace.jsonl');contact_trace=HashText(out/'contact_trace.jsonl')\n    motor_audit=MotorAudit(out/'motor_trace.jsonl');signal_adapter=PublicSignalAdapter()\n    metadata_counts={};skipped_motor_windows=0")
change('from bridge_v2 import V2Plant as AuditedPlant','from observed_bridge_v1 import ObservedV2Plant as AuditedPlant')
change('            try: return original_build(*a, **kw)', '''            try:
                model,meta=original_build(*a,**kw)
                if meta['zones'][0]['key']!='flat_run':raise ValueError('Expected published flat_run')
                meta['original_public_spawn']=copy.deepcopy(meta['zones'][0])
                meta['zones'][0]['spawn']=copy.deepcopy(protocol['public_route']['start_ground_m'])
                meta['zones'][0]['yaw']=protocol['public_route']['yaw_rad']
                meta['planned_reverse_route']=copy.deepcopy(protocol['public_route'])
                return model,meta''')
change('        direction, lateral = np.array([math.cos(yaw), math.sin(yaw)]), np.array([-math.sin(yaw), math.cos(yaw)])',
 '        direction, lateral = protocol[\'direction_sign\']*np.array([math.cos(yaw), math.sin(yaw)]), np.array([-math.sin(yaw), math.cos(yaw)])')
change("            t = time.perf_counter(); g = p.grade_current()", '''            t = time.perf_counter()
            metadata=copy.deepcopy(p.last_sensor_time_metadata)
            reason=metadata.get('source_selection_reason','NO_METADATA')if metadata else'NO_METADATA'
            metadata_counts[reason]=metadata_counts.get(reason,0)+1
            aligned=signal_adapter.observe(engine.packet,metadata,float(p.d.time))if engine.packet else None
            g = p.grade_current()''')
change("            xy = np.asarray(g['xyz'][:2])-origin", '''            if int(engine.controls)==k+1:
                motor_audit.observe(k,engine.last_tau,p.motor_telemetry_window,p.motor_telemetry_summary,samples or [])
            else:skipped_motor_windows+=1
            xy = np.asarray(g['xyz'][:2])-origin''')
change("                sensor_time_s=None if engine.packet is None else float(engine.packet.time_s),", '''                sensor_time_s=None if engine.packet is None else float(engine.packet.time_s),
                source_time_metadata=metadata,
                public_packet=None if engine.packet is None else dict(time_s=engine.packet.time_s,arrival_s=engine.packet.arrival_s,
                    gyro_body=engine.packet.gyro_body,accel_proper_body=engine.packet.accel_proper_body,
                    joint_pos4=engine.packet.joint_pos4,joint_vel4=engine.packet.joint_vel4,
                    wheel_vel2=engine.packet.wheel_vel2,motor_torque6=engine.packet.motor_torque6),
                alignment=None if aligned is None else asdict(aligned),
                motor_window_summary=p.motor_telemetry_summary,''')
change("        trace.flush(); contact_trace.flush()", "        trace.flush(); contact_trace.flush();motor_audit.flush()")
change("        assessed=all(value is not None for value in checks.values())", '''        # Additional planned-route diagnostics do not rewrite any old gate.
        xs=[r['post_truth']['xyz'][0]for r in rows]
        extra_diagnostics=dict(public_route_center_x_min=min(xs)if xs else None,public_route_center_x_max=max(xs)if xs else None,
            planned_endpoint_x_bounds=[-9.,-5.5],reverse_progress_projection=True,
            center_within_endpoints_plus_025m=bool(xs and min(xs)>=-9.25 and max(xs)<=-5.25))
        assessed=all(value is not None for value in checks.values())''')
change("status='T01_PROTOCOL_CASE_COLLECTED_NOT_WHOLE_TASK_OR_RELIABILITY_QUALIFICATION'", "status='NEW_REVERSE_OBSERVABILITY_CASE_NOT_T01_GRADUATION_OR_MATCHED_FORWARD_COMPARISON'")
change("            control_truth_contact_inputs=False,no_extra_reset=True,next_case_requires_parent_instruction=True)", '''            control_truth_contact_inputs=False,no_extra_reset=True,next_case_requires_parent_instruction=True,
            new_behavior_not_old_case_replay=True,extra_diagnostics=extra_diagnostics,
            private_motor_observation=motor_audit.summary(),public_signal_observation=signal_adapter.summary(),
            metadata_status_counts=metadata_counts,skipped_motor_windows=skipped_motor_windows,
            producer_raw_receipts=[trace.receipt(),contact_trace.receipt(),motor_audit.writer.receipt()],
            observer_data_returned_to_engine_or_controller_or_proxy=False)''')
change("        trace.close();contact_trace.close()", "        trace.close();contact_trace.close();motor_audit.close()")
ast.parse(source)
if D.exists():raise RuntimeError('Diagnostic prefix exists; do not regenerate/rerun')
D.mkdir();(D/'run_reverse_observe.py').write_text(source,encoding='utf-8')
(D/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2,ensure_ascii=False),encoding='utf-8')
(D/'PREPARATION.json').write_text(json.dumps(dict(derived_from='T01_V2/run_t01_v2.py',
 original_source_modified=False,all_old_gate_numbers_unchanged=True,physics_steps=0,model_builds=0,
 route_boundary_basis='actual published flat_run waypoints; reverse starts at OTHER endpoint -5.5,not undocumented -9 to -10.6 extension',
 new_case='v2_t01_reverse_observe_nominal_520130_001',no_default_runtime_change=True),indent=2),encoding='utf-8')
print('PREPARED_ONE_NEW_REVERSE_OBSERVABILITY_RUNNER physics0 model0',flush=True)
