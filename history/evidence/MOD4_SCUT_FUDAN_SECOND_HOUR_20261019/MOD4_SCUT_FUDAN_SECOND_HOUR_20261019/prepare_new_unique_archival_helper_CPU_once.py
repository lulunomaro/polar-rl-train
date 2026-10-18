"""Prepare new stage archival only; no record, GPU, transport or budget operation."""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;P=B.parent/'MOD4_SCUT_FUDAN_JUMP_REWARD_20261019'
s=(P/'archive_scut_fudan_jump_reward_training_unique_once.py').read_text('utf8')
s=s.replace("G=W/'MOD4_THREE_GPU_HOUR5_CONTINUATION_20261018'","G=W/'MOD4_SCUT_FUDAN_JUMP_REWARD_20261019'")
s=s.replace('6e1f77a607d346497d1a08e2a87970aca8c6347f','cf8894e78b7c034b9ced6bde9745bbe8d3382502').replace('scut-fudan-public4-jump-reward-one-hour-three-experts','scut-fudan-second-hour-closed-source-and-local-behavior')
s=s.replace('Train H1 with SCUT jump rewards and Fudan complements while continuing all three experts','Continue three experts from first SCUT Fudan hour finals and preserve local jump diagnostics').replace('assert len(old)==1385','assert len(old)==1386')
a=s.index(' for q in (REPO/');z=s.index('  for r in json.loads(q.read_bytes())',a)
s=s[:a]+" for q in (REPO/'history/evidence/MOD4_SCUT_FUDAN_JUMP_REWARD_20261019/REPORT_CAPTURE_INDEX.json',):\n"+s[z:]
a=s.index(' note=');z=s.index(' NOTE.write_text',a)
s=s[:a]+" note=(B/'STAGE_SUMMARY.md').read_text('utf8')+'\\n\\nActual prior closure:\\n'+json.dumps(f,indent=2)+'\\n\\nActual new dispatch and learning metadata:\\n'+json.dumps(d,indent=2)+json.dumps(learning,indent=2)\n"+s[z:]
s=s.replace("assert len(git('tag','--list').splitlines())==1386","assert len(git('tag','--list').splitlines())==1387").replace('total_tags=1386,all1385old_objects_peels_exact=True','total_tags=1387,all1386old_objects_peels_exact=True')
s=s.replace("deferred=[])\n q=DEST/'REPORT_CAPTURE_INDEX.json'","deferred=[],local_NPZ_producer_index=[x['raw'] for x in json.loads((B/'reports/FIRST_SCUT_FUDAN_HOUR_LOCAL_MUJOCO_BEHAVIOR_V2_ACTUAL.json').read_bytes())['episodes']])\n q=DEST/'REPORT_CAPTURE_INDEX.json'")
ast.parse(s)
with (B/'archive_same_recipe_second_hour_and_local_behavior_unique_once.py').open('x',encoding='utf8') as f:f.write(s)
with (B/'reports/LOCAL_LOOKUP_AND_SHELL_ARCHIVAL_HELPER_PREPARATION_ERRORS_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),errors=[dict(kind='lookup_miss',attempt='payload/h1/job0/runtime/h1_takeoff_progress_environment_v2.py',actual='payload/h1/job0/runtime/isaac/mod4/h1_takeoff_progress_environment_v2.py',effect='read-only missing source alias; no GPU failure'),dict(kind='PowerShell ParserError before Python',attempt='inline Python archival-helper generator with nested shell quotes',message='Missing argument in parameter list',effect='no helper file, record, remote operation, GPU or budget change',repair='Separate UTF8 Python source file with AST validation; new helper only prepared')],original_behavior_AttributeError_preserved_in_separate_source_and_report=True,metadata_10054_original_preserved=True),f,indent=2)
print('New unique archival helper prepared and AST valid; not recorded.')
