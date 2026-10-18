"""Bound one existing owner-metadata connection around the hour end; no extra watcher."""
from pathlib import Path
import ast,json,time,shutil
B=Path(__file__).resolve().parent
def main():
 p=B/'collect_next_hour_only_missing_closed_finals_cost_exit_once.py';s=p.read_text('utf8');needle="out['owner']=d.a.code(c,d.a.t.PY,META,v['source_root'],timeout=90);out['experts']['e2']";assert needle in s
 replacement="""start=time.monotonic();observations=0
  while True:
   out['owner']=d.a.code(c,d.a.t.PY,META,v['source_root'],timeout=90);observations+=1
   if (out['owner']['rows'].get('COHORT_FINAL.json') and not out['owner']['actual_own_processes']) or time.monotonic()-start>=900:break
   time.sleep(10)
  out['source_owner_bound_metadata_wait']=dict(limit_seconds=900,observations=observations,same_connection_only_no_new_watcher=True,no_model_or_behavior_audit_before_actual_closed=True)
  out['experts']['e2']"""
 s=s.replace(needle,replacement);ast.parse(s)
 with (B/'collect_next_hour_missing_closed_finals_bounded_owner_wait_V2_once.py').open('x',encoding='utf8') as f:f.write(s)
 p=B/'save_third_hour_actual_handoff_automation_V19_once.py';s=p.read_text('utf8');(B/'prepared_history').mkdir(exist_ok=True);shutil.copy2(p,B/'prepared_history/save_third_hour_handoff_V19_before_bounded_final_wait.py');a='V/collect_next_hour_only_missing_closed_finals_cost_exit_once.py';assert a in s;s=s.replace(a,'V/collect_next_hour_missing_closed_finals_bounded_owner_wait_V2_once.py');s=s.replace('下一在实际本小时保存结束后只收缺本V三真正FINAL/PT','下一heartbeat在本小时结束附近就推进：若尚未完整保存，V2在同一source连接最多900秒只读取原owner终态metadata，实际闭合后才取模型，不另建watcher、不做中途模型或行为审计、不机械等下一小时；只收缺本V三真正FINAL/PT');ast.parse(s);p.write_text(s,'utf8')
 with (B/'reports/THIRD_HOUR_FUTURE_FINAL_BOUNDED_OWNER_WAIT_V2_PREPARED_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),prepared_AST_only=True,not_executed=True,actual_bound_owner162530=True,same_source_connection_max900_metadata_wait_before_any_final_download=True,no_midhour_PT_or_behavior_audit=True,no_second_monitor_or_GPU_Task_or_account_mutation=True,original_V1_helper_and_original_prepared_handoff_source_preserved=True,initial_apply_patch_exact_line_lookup_rejected_before_any_mutation='Monolithic prompt line did not match isolated filename line; separate prepared-script edit fixed exact string, no GPU or remote action'),f,indent=2)
if __name__=='__main__':main()
