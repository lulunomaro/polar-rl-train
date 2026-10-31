"""Freeze the new CPU-only source/schema purpose; no old inputs beyond text."""
from pathlib import Path
import hashlib,json,time
HERE=Path(__file__).resolve().parent;T=HERE.parent
OV=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
def row(path):
 raw=path.read_bytes();return dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())
def main():
 proofs={
  'E2':dict(**row(T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028/reports/E2_93_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json'),
   critical_D0_D7_key='all_critical_D1_D7_and_E2_command_CPU_validated',Adam_step=859300,stored_iteration=42822,
   LR=.00022500000000000002,model_SHA='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'),
  'E3':dict(**row(OV/'TWO97_NEW_E3_PPO_FORMAL_INITIAL_CPU_SOURCE_V1/reports/E3_97_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V1.json'),
   critical_D0_D7_key='all_critical_D1_D7_and_E3_13recipe_phase_CPU_validated',Adam_step=866060,stored_iteration=43090,
   LR=.0002562890625000001,model_SHA='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8')}
 value=dict(ID='NEW213_E2_CYCLE_FIELDS_AND_SAVED_EXPERT_SCHEMA_CPU_V1',epoch=time.time(),
  source_rows=[row(p)for p in sorted((HERE/'source').glob('*.py'))]+[row(HERE/'check213_once.py')],
  saved_CPU_proofs=proofs,envs=5,controls=240,synthetic_population_controls=1200,
  expected_groups=3,expected_metadata_checks=12,expected_negative_refusals=4,
  original_model_raw_NPZ_USD_SDK_GPU_remote_reads=0,neural_updates=0,
  no_old_fixture_replay=True,new_purpose='Only new E2 cross/signedyaw/UID/terminal fields and saved CPU proof schema join')
 path=HERE/'reports/CPU213_PURPOSE_FROZEN.json'
 with path.open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
 print(json.dumps(dict(path=str(path),source_files=len(value['source_rows']),ID=value['ID'])))
if __name__=='__main__':main()
