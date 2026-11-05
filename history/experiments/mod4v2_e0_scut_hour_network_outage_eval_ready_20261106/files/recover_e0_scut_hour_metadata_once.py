"""A distinct metadata observer after the original SSH observer exited; no worker replay."""
from pathlib import Path
import json,time
D=Path(__file__).resolve().parent
old=json.loads((D/'COLLECT_E0_SCUT_HOUR_ONCE.json').read_bytes())
assert old['root']=='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_SCUT_HOUR_FULL_LEARNER_MIGRATION_20261106_062902_1793917742719982000'
assert not (D/'E0_SCUT_HOUR_CLOSED_RESULT_PATH.json').exists()
record=D/'E0_SCUT_HOUR_OBSERVER_CONNECTION_FAILURE_V1.json';assert not record.exists()
record.write_text(json.dumps(dict(kind='LOCAL_METADATA_OBSERVER_SSH_DROPPED_NOT_TRAINING_FAILURE',epoch=time.time(),root=old['root'],original_observer_job='pwsh-2e580d242d3c4fa8',original_observer_exit_code=1,error='Socket exception 10054; paramiko SSHException: Server connection dropped',last_received_actual_updates=18,remote_training_or_close_state='UNKNOWN_UNTIL_NEW_OWN_METADATA_READ',old_marker_and_snapshots_preserved=True,new_observer_only=True,worker_launch_or_stop_or_model_or_canonical_operations=0),indent=2),encoding='utf8')
s=(D/'collect_e0_scut_hour_once.py').read_text(encoding='utf8')
a="marker=D/'COLLECT_E0_SCUT_HOUR_ONCE.json'";assert s.count(a)==1;s=s.replace(a,"marker=D/'COLLECT_E0_SCUT_HOUR_RECOVERY1_ONCE.json'")
a="out=D/'reports'/s['run_id']";assert s.count(a)==1;s=s.replace(a,"out=D/'reports'/(s['run_id']+'_METADATA_RECOVERY1')")
exec(compile(s,str(Path(__file__)),'exec'),dict(globals(),__name__='__main__',__file__=str(Path(__file__))))
