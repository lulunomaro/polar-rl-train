from pathlib import Path
import ast
N=Path(__file__).resolve().parent;T=N.parent
old=T/"H1_NATIVE107_COHERENT20S_FROZEN_MOTION_WM_N1_V108_20261029/analyze_NEW108_newcase_motion_contact_clock_and_WM_TEXT_ONLY_once.py"
S=T/"H1_NATIVE111_COHERENT_REWARD_FROZEN_MOTION_WM_N1_V112_20261029"
s=old.read_text(encoding="utf8")
for a,b in [("FROZEN108","FROZEN112"),("NEW108","NEW112"),("source107_formal","source111_formal"),("qualified107_remains","qualified111_remains"),("json,math,time","json,math,time,statistics")]:s=s.replace(a,b)
a="result=actual['case']['result'];assert result['controls']==2000 and result['physics_callbacks']==8000 and result['termination']=='actual_original_done' and result['last_termination_terms']['values']['time_out']"
b="result=actual['case']['result'];count=result['controls'];assert 0<count<=2000 and result['physics_callbacks']==4*count and result['termination']=='actual_original_done'"
assert s.count(a)==1;s=s.replace(a,b)
s=s.replace("assert len(arrays)==2000","assert len(arrays)==count").replace("assert physics_count==8000","assert physics_count==4*count")
a="actual_done=x['actual_original_done'],actual_phase=x['actual_phase_record']))"
b=a+"\n   arrays[-1].update(world_velocity3=last['root13_sdk_xyzw'][7:10],actor_worldheading_cue=x['actor_obs86_for_action'][3],actual_task_reward_objective=x['actual_Fudan270_objective'])"
assert s.count(a)==1;s=s.replace(a,b)
a=" outcome=dict(epoch=time.time()"
b=""" active=[x for x in arrays if x['request_for_action']]
 request_motion=dict(actual_controls=len(active),world_forward_target_m_s=.5,world_vx_mean=statistics.fmean(x['world_velocity3'][0] for x in active) if active else None,world_vx_target_abs_error_mean=statistics.fmean(abs(x['world_velocity3'][0]-.5) for x in active) if active else None,world_vy_abs_mean=statistics.fmean(abs(x['world_velocity3'][1]) for x in active) if active else None,actor_heading_cue_range=[min(x['actor_worldheading_cue'] for x in active),max(x['actor_worldheading_cue'] for x in active)] if active else None,world_vx_negative_controls=sum(x['world_velocity3'][0]<0 for x in active),measured_world_velocity_not_reward_proxy=True)
 outcome=dict(actual_request_motion=request_motion,epoch=time.time()"""
assert s.count(a)==1;s=s.replace(a,b)
s=s.replace("controls=2000,physics_callbacks=8000,physical_seconds=20.,original_time_out_only=True","controls=count,physics_callbacks=4*count,physical_seconds=count*.01,original_termination_terms=result['last_termination_terms'],full_requested2000controls=count==2000")
s=s.replace("clock_ages_all_0_through1999=True","clock_ages_all_actual_controls_coherent=True").replace("actual_actor_request_matches_200_2000_all2000controls=True","actual_actor_request_matches_200_2000_all_actual_controls=True")
s=s.replace("'source_window_phase_label_scope_correction='","'source_window_phase_label_scope_correction='")
s=s.replace("V1 starts_grounded_not_air used first post-control endpoint. New derived labels use previous terminal as actual input s0; first0 unknown. Original V1 fields/errors retained, no model/physics rerun.","Selected112 source uses previous actual terminal as input, first unknown. This report additionally requires nonwheel<=1N for clean-supported-input subsets. Original flags remain, no model/physics rerun.")
s=s.replace("original_first_post_label=x['starts_grounded_not_air']","selected_source_input_grounded_label=x['starts_grounded_not_air']")
s=s.replace("# Source V1 flag looked at first POST-control endpoint, not input s0.","# Selected112 source records the actual prior endpoint INPUT label.")
s=s.replace("# Preserve it and derive the exact prior actual endpoint before this window.","# Independently require clean nonwheel force for this strict supported subset.")
s=s.replace("'one_step_teacherforced_max_wheel_error_m','contiguous_actual_action_WM'","'one_step_teacherforced_max_wheel_error_m','contiguous_actual_action_WM','actual_request_motion'")
s=s.replace("qualified111_remains_native_method_not_skill=True","qualified111_remains_native_method_not_skill=True")
compile(s,"new112_analysis","exec")
p=S/"analyze_NEW112_newcase_world_motion_contact_clock_and_WM_TEXT_ONLY_once.py"
with p.open("x",encoding="utf8",newline="\n") as f:f.write(s)
print(str(p))

