"""Finite evaluation launcher; no optimizer or training."""
from pathlib import Path
import argparse,json,os,subprocess,time,hashlib
p=argparse.ArgumentParser();p.add_argument('--level',type=int,choices=[0,3],required=True);a=p.parse_args();b=Path(__file__).resolve().parent;plan=json.loads((b/'PLAN.json').read_text());root=Path(plan['root']);name=f'paired_ablation_level{a.level}_r1';out=b/name;log=b/(name+'.log')
if out.exists() or log.exists():raise SystemExit('Use a new run identifier')
r=subprocess.run(['nvidia-smi','--query-compute-apps=pid','--format=csv,noheader,nounits'],capture_output=True,text=True,check=True)
if r.stdout.strip():raise SystemExit('GPU occupied')
env=dict(os.environ);env.update(WARP_CACHE_PATH=str(root/'cache/warp'),XDG_CACHE_HOME=str(root/'cache'),TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),PYTHONUNBUFFERED='1',CUDA_VISIBLE_DEVICES='0',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
cmd=[plan['python'],'-B','-u',str(b/'start_and_dr_probe.py'),'--plan',str(b/'PLAN.json'),'--out',str(out),'--support',plan['support'],'--version',name,'--models',str(b/'MODELS.json'),'--level',str(a.level)]
with log.open('xb',buffering=0) as f:child=subprocess.Popen(cmd,cwd=plan['support'],env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
value=dict(pid=child.pid,epoch=time.time(),cmd=cmd,no_training=True,script_sha256=hashlib.sha256((b/'start_and_dr_probe.py').read_bytes()).hexdigest());(b/(name+'_LAUNCH.json')).write_text(json.dumps(value,indent=2));print(json.dumps(value))
