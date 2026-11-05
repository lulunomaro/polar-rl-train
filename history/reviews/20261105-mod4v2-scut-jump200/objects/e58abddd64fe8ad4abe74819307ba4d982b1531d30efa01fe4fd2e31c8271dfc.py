from pathlib import Path
import json,subprocess,sys
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
note=G/'history/reviews/20261105-mod4v2-scut-jump200/NEWTON_MIGRATION_AND_SUPERMIMIC.md'
# Avoid a repository-wide stage in this shared checkout.
subprocess.run([sys.executable,'-B',str(N/'archive.py')],check=True)
status=subprocess.check_output(['git','-C',str(G),'status','--porcelain','-uall'],text=True)
selected=[]
for line in status.splitlines():
 path=line[3:]
 if path=='AGENTS.md' or path.startswith(('project/isaac/mod4v2_scut/','history/reviews/20261105-mod4v2-scut-jump200/')):
  selected.append(path)
assert selected
subprocess.run(['git','-C',str(G),'add','--',*selected],check=True)
subprocess.run(['git','-C',str(G),'-c','core.whitespace=cr-at-eol','diff','--cached','--check'],check=True)
subprocess.run(['git','-C',str(G),'reset','-q','--',*selected],check=True)
subprocess.run([sys.executable,'-B',str(G/'archive_tools/record_experiment.py'),
 '--id','mod4v2-newton-migration-supermimic-interleave-01',
 '--title','Integrate Newton MOD4v2 PPO and schedule SuperMimic interleaving',
 '--kind','repair','--note-file',str(note),'--files',*selected,
 '--validation','Actual native CPU/CUDA/PPO/graph tests, original failures and actual production receipts; no jump success inferred',
 '--push'],check=True)
