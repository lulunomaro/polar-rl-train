"""Read only this completed attempt's own H1 SDK stdout for the actual native limit failure."""
from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;out=D/'attempts/admission2_H1_startup_tail.log';assert not out.exists();stage=json.loads((D/'STAGE_NINE_ADMISSION2_RESULT.json').read_bytes());closed=json.loads(Path(json.loads((D/'NINE_ADMISSION2_CLOSED_RESULT_PATH.json').read_bytes())['path']).read_bytes());m=closed['metadata'];assert m['OWNER_EXIT_ACTUAL.json']['all_own_children_waited']is True and m['OWNER_EXIT_ACTUAL.json']['original_cost_settled']is True and m['OWNER_EXIT_ACTUAL.json']['original_private_finite_authority_leases_released']is True and m['OUTER_OWNER_WAIT_ACTUAL.json']['original_owner_reaped']is True
sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 with s.open(stage['root']+'/roles/H1_normal/PPO_FULL_STDOUT_STDERR.log','r')as f:f.seek(0,2);n=f.tell();f.seek(max(0,n-100000));raw=f.read()
 out.write_bytes(raw);print(json.dumps(dict(path=str(out),bytes=len(raw),own_completed_attempt_log_only=True,model_SDK_GPU_C_or_foreign_operations=0)))
finally:s.close();c.close()
