from pathlib import Path
import ast,hashlib,json,shutil,tarfile,time
D=Path(__file__).resolve().parent;R=D/'reports';Q=D/'payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not (R/'OWNED72_NATIVE_CANDIDATES_ASSETS_V2_ACTUAL.json').exists()
 v=json.loads((R/'SOURCE210_CHECKPOINTS_CANONICAL_AND_ORIGINAL_CONTRACT_ACTUAL.json').read_bytes());rows=[]
 contract=Q/'job0/runtime/isaac/mod4/import_contract.json'
 for i,x in enumerate(v['original_snapshots']):
  j=Q/('job'+str(i));a=j/'assets';m=j/'runtime/isaac/mod4'
  assert H(contract)==x['metadata']['import_contract_sha256']
  for p in (a/'import_contract.json',m/'import_contract.json'):
   if p.exists():assert H(p)==H(contract)
   else:shutil.copyfile(contract,p)
  assert 'robot_cfg.py' not in x['src_sha256']
  old=m/('train_curb20_entry_resume_ppo.py' if i==0 else 'train_slope5_snapshot_reviewed_resume_ppo.py')
  source=old.read_text(encoding='utf8');needle='from isaaclab.app import AppLauncher';assert source.count(needle)==1
  new=m/'train_host72_backend_admission_v1.py';assert not new.exists()
  new.write_text(source.replace(needle,'from zonglin2_app_launcher import Zonglin2AppLauncher as AppLauncher'),encoding='utf8')
  reverse=new.read_text(encoding='utf8').replace('from zonglin2_app_launcher import Zonglin2AppLauncher as AppLauncher',needle)
  assert ast.dump(ast.parse(reverse))==ast.dump(ast.parse(source))
  rows.append(dict(job=i,original_entry=str(old),original_SHA=H(old),candidate=str(new),candidate_SHA=H(new),inverse_AST_exact=True,
   import_contract_SHA=H(a/'import_contract.json'),robot_USD_SHA=H(a/'robot.usd'),robot_cfg_absent_in_original_snapshot_and_not_imported_by_original_task=True,
   native_scope='Original source-bound backend/fullrestore admission only; new command/route learning axis still requires separate admission.'))
  freeze=j/'runtime/reports/SOURCE_FREEZE.json';freeze.parent.mkdir(exist_ok=True)
  assert not freeze.exists();freeze.write_text(json.dumps(dict(sha256={str(p.relative_to(j/'runtime')).replace('\\','/'):H(p) for p in (j/'runtime').rglob('*') if p.is_file()}),indent=2),encoding='utf8')
 out=dict(epoch=time.time(),rows=rows,no_robot_cfg_fabrication=True,previous_partial_import_contract_reused_exact=True,no_network_GPU_PPO_or_budget=True)
 (R/'OWNED72_NATIVE_CANDIDATES_ASSETS_V2_ACTUAL.json').write_text(json.dumps(out,indent=2),encoding='utf8')
 print(json.dumps(dict(candidates=2,original_physics_inverse_AST_exact=True,robot_cfg_originally_absent=True)))
if __name__=='__main__':main()
