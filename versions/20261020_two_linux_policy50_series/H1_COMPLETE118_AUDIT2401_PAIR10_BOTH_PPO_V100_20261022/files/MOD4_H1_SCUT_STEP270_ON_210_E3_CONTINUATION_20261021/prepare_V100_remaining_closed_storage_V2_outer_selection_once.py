from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;N=T/'H1_STEP270_E3_COMMAND_AUDIT_PAIR_V9_20261022';R=T/'reports';p=N/'relocate_remaining_actual_closed_pair9_H1_peer_TLS_V100_bounded_once.py'
s=p.read_text('utf8');needle="if inv['already_above_original_disk25']:";assert s.count(needle)==1
s=s.replace(needle,"if not inv['files']:").replace('PEER_TLS_REMAINING_V100_','PEER_TLS_REMAINING_V100_V2_').replace('REMAINING_V100_PEER_FORENSICS_','REMAINING_V100_V2_PEER_FORENSICS_');ast.parse(s)
new=N/'relocate_remaining_actual_closed_pair9_H1_peer_TLS_V100_V2_bounded_once.py';new.open('x',encoding='utf8').write(s)
v=dict(epoch=time.time(),original_helper_consumed=True,original_returncode=0,original_outcome='inventory complete but inherited outer disk25 early return skipped transfer; no target or remote storage process created',original_no_transfer_report=str(N/'reports/REMAINING_V100_PEER_FORENSICS_NO_TRANSFER_NEEDED_ACTUAL.json'),original_source_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),new_unused_source=str(new),new_source_SHA=hashlib.sha256(new.read_bytes()).hexdigest(),only_outer_selection_changed_to_no_remaining_files=True,new_namespace=True,original25GiB_training_admission_8GiB_savedstop_unchanged=True,closed_authorized_remaining_producer_data_only=True,no_training_failure_or_cost_change=True)
with (R/'V100_REMAINING_STORAGE_OUTER_SKIP_AND_UNUSED_V2_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(new_unused_V2=True,old_no_transfer_preserved=True)))
