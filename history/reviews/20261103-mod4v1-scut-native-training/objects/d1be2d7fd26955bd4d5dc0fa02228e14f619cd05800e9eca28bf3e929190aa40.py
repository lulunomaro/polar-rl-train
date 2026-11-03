"""Owned task dispatcher, no alternate budget or implicit checkpoint restore."""
from pathlib import Path
import argparse,json,os,runpy,sys

J=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('mode',choices=['train','evaluate']);a=p.parse_args()
task=json.loads((J/'TASK.json').read_bytes())
sys.path.insert(0,task.get('package_root',str(J/'package')))
if task.get('module_overlay'):
    import mod4v1_scut
    mod4v1_scut.__path__.insert(0,task['module_overlay'])
os.environ['MOD4_SCUT_SOURCE_PATHS']=str(J/'SOURCE_PATHS.json')
common=['--assets',task['assets'],'--runtime',task['runtime'],
    '--runtime-manifest',task['runtime_manifest'],'--guard',task['guard'],
    '--profile',task['profile']]
for path in task['support']:common += ['--support',path]
if a.mode=='train':
    go=json.loads((J/'GO_PRODUCTION.json').read_bytes())
    init=['--resize-resume' if task.get('resized_learning_continuation') else '--init-checkpoint',task['source_checkpoint']['path']]
    sys.argv=['mod4v1_scut.train',*common,'--job-root',str(J/'production'),
        '--num-envs',str(task['num_envs']),'--seed',str(task['seed']),
        '--iterations','10000000','--save-deadline',str(go['save_deadline']),
        *init,
        '--init-SHA',task['source_checkpoint']['SHA'],'--init-bytes',str(task['source_checkpoint']['bytes'])]
    runpy.run_module('mod4v1_scut.train',run_name='__main__')
else:
    final=json.loads((J/'production/FINAL.json').read_bytes())
    sys.argv=['mod4v1_scut.evaluate',*common,'--job-root',str(J/'evaluation'),
        '--checkpoint',final['checkpoint']['path'],'--checkpoint-SHA',final['checkpoint']['SHA']]
    runpy.run_module('mod4v1_scut.evaluate',run_name='__main__')
