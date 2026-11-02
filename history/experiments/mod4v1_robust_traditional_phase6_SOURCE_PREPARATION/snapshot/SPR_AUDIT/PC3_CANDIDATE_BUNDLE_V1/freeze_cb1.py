"""Small explicit reference freeze; no traversal/import/execution of any old core."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
NAMES=['SPR_AUDIT/portable_control_v3_current/'+n for n in ('pc3_control.h','pc3_estimator.c','pc3_controller.c','pc3_p25_data.h','pc3_geometry_data.h','pc3_vector_layout.h','pc3_replay_host.c','REFERENCE_VECTORS.csv','REFERENCE_LAYOUT.json','C_REPLAY_01.jsonl')]+['SPR_AUDIT/portable_core_v2_kinematics/'+n for n in ('ct_kinematics.c','ct_kinematics.h')]+['SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1/ROUNDTRIP_01.jsonl','SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1/selftest_io.py','CONTROL_CHAIN_SEAM_AUDIT_V1/REPORT.md','CONTROL_CHAIN_SEAM_AUDIT_V1/RECEIPT.json','SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/build_pa1_arm.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (HERE/'SOURCE_REFERENCES.json').exists()
 assert not (HERE/'cb1_candidate.c').exists()
 refs=[dict(path=n,bytes=(ROOT/n).stat().st_size,sha256=sha(ROOT/n))for n in NAMES]
 v=dict(status='PREREGISTERED_SMALL_SCOPE_ONLY',references=refs,pre_core_contracts={n:sha(HERE/n)for n in ('ARCHITECTURE.md','NUMERICAL_BUDGET.json')},freeze_script_sha256=sha(Path(__file__)),old_tree_traversal=False,old_executable_or_SDK_runs=0,physics_imports_or_steps=0)
 with (HERE/'SOURCE_REFERENCES.json').open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
 print(json.dumps(dict(status=v['status'],selected_files=len(refs),pre_core_contracts=v['pre_core_contracts'],global_tree_hash=False),indent=2))
if __name__=='__main__':main()
