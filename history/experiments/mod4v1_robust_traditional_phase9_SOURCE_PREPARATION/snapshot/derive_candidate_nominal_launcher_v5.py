"""One metadata-only derivation; freezes the old V4 launcher unchanged."""
from pathlib import Path
import ast, hashlib, json
R=Path(__file__).resolve().parent
src=R/'launch_manual_profile_train_v4.py'
raw=src.read_bytes(); text=raw.decode('utf-8')

def replace_once(old,new):
    global text
    assert text.count(old)==1,old
    text=text.replace(old,new)

replace_once('V1/V2/V3 immutable. V4 uses artifact-aware software-stop waves.',
             'V1/V2/V3/V4 immutable. V5 additionally binds actual candidate artifacts before RM admission.')
replace_once('from fresh_train_batch_v2 import launch,dump',
             'from fresh_train_batch_v2 import launch,dump\nfrom candidate_case_evidence_v1 import validate_case')
replace_once("p=json.loads((D/'PROTOCOL.json').read_bytes());cases=[(n,c)for n,c in p['configs']]",
             "p=json.loads((D/'PROTOCOL.json').read_bytes());cases=[(n,c)for n,c in p['configs']]\nbinding=p['candidate_binding']\nassert binding['entry_path']==args.runner\ndef bind_cases(items):\n    return [validate_case(R,n,c,s,binding) for n,c in items]")
replace_once("    f=launch(R,args.batch_prefix+'_flat',args.runner,flat,meta,keys,max_workers=workers)",
             "    f=launch(R,args.batch_prefix+'_flat',args.runner,flat,meta,keys,max_workers=workers)\n    flat_bindings=bind_cases(flat)\n    dump(D/'FLAT_RUNTIME_BINDING.json',dict(status='MATCHES_LOCKED_CANDIDATE',cases=flat_bindings,dynamic_qualification=False))")
replace_once("status='FLAT_SOFTWARE_ABORT_NO_RM_LAUNCH'", "status='FLAT_SOFTWARE_OR_CANDIDATE_BINDING_ABORT_NO_RM_LAUNCH'")
replace_once("    launch(R,args.batch_prefix+'_rm',args.runner,admitted,meta,keys,max_workers=workers)",
             "    launch(R,args.batch_prefix+'_rm',args.runner,admitted,meta,keys,max_workers=workers)\n    rm_bindings=bind_cases(admitted)\n    dump(D/'RM_RUNTIME_BINDING.json',dict(status='MATCHES_LOCKED_CANDIDATE',cases=rm_bindings,dynamic_qualification=False))")
ast.parse(text)
out=R/'launch_manual_profile_train_v5.py'
with out.open('x',encoding='utf-8')as f:f.write(text)
assert hashlib.sha256(src.read_bytes()).digest()==hashlib.sha256(raw).digest()
print(json.dumps(dict(status='DERIVED_AST_VALID_NO_MODEL_OR_PHYSICS_EXECUTION',
                      source=str(src),source_SHA=hashlib.sha256(raw).hexdigest(),
                      output=str(out),output_SHA=hashlib.sha256(out.read_bytes()).hexdigest(),
                      new_physics_steps=0),indent=2))
