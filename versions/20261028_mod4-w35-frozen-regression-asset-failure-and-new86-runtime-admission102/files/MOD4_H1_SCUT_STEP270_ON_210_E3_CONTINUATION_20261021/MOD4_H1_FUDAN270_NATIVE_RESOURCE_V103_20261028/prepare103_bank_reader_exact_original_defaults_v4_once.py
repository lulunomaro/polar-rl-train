from pathlib import Path
import ast,copy,hashlib,json,os,shutil,time
N=Path(__file__).resolve().parent;R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.write_text(s,encoding='utf8')
def main():
 prior=json.loads((R/'TWO103_FUDAN270_PAYLOADS_PREPARED_ACTUAL.json').read_bytes());result=copy.deepcopy(prior)
 for mode,spec in result['payloads'].items():
  A=Path(spec['payload']);B=N/'payloads_v4'/mode;B.mkdir(parents=True);m=json.loads((A/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());rows={r['relative']:r for r in m['files']}
  original_reset=(A/'job0/runtime/isaac/mod4/scut_flat_rescue.py').read_text('utf8');assert "p['joint_pos'].get(n,0.) for n in robot.joint_names" in original_reset
  for row in m['files']:
   src=A/row['relative'];dst=B/row['relative'];dst.parent.mkdir(parents=True,exist_ok=True)
   if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(src,dst)
   else:shutil.copy2(src,dst)
  p=B/'target_native_flat90_source_sdk_CPU_once.py';old=p.read_text('utf8');assert old.count("r['joint_pos'][name]")==1
  new=old.replace("r['joint_pos'][name]","r['joint_pos'].get(name,0.)")
  assert new.replace("r['joint_pos'].get(name,0.)","r['joint_pos'][name]")==old
  write(p,new);ast.parse(new)
  c=json.loads((B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json').read_bytes());c['approved_python'][p.relative_to(B).as_posix()]=H(p);write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2))
  task=json.loads((B/'job0/TASK.json').read_bytes());task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
  for relative in ['target_native_flat90_source_sdk_CPU_once.py','FLAT90_SOURCE_CONTRACT_ACTUAL.json','job0/TASK.json']:
   p=B/relative;rows[relative]=dict(relative=relative,bytes=p.stat().st_size,SHA=H(p))
  m['files']=list(rows.values());write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(m,indent=2))
  spec.update(task=task,payload=str(B),job_root=spec['job_root'].replace('MOD4_H1_FUDAN270_NATIVE_2610v103/','MOD4_H1_FUDAN270_BANK_READER_2610v103CPUv3/'),manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'))
 result.update(epoch=time.time(),bank_reader_matches_original_reset_default_semantics=True,no_runtime_or_reward_change=True,source_CPU_pending=True,original_failed_seed27_initial_loads=dict(native101=1,normal86=1),new_CPU_repair_load_scope='fresh qualified-candidate installed-source qualification; not for Git or extra statistics',original_false_preserved=True)
 with (R/'TWO103_BANK_READER_V4_PAYLOADS_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
 s=(N/'install_two103_CPU_only_source_SDK_initial_CPU_v2_once.py').read_text('utf8').replace('TWO103_FUDAN270_PAYLOADS_PREPARED_ACTUAL.json','TWO103_BANK_READER_V4_PAYLOADS_PREPARED_ACTUAL.json')
 s=s.replace("root=spec['job_root'].replace('MOD4_H1_FUDAN270_NATIVE_2610v103/','MOD4_H1_FUDAN270_CPU_ADMISSION_2610v103CPUv2/')","root=spec['job_root']")
 s=s.replace('NATIVE103_','NATIVE103_V3_').replace('TWO103_CPU_ONLY_V2','TWO103_CPU_ONLY_V3').replace('TWO103_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json','TWO103_V3_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json')
 ast.parse(s)
 with (N/'install_two103_bank_reader_repaired_CPU_only_v3_once.py').open('x',encoding='utf8') as f:f.write(s)
 print(json.dumps(dict(new_payloads_prepared=True,new_remote_namespace=True,reader_one_get_default_only=True,no_models_read=True)))
if __name__=='__main__':main()
