"""One bounded, explicitly uploaded repair case inside the existing finite owner."""
from pathlib import Path
import json,hashlib,re
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_ready(root,template):
 root=Path(root).resolve();p=root/'CURB_REPAIR_CASE_READY.json'
 if not p.is_file():return None
 v=json.loads(p.read_bytes());case=Path(v['case_root']).resolve();assert case!=root and case.is_relative_to(root) and not case.is_symlink();s=v['spec'];assert s['key']=='curb' and s['GPU_UUID']==template['GPU_UUID'] and s['python']==template['python'];assert 600<=s['max_parent_seconds']<=template['max_parent_seconds'] and s['exit_headroom_seconds']==300 and s['native_controls']==144 and s['native_script']=='native_admission_worker.py' and s['production_script']=='production_worker.py';assert re.fullmatch('[0-9a-f]{64}',s['source_SHA']) and re.fullmatch('[0-9a-f]{64}',s['manifest_SHA']);mf=case/'CONTINUATION_COMPLETE_MANIFEST_V2.json';assert H(mf)==s['manifest_SHA'];receipt=case/'TARGET_CPU_SOURCE_ADMISSION_ACTUAL.json';assert H(receipt)==v['target_CPU_receipt_SHA'];cpu=json.loads(receipt.read_bytes());assert cpu['passed_CPU_only'] and cpu['source_SHA']==s['source_SHA'] and cpu['manifest_SHA']==s['manifest_SHA'] and cpu['full_source_all_tensor_finite'] and cpu['all_target_manifest_files_actual_SHA'] and cpu['no_GPU_or_PPO'];assert v['existing_master_repair_axis_explicit'] and v['original_global_budget_unchanged']
 for r in v['original_live_control_files']:assert H(root/r['relative'])==r['SHA']
 return dict(spec=s,case_root=str(case),ready_SHA=H(p),target_CPU_receipt_SHA=v['target_CPU_receipt_SHA'])
