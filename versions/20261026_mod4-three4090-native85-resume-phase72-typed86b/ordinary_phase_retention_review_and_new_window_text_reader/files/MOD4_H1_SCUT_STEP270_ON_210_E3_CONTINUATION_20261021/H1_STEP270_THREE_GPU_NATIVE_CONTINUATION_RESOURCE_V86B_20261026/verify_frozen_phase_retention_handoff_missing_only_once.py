from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent
A=N.parent/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026/agent_native_phase_retention_next_candidate_cpu_20261026'
def main():
 p=A/'FROZEN_NATIVE_PHASE_RETENTION_NEXT_CANDIDATE_INDEX.json';raw=p.read_bytes()
 assert hashlib.sha256(raw).hexdigest()=='68683c4fb6231910658f198890b8ee36a62df8e67ed5954c6aa09bbbae0f1a6e'
 index=json.loads(raw);assert index['frozen'] and index['source_metadata_CPU_passed']==index['source_metadata_CPU_total']==4
 assert index['candidate_sampler_implemented'] is False and index['candidate_runtime_admitted'] is False
 for row in index['files']:
  path=Path(row['path']);assert path.resolve().is_relative_to(A.resolve()) and path.suffix in ('.py','.md','.json')
  b=path.read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['SHA']
 with (N/'reports/FROZEN_PHASE_RETENTION_HELPER_ROOT_TEXT_SHA_REVIEW_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,index_path=str(p),index_SHA=hashlib.sha256(raw).hexdigest(),files_verified=len(index['files']),source_only_4_CPU_checks_not_runtime=True,source_design=dict(extra_declared_tensor_bytes=53010432,ceiling_MiB=64,changes_future_sampling_distribution=True,private_RNG_and_new_admission_required=True),candidate_not_selected_or_implemented=True,no_PT_raw_GPU_or_remote=True),f,indent=2)
 print(json.dumps(dict(passed=True,text_files_verified=len(index['files']),no_active_helper=True)))
if __name__=='__main__':main()
