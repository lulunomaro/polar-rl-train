"""Prepare a separate post-hour E0 evaluation purpose; no training source changes or dispatch."""
from pathlib import Path
import ast,json
D=Path(__file__).resolve().parent;stage=json.loads((D/'STAGE_E0_HOUR_WINDOW_RESULT.json').read_bytes());assert stage['returncode']==0
outputs={};s=(D/'worker_mod4v2_frozen_eval_e0_single_v3.py').read_text(encoding='utf8');a='worker_mod4v2_expert_migration_v4.py';assert s.count(a)==2;s=s.replace(a,'worker_mod4v2_expert_migration_hour_v5.py');outputs[D/'worker_mod4v2_frozen_eval_e0_hour_v4.py']=s
for name in('parent.py','stage.py','dispatch_once.py','collect_once.py'):
 s=(D/('E0_SINGLE_FROZEN_'+name)).read_text(encoding='utf8').replace('E0_SINGLE_FROZEN_','E0_HOUR_FROZEN_').replace('worker_mod4v2_frozen_eval_e0_single_v3.py','worker_mod4v2_frozen_eval_e0_hour_v4.py').replace('worker_mod4v2_expert_migration_v4.py','worker_mod4v2_expert_migration_hour_v5.py')
 if name=='stage.py':
  tree=ast.parse(s);node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='FRONTDOOR'for t in n.targets));fd=ast.literal_eval(node.value);fd.update(closed_pointer='E0_HOUR_WINDOW_CLOSED_RESULT_PATH.json',train_plan='SOURCE_PLAN_E0_HOUR_WINDOW_ACTUAL_V1.json',expected_train_root=stage['root']);lines=s.splitlines(keepends=True);lines[node.lineno-1:node.end_lineno]=['FRONTDOOR='+repr(fd)+'\n'];s=''.join(lines)
 outputs[D/('E0_HOUR_FROZEN_'+name)]=s
for p,s in outputs.items():assert not p.exists();ast.parse(s);compile(s,str(p),'exec')
for p,s in outputs.items():p.write_text(s,encoding='utf8',newline='\n')
print('Separate E0 post-hour eval sources compiled, actual current root bound; native stage requires true final/save/wait/settlement/release, no candidate/model/SDK access')
