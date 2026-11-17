"""Direct frozen c874 reference under the exact final replay scripts; no Route2 actor hook."""
from pathlib import Path
import subprocess,sys,json,time
T=Path(__file__).resolve().parent;R=T.parents[2];out=T/'evidence/reference_c874_direct';out.mkdir(exist_ok=False)
model=R/'deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt'
# Use a fresh interpreter and disable only the optional actor replacement hook.
# The original script, original35D actor and original c874 checkpoint remain intact.
code="import sys,types,runpy;hook=types.ModuleType('history_eval_hooks');hook.install=lambda *a,**k:None;sys.modules['history_eval_hooks']=hook;script=sys.argv[1];sys.argv=sys.argv[1:];runpy.run_path(script,run_name='__main__')"
results={};start=time.time()
for name,script in [('pitch','fixed_pitch_eval.py'),('stairs','fixed_stair_eval.py'),('descent','descent_eval.py')]:
    cmd=[sys.executable,'-X','utf8','-B','-c',code,str(T/script),'--model',str(model),'--out',str(out/name)]
    if name in ('stairs','descent'):cmd+=['--highest-command-only']
    with (out/(name+'.log')).open('wb') as log:r=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
    results[name]={'exit_code':r.returncode};print('REFERENCE',name,r.returncode,flush=True)
receipt={'results':results,'complete':all(x['exit_code']==0 for x in results.values()),'wall_seconds':time.time()-start,'PPO_updates':0,'optimizer_updates':0,'direct_c874_actor':True,'Route2_hook':False}
(out/'EVALUATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
