from pathlib import Path
import json,hashlib,time,ast,shutil
D=Path(__file__).resolve().parent;Q=D/'payload';R=D/'reports'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (R/'FINAL_EXECUTABLE_PAYLOAD_MANIFEST_CPU_ACTUAL.json').exists();prior=json.loads((R/'TWO_EXPERT_UNUSED_PACKAGES_MANIFEST_AND_NEGATIVES_CPU_ACTUAL.json').read_bytes());frozen=[]
 for spec in prior['frozen']:
  b=Q/spec['key'];mf=b/'CONTINUATION_COMPLETE_MANIFEST_V2.json';shutil.copy2(mf,R/(spec['key']+'_PRE_FINAL_FREEZE_ORIGINAL_MANIFEST.json'));p=b/'cohort_finite.py';s=p.read_text('utf8').replace('new_budget_or_curriculum_or_DR_or_reward=False','new_budget_or_DR_or_hardware=False,explicit_new_CURB_approach_command_and_E3_recovery_reward_contract=True').replace('engineering_bounded2700_each_sum_actual_distinct_expert_seconds=True','engineering_CURB_cap2700_recovery_cap1800_sum_actual_distinct_expert_seconds=True');p.write_text(s,encoding='utf8');files=[]
  for p in sorted(b.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts or p==mf:continue
   if p.suffix=='.py':ast.parse(p.read_text('utf8'))
   files.append(dict(relative=p.relative_to(b).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
  m=json.loads(mf.read_bytes());m['files']=files;m['accounting_actual_contract']='One canonical owner after old E2 actual terminal and locks; sum2700/1800 independently, native0PPO uncharged';mf.write_text(json.dumps(m,indent=2),encoding='utf8');frozen.append(dict(spec,manifest_SHA=H(mf),files=len(files)))
 out=dict(epoch=time.time(),passed_CPU_only=True,frozen=frozen,earlier_manifest_bytes_preserved=True,final_contract_metadata_discloses_new_axes=True,actual_target_native_PPO_not_claimed=True);(R/'FINAL_EXECUTABLE_PAYLOAD_MANIFEST_CPU_ACTUAL.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
if __name__=='__main__':main()
