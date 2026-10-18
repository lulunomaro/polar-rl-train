"""New-stage helper preparation only; does not record, deploy, or change a monitor."""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;Q=B.parent/'MOD4_SCUT_FUDAN_SECOND_HOUR_20261019'
s=(Q/'archive_same_recipe_second_hour_and_local_behavior_unique_once.py').read_text('utf8')
s=s.replace("G=W/'MOD4_SCUT_FUDAN_JUMP_REWARD_20261019'","G=W/'MOD4_SCUT_FUDAN_SECOND_HOUR_20261019'").replace('cf8894e78b7c034b9ced6bde9745bbe8d3382502','3778db1e16f5da80a6e11a555d8aa2373f503bba').replace('scut-fudan-second-hour-closed-source-and-local-behavior','scut-fudan-third-hour-closed-sources-local-jump-feedback')
s=s.replace('Continue three experts from first SCUT Fudan hour finals and preserve local jump diagnostics','Continue three experts from second reward-hour finals and record new-source local jump regression')
s=s.replace('assert len(old)==1386','assert len(old)==1387').replace("history/evidence/MOD4_SCUT_FUDAN_JUMP_REWARD_20261019/REPORT_CAPTURE_INDEX.json","history/evidence/MOD4_SCUT_FUDAN_SECOND_HOUR_20261019/REPORT_CAPTURE_INDEX.json")
s=s.replace("assert len(git('tag','--list').splitlines())==1387","assert len(git('tag','--list').splitlines())==1388").replace('total_tags=1387,all1386old_objects_peels_exact=True','total_tags=1388,all1387old_objects_peels_exact=True')
s=s.replace('FIRST_SCUT_FUDAN_HOUR_LOCAL_MUJOCO_BEHAVIOR_V2_ACTUAL.json','SECOND_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json');ast.parse(s)
with (B/'archive_third_reward_hour_closed_sources_local_feedback_unique_once.py').open('x',encoding='utf8') as f:f.write(s)
s=(Q/'verify_actual_monitor_readback_and_future_templates_CPU_once.py').read_text('utf8').replace('SECOND_HOUR_V24','THIRD_HOUR_V25').replace('V24','V25').replace("assert '212000' in text and '197995' not in text","assert '223670' in text and '212000' not in text").replace('bound_owner212000','bound_owner223670').replace('T3sf3_1910v8','T3sf4_1910v9');ast.parse(s)
with (B/'verify_actual_monitor_readback_and_future_templates_CPU_once.py').open('x',encoding='utf8') as f:f.write(s)
s=(Q/'verify_same_recipe_and_local_callback_schema_CPU_once.py').read_text('utf8').replace("P=B.parent/'MOD4_SCUT_FUDAN_JUMP_REWARD_20261019'","P=B.parent/'MOD4_SCUT_FUDAN_SECOND_HOUR_20261019'").replace('==212000','==223670').replace('original_initial_module_path_AttributeError_and_transport10054_kept=True','no_new_module_or_transport_error=True');ast.parse(s)
with (B/'verify_same_recipe_and_local_callback_schema_CPU_once.py').open('x',encoding='utf8') as f:f.write(s)
print('Prepared unique new-stage archival and exact monitor readers; none executed here.')
