from pathlib import Path
import hashlib,json,time
H=Path(__file__).resolve().parent;T=H.parent
original=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/W35_PPO50_gas400_source_preparation_20261027/runtime_candidate_v1/isaac/mod4/mild_dr.py'
def row(path):
 raw=path.read_bytes();return dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
def main():
 value=dict(ID='NEW214_MATERIAL_SOURCE_AND_20K_BUCKET_RNG_PRESERVATION_CPU_V1',epoch=time.time(),
  source_rows=[row(p)for p in sorted((H/'source').glob('*.py'))]+[row(H/'check214_once.py'),row(original)],
  num_envs=20000,old_reset_calls=2,new_reset_calls=2,new_own_reapply_calls=1,
  expected_groups=3,expected_negative_refusals=3,original_model_NPZ_USD_SDK_GPU_remote_reads=0,
  source_only_no_PhysX_capacity_or_actualUSD_admission=True,no_old213_or208_fixture_replay=True)
 with (H/'reports/CPU214_PURPOSE_FROZEN.json').open('x')as f:json.dump(value,f,indent=2)
 print(json.dumps(dict(ID=value['ID'],source_files=len(value['source_rows']))))
if __name__=='__main__':main()
