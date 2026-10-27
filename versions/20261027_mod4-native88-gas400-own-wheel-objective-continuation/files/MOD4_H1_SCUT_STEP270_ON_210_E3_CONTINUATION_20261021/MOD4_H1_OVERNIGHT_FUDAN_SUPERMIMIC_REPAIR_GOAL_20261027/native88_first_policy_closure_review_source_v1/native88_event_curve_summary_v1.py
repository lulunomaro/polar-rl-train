"""Pure completed-control event intervals; never infers controls from iterations."""
from pathlib import Path
import json,math
EVENTS=('takeoff_count','landing_count','recovery_count','both_leading_edges_cross_event_count')
def require(v,message):
 if not v:raise ValueError(message)
def snapshot(value):
 require(value['schema']=='completed_control_goal_events_v1','original completed-control event schema')
 n=value['num_envs'];c=value['complete_control_rows']
 require(n==4096 and type(c) is int and c>=0,'actual4096 completed controls required')
 require(value['environment_control_transitions']==c*n,'completed-control denominator mismatch')
 counts={k:value['events'][k] for k in EVENTS[:3]}
 counts[EVENTS[3]]=value['both_leading_edges_cross_event_count']
 require(all(type(x) is int and x>=0 for x in counts.values()),'event counter type/range')
 return dict(control=c,num_envs=n,counts=counts,diagnostic_valid=value['diagnostic_valid'] is True,
             original_flags=value)
def summarize_rows(rows,terminal_events=None):
 intervals=[];errors=[];previous=None;last_iteration=None;last_native=None;valid_rows=0;first=None
 for i,row in enumerate(rows):
  try:
   s=snapshot(row['events'])
   require(row['completed_control_rows']==s['control'] and row['environment_transitions']==s['control']*4096,'curve actual control fields disagree')
   it=row['native_iteration'];native=(row['world_updates'],row['policy_updates'])
   require(type(it) is int and it>=0 and all(type(x) is int and x>=0 for x in native),'native counters invalid')
   require(last_iteration is None or it>=last_iteration,'iteration regressed')
   require(last_native is None or all(a>=b for a,b in zip(native,last_native)),'native update counter regressed')
   if first is None:first=dict(control=s['control'],native_iteration=it,world_updates=native[0],policy_updates=native[1])
   if previous is None:
    initial=s['original_flags']['initial_counter_snapshot_sums']
    # A zero initial lifetime sum identifies the declared physical fresh origin;
    # otherwise the first observed row is left-censored without invented deltas.
    if all(initial.get(k)==0 for k in EVENTS[:3]):previous=dict(control=0,counts={k:0 for k in EVENTS})
   if previous is not None:
    require(s['control']>=previous['control'],'completed controls regressed')
    delta={k:s['counts'][k]-previous['counts'][k] for k in EVENTS}
    require(all(x>=0 for x in delta.values()),'lifetime event counter regressed')
    width=s['control']-previous['control']
    require(width>0 or not any(delta.values()),'event increment without completed controls')
    if any(delta.values()):intervals.append(dict(left_control_exclusive=previous['control'],right_control_inclusive=s['control'],
      left_simulated_seconds=previous['control']*.01,right_simulated_seconds=s['control']*.01,
      environment_control_transitions=width*4096,event_deltas=delta,
      observation='interval_censored_cumulative_event_increments_not_exact_event_times'))
   previous=s;last_iteration=it;last_native=native;valid_rows+=1
   if not s['diagnostic_valid']:errors.append(dict(row=i,original_event_diagnostic_false=s['original_flags']))
  except (ValueError,KeyError,TypeError) as exc:errors.append(dict(row=i,error=type(exc).__name__+': '+str(exc)))
 if terminal_events is not None:
  try:
   s=snapshot(terminal_events)
   if previous is not None:
    require(s['control']>=previous['control'],'terminal completed controls regressed')
    delta={k:s['counts'][k]-previous['counts'][k] for k in EVENTS};require(all(x>=0 for x in delta.values()),'terminal events regressed')
    if any(delta.values()):
     require(s['control']>previous['control'],'terminal increments without completed controls')
     intervals.append(dict(left_control_exclusive=previous['control'],right_control_inclusive=s['control'],
       environment_control_transitions=(s['control']-previous['control'])*4096,event_deltas=delta,
       observation='interval_censored_final_complete_control_snapshot'))
   previous=s
   if not s['diagnostic_valid']:errors.append(dict(terminal_original_event_diagnostic_false=s['original_flags']))
  except (ValueError,KeyError,TypeError) as exc:errors.append(dict(terminal_error=type(exc).__name__+': '+str(exc)))
 return dict(schema='mod4.native88.completed_control_event_curve.v1',diagnostic_passed=not errors,
   valid_curve_rows=valid_rows,first_curve_observation=first,latest_complete_snapshot=previous,
   event_increment_intervals=intervals,reader_errors=errors,
   control_clock_seconds=.01,num_envs=4096,denominator='actual completed_control_rows times4096',
   iterations_or_UTD_not_used_as_control_counts=True,no_updates_times24_conversion=True,
   intervals_not_precise_event_time_or_policy_causal_attribution=True,
   crossing_is_original_leading_edge_truth_not_footprint_landing=True,not_frozen_skill_graduation=True)
def read_curve(path,terminal_events=None):
 rows=[];parse_errors=[]
 try:
  with Path(path).open(encoding='utf8') as stream:
   for i,line in enumerate(stream):
    if not line.strip():continue
    try:rows.append(json.loads(line))
    except (ValueError,TypeError) as exc:parse_errors.append(dict(line=i+1,error=type(exc).__name__+': '+str(exc),original_line=line.rstrip('\n')))
 except OSError as exc:parse_errors.append(dict(error=type(exc).__name__+': '+str(exc)))
 result=summarize_rows(rows,terminal_events);result['JSONL_reader_errors']=parse_errors
 result['diagnostic_passed']=result['diagnostic_passed'] and not parse_errors
 return result
