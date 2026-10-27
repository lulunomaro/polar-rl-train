"""PreserveV1; remove a premature install-receipt claim, with no new NPZ read."""
from pathlib import Path
import ast,hashlib,json,time
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 old=HERE/'W35_nearest250_reset_gas400_mutable_candidate_v1';new=HERE/'W35_nearest250_reset_gas400_mutable_candidate_v2';assert not new.exists();new.mkdir()
 old_helper=old/'W35_gas400_exact_selected_reset_compatibility_v1.py';old_reset=old/'e1_full_pose_reset.py'
 s=old_helper.read_text('utf8')
 a="actual_original_dependency_fullSHA_from_install_receipt=True";b="actual_original_dependency_install_receipt_required_from_caller=True"
 assert s.count(a)==1;s=s.replace(a,b)
 a=" require(bank.zip.fp is not None,'original np.load bank must remain open for caller')\n";assert s.count(a)==1;s=s.replace(a,'')
 helper=new/'W35_gas400_exact_selected_reset_compatibility_v2.py';helper.write_text(s,encoding='utf8');ast.parse(s)
 s=old_reset.read_text('utf8');assert s.count('from W35_gas400_exact_selected_reset_compatibility_v1 import')==2
 s=s.replace('from W35_gas400_exact_selected_reset_compatibility_v1 import','from W35_gas400_exact_selected_reset_compatibility_v2 import')
 reset=new/'e1_full_pose_reset.py';reset.write_text(s,encoding='utf8');ast.parse(s)
 report=dict(attempt_id='W35_RESET_READER_SCOPE_AND_PREMATURE_RECEIPT_CLAIM_CORRECTION_SOURCE_20261027_V2',epoch=time.time(),
  original_V1_retained=dict(helper=dict(path=str(old_helper),SHA=H(old_helper)),reset=dict(path=str(old_reset),SHA=H(old_reset))),
  V1_reader_scope_correction='The original preparation stage opened NPZ twice: first used-field metadata extraction, then independent used-input helper check. It did not compute fullNPZ SHA. The once wording described one preparation attempt, not one np.load call.',
  V1_source_claim_correction='The helper did not itself read a target source-integrity receipt. Its True install-receipt claim was premature. V2 explicitly requires the caller actual installation receipt and does not claim it exists.',
  removed_private_zip_fp_check='Unnecessary NpzFile implementation-detail check removed; original used q/points/rootheight/joint input identity checks retained.',
  actual_new_bank_model_or_USD_read=False,no_GPU_or_sdk_or_physics_or_new_physical_gate=True,
  V2=dict(helper=dict(path=str(helper),SHA=H(helper)),reset=dict(path=str(reset),SHA=H(reset))),
  actual_target_source_integrity_and_CPU_USD_composition_pending=True,W35_mutable_pending=True,E0_frozen_unmodified=True,
  Git_status='pending_root_ordinary_supplement')
 p=HERE/'reports/W35_RESET_SCOPE_CORRECTION_V2_SOURCE_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8')
 print(json.dumps(dict(V2=report['V2'],no_new_NPZ_read=True,actual_GPU=False)))
if __name__=='__main__':main()
