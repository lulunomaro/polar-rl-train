"""Read-only diagnosis: normal-mode transient-height counterfactual and bank capture."""
from pathlib import Path
import sys,json,argparse,hashlib,ast,contextlib,io
import numpy as np
T=Path(__file__).resolve().parents[1];D=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--name',required=True);p.add_argument('--lower-height-guard',action='store_true');a=p.parse_args();out=D/a.name;out.mkdir(exist_ok=False)
s=(T/'fixed_60_eval.py').read_text();tree=ast.parse(s)
for node in ast.walk(tree):
 if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='tasks'for t in node.targets):
  node.value.elts=[v for v in node.value.elts if ast.literal_eval(v.elts[0])in ['forward20','height020','height040']]
 if isinstance(node,ast.Call)and isinstance(node.func,ast.Name)and node.func.id=='range'and len(node.args)==1 and isinstance(node.args[0],ast.Constant)and node.args[0].value==10:node.args[0].value=1
s=ast.unparse(ast.fix_missing_locations(tree))
marker='old_step = sim.step';assert marker in s
capture="""old_step = sim.step
    captured=[]
    def capture_actor(module,args):
        captured.extend(args[0].detach().cpu().numpy().copy())
    rr.actor.register_forward_pre_hook(capture_actor)
"""
if a.lower_height_guard:capture+='    sim.args.term_height=.10\n'
s=s.replace(marker,capture)
s=s.replace('trace = []\n            row = replay.run_case', 'trace = []\n            row = replay.run_case')
needle="rows.append(row)";assert needle in s;s=s.replace(needle,needle+"\n                row['minimum_height']=float(data[:,2].min());row['maximum_pitch_equivalent_deg']=float(np.rad2deg(np.arccos(np.clip(data[:,3].min(),-1,1))));row['diagnostic_height_threshold_m']=sim.args.term_height\n                np.savez_compressed(out/(name+'_observations.npz'),obs=np.asarray(captured,dtype=np.float32),trace=data);captured.clear()")
# Treat lowered threshold as counterfactual only; never overwrite the original score.
s=s.replace("protocol='Original6tasks", "protocol='DIAGNOSTIC_ONLY_3TASKS_1SEED;Original6tasks")
sys.argv=[str(T/'fixed_60_eval.py'),'--model',a.model,'--out',str(out/'evaluation')]
# Preserve original helper __file__ paths; output and captured banks stay isolated.
s=s.replace('out.mkdir(exist_ok=False)', 'out.mkdir(exist_ok=False)')
(D/'generated_probe.py').write_text(s,encoding='utf8')
namespace={'__name__':'__main__','__file__':str(T/'fixed_60_eval.py')};exec(compile(s,'<read-only-normal-height-diagnosis>','exec'),namespace)
result=json.loads((out/'evaluation/RESULT.json').read_text());result['diagnostic_only']=True;result['formal_original_0_18m_scores_unchanged']=True;result['physical_or_training_config_changes']=False;result['lowered_height_guard']=a.lower_height_guard
(out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('DIAG_DONE',a.name,[(r['task'],r['passed'],r['minimum_height'])for r in result['rows']])
