"""Freeze old stages + exact real MPC H15 inputs; never execute parent/physics."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent;PREV=HERE.parent/'portable_spin_h2_v1';MPC=HERE.parent/'C_MPC8_NUMERIC_V1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
 assert not (HERE/'SOURCE_FREEZE.json').exists();old={}
 for r in load(PREV/'SOURCE_FREEZE.json')['old_files']:
  p=Path(r['path']);assert sha(p)==r['sha256'];old[str(p)]={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
 for r in load(PREV/'INDEX.json')['files']:
  p=PREV/r['path'];assert sha(p)==r['sha256'];old[str(p)]={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
 for n in ['INDEX.json','VALIDATION.json','MANIFEST.json','index_validation_01.log']:
  p=PREV/n;old[str(p)]={'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
 refs=[]
 for n in ['actual_model_vectors.json','HESSIAN_BASELINE.json','COMPARISON.json','README.md','MANIFEST.json']:
  p=MPC/n;refs.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
 data=load(MPC/'actual_model_vectors.json');assert len(data['H32'])==15 and len(data['cases'])==18
 for i in range(15):
  for j in range(15):assert data['H32'][i][j]==data['H32'][j][i]
 report={'old_files':list(old.values()),'real_MPC_references':refs,'real_input_mode':data['mode'],'real_dimension':15,'real_cases':18,'objective':'.5*z^T H z + f^T z; exact f32 inputs assessed as double','warm':'original shifted previous synthetic-case quantized oracle, not closed-loop data','new_API_independent':True,'old_ABI_modified':False,'no_physics':True,'budget_sha256':sha(HERE/'NUMERICAL_BUDGET.json')}
 (HERE/'SOURCE_FREEZE.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'old_files_frozen':len(old),'real_dimension':15,'real_cases':18,'real_vectors_sha256':sha(MPC/'actual_model_vectors.json'),'physics_steps':0}))
if __name__=='__main__':main()
