from pathlib import Path
import json,sys,os,runpy
r=Path(__file__).resolve().parent;j=r.parent
p=json.loads((j/'PLAN.json').read_bytes());v=json.loads((r/'PLAN.json').read_bytes())
sys.path.insert(0,p['package_root'])
import mod4v2_scut
for path in reversed([str(j/'overlay'),*p['previous_overlay_paths']]):mod4v2_scut.__path__.insert(0,path)
os.environ['MOD4_SCUT_SOURCE_PATHS']=p['scut_source_paths']
os.environ['MOD4V2_NEWTON_MJCF']=p['mjcf_remote']
s=v['checkpoint'];module='mod4v2_scut.supermimic_evaluate'
sys.argv=[module,'--package',p['hardware_remote'],'--components',p['runtime'],
 '--reset-bank',p['reset_bank'],'--job-root',str(r/'evaluation'),
 '--checkpoint',s['path'],'--checkpoint-SHA',s['SHA'],
 '--binding',str(j/'SUPERMIMIC_BINDINGS.json')]
runpy.run_module(module,run_name='__main__')
