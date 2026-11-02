"""Hash-only preregistration and immutable old-component snapshot; no physics imports."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OLD=ROOT/'MINIHOP_AUDIT_V2'
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rec(p):
    p=Path(p).resolve();return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def dump(p,v):
    with Path(p).open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)
def main():
    assert sha(OLD/'README.md')=='b76416f02e11e8b44cce21ec40ad5d025f634a3991f4573484368da12e947145'
    assert sha(OLD/'INDEX.json')=='9ee8c0ee1bc02115aa3cb9ba0ae090610b42605007ff67c0c29e7ccb9f3fab80'
    previous=json.loads((OLD/'SOURCE_FREEZE.json').read_bytes());index=json.loads((OLD/'INDEX.json').read_bytes())
    known={}
    for r in previous['old_files']:
        assert Path(r['path']).stat().st_size==r['bytes']and sha(r['path'])==r['sha256'];known[r['path']]=r
    for r in index['files']:
        p=OLD/r['path'];assert p.is_file()
        if r['sha256']is not None:assert sha(p)==r['sha256']and p.stat().st_size==r['bytes']
        known[str(p.resolve())]=rec(p)
    refs=previous['sources'];assets=previous['model_assets']
    for r in refs+assets:assert Path(r['path']).stat().st_size==r['bytes']and sha(r['path'])==r['sha256']
    budget=json.loads((HERE/'NUMERICAL_BUDGET.json').read_bytes());model=json.loads((HERE/'MODEL_CONTRACT.json').read_bytes())
    assert budget['bisection_iterations']==40 and budget['random_oracle_cases']==192 and budget['valid_constraint_or_torque_box_violation_tolerance']==0.
    assert model['parent_accepted_narrowed_model']and not model['regen_credit']
    snapshot=dict(scope='NEW_PORTABLE_POWER_ALLOCATOR_V1_ONLY',old_files=list(known.values()),source_references=refs,model_assets=assets,old_component_modified=False,active_parent_R43_R44_outputs_excluded=True,root_active_world_leg_excluded=True,no_physics_import=True,preregistered=[rec(HERE/n)for n in ('ARCHITECTURE.md','MODEL_CONTRACT.json','NUMERICAL_BUDGET.json')])
    dump(HERE/'SOURCE_FREEZE.json',snapshot)
    result=dict(status='PREREGISTERED_BEFORE_CORE',old_files=len(known),source_references=len(refs),model_assets=len(assets),budget_SHA=sha(HERE/'NUMERICAL_BUDGET.json'),contract_SHA=sha(HERE/'MODEL_CONTRACT.json'),physics_steps=0)
    dump(HERE/'PREREGISTRATION_RECEIPT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
