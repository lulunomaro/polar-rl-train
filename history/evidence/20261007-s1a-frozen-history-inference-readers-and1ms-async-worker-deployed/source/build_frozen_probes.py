"""Transform only inference construction; preserve original task and metric statements."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent;BASE=D/'reference/isaac/mod4';OUT=D/'generated';OUT.mkdir(exist_ok=True)
proof={}
for kind,name,var,indent in [('flat','validate_speed.py','rcfg',8),('spin','contact_calibration_probe.py','rc',4),('world','world_spin_probe.py','rc',4)]:
    original=(BASE/name).read_text(encoding='utf8');start=original.index(' '*indent+var+'=RslRlOnPolicyRunnerCfg(')
    end=original.index('    env.reset()',start)
    old=original[start:end]
    replacement=' '*indent+'from frozen_history_policy import build_frozen_policy\n'+' '*indent+'vec,policy,policy_observer=build_frozen_policy(vec,args.checkpoint,dev)\n'
    revised=original[:start]+replacement+original[end:]
    needle='    Path(args.output).write_text(json.dumps(result,indent=2))'
    assert revised.count(needle)==1
    revised=revised.replace(needle,"    result['frozen_architecture_audit']=policy_observer.audit()\n"+needle)
    # Prove original physical task/measurement/loop AST unchanged after masking loader/audit edits.
    a=original.replace(old,' '*indent+'pass\n')
    b=revised.replace(replacement,' '*indent+'pass\n').replace("    result['frozen_architecture_audit']=policy_observer.audit()\n",'')
    assert ast.dump(ast.parse(a),include_attributes=False)==ast.dump(ast.parse(b),include_attributes=False)
    p=OUT/('frozen_history_'+kind+'.py');p.write_text(revised,encoding='utf8')
    proof[kind]=dict(original_source_sha256=hashlib.sha256((BASE/name).read_bytes()).hexdigest(),
      new_entry_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),AST_original_task_measurement_loop_exact=True,
      change='Only frozen actor/history inference construction and audit field')
(D/'reports/FROZEN_PROBE_AST_CONTRACT.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
print(json.dumps(proof))
