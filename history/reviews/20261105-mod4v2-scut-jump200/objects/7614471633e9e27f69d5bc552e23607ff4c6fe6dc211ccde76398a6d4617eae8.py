"""Frozen dispatcher for actual Newton training and independent80."""
from pathlib import Path
import json,os,runpy,sys
J=Path(__file__).resolve().parent
p=json.loads((J/'PLAN.json').read_bytes())
sys.path.insert(0,p['package_root'])
import mod4v2_scut
for path in reversed([str(J/'overlay'),*p['previous_overlay_paths']]):mod4v2_scut.__path__.insert(0,path)
os.environ['MOD4_SCUT_SOURCE_PATHS']=p['scut_source_paths']
os.environ['MOD4V2_NEWTON_MJCF']=p.get('mjcf_remote',str(J/'model_source.xml'))
mode=sys.argv[1]
common=['--package',p['hardware_remote'],'--components',p['runtime'],
        '--reset-bank',p['reset_bank']]
if mode=='train':
 go=json.loads((J/'GO_PRODUCTION.json').read_bytes());s=p['source_checkpoint']
 module='mod4v2_scut.supermimic_train'if p.get('learner')=='SuperMimic'else'mod4v2_scut.newton_train'
 sys.argv=[module,*common,'--job-root',str(J/'production'),
    '--num-envs',str(p['num_envs']),
    '--resume',s['path'],'--resume-SHA',s['SHA'],'--save-deadline',str(go['save_deadline'])]
 if p.get('learner')=='SuperMimic':
  sys.argv+=['--binding',str(J/'SUPERMIMIC_BINDINGS.json')]
  if 'policy_residual_scale'in p:sys.argv+=['--residual-scale',str(p['policy_residual_scale'])]
 else:sys.argv+=['--seed',str(p['seed'])]
 runpy.run_module(module,run_name='__main__')
elif mode=='evaluate':
 s=json.loads((J/'production/FINAL.json').read_bytes())['checkpoint']
 module='mod4v2_scut.supermimic_evaluate'if p.get('learner')=='SuperMimic'else'mod4v2_scut.newton_evaluate'
 sys.argv=[module,*common,'--job-root',str(J/'evaluation'),
           '--checkpoint',s['path'],'--checkpoint-SHA',s['SHA']]
 if p.get('learner')=='SuperMimic':sys.argv+=['--binding',str(J/'SUPERMIMIC_BINDINGS.json')]
 runpy.run_module(module,run_name='__main__')
else:raise ValueError(mode)
