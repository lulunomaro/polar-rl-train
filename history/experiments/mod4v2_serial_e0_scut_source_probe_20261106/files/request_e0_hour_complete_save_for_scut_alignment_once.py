"""Request only own original complete-boundary save/exit after the human's SCUT recipe correction."""
from pathlib import Path
import json,sys,time,posixpath
D=Path(__file__).resolve().parent;stage=json.loads((D/'STAGE_E0_HOUR_WINDOW_RESULT.json').read_bytes());readback=json.loads((D/'E0_HOUR_CURRENT_RECIPE_SOURCE_READBACK_V1.json').read_bytes());root=stage['root'];assert readback['root']==root and readback['selected_original_environment']['RM_SCUT_TERM_W']=='0.0';out=D/'E0_HOUR_SCUT_ALIGNMENT_STOP_REQUEST_V1.json';assert not out.exists();sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
client=connect72();s=client.open_sftp()
try:
 with s.open(root+'/roles/E0/TASK.json','rb')as f:task=json.loads(f.read())
 assert task['role']=='E0'and task['run_id']==stage['run_id']and task['source_SHA']=='6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693' and task['window_mode']=='ORIGINAL_FINITE_WALL_CLOCK_HOUR'
 stop=task['stop_file'];assert posixpath.normpath(stop)==root+'/roles/E0/STOP_AFTER_SAVE.json';r=dict(epoch=time.time(),run_id=task['run_id'],role='E0',reason='Human requires SCUT original recipe; actual inherited RM_SCUT_TERM_W0 and value_loss2 differ from registered V14 flat -200/value_loss4. Preserve complete current candidate, correct only NEW source/window.',reference_commit='b8ff79f3df855faf9dc92f4a282bd80c42649466',complete_own_save_and_exit_only=True,no_signal_no_live_reward_or_source_patch_no_ledger_or_refund=True)
 with s.open(stop,'wx')as f:f.write(json.dumps(r,indent=2).encode())
finally:s.close();client.close()
out.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))
