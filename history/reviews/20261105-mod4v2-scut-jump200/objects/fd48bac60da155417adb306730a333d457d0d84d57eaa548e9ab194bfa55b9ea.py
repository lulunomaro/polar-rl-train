"""New v2 process dispatcher; training starts from random initialization."""
import argparse,json,os,runpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('mode',choices=['train','evaluate']);a=p.parse_args()
task=json.loads((ROOT/'TASK.json').read_bytes())
sys.path.insert(0,task['package_root'])
import mod4v2_scut
mod4v2_scut.__path__.insert(0,task['module_overlay'])
mod4v2_scut.__path__.insert(1,task['previous_module_overlay'])
os.environ['MOD4_SCUT_SOURCE_PATHS']='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_SCUT_STEP270_2H_1793711274668684600/env20000_1h/SOURCE_PATHS.json'
common=['--assets',task['assets'],'--runtime',task['runtime'],'--runtime-manifest',task['runtime_manifest'],
        '--guard',task['guard'],'--profile','jump200']
for path in task['support']:common += ['--support',path]
if a.mode=='train':
    go=json.loads((ROOT/'GO_PRODUCTION.json').read_bytes())
    sys.argv=['mod4v2_scut.train',*common,'--job-root',str(ROOT/'production'),
        '--num-envs',str(task['num_envs']),'--seed',str(task['seed']),
        '--iterations','10000000','--save-deadline',str(go['save_deadline'])]
    source=task['source_checkpoint']
    sys.argv+=['--resume',source['path'],'--init-SHA',source['SHA'],'--init-bytes',str(source['bytes'])]
    runpy.run_module('mod4v2_scut.train',run_name='__main__')
else:
    final=json.loads((ROOT/'production/FINAL.json').read_bytes())
    sys.argv=['mod4v2_scut.evaluate',*common,'--job-root',str(ROOT/'evaluation'),
        '--checkpoint',final['checkpoint']['path'],'--checkpoint-SHA',final['checkpoint']['SHA']]
    runpy.run_module('mod4v2_scut.evaluate',run_name='__main__')
