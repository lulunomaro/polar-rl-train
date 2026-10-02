"""Isolated integrated-contact verification. No production takeover."""
from pathlib import Path
import subprocess,json,os,time
r=Path('/home/egde/rl_candidates/MOD4_contact_integrated_repair_20260930');p=r/'reports'
py='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
status={'stage':'waiting_probe','production_handover':False}
def save(): (p/'preflight_status.json').write_text(json.dumps(status,indent=2))
def run(name,args,expected=None):
 status.update(stage=name);save()
 e=dict(os.environ);e.update({k:str(v) for k,v in json.loads((r/'isaac/mod4/env.json').read_text()).items()})
 e.update(RM_CONTACT_INTEGRATED='1',RM_CONTACT_EAGER5MS='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 with (p/(name+'.log')).open('x') as f:
  child=subprocess.Popen([py,*args],cwd=r,env=e,stdout=f,stderr=subprocess.STDOUT)
  status['pid']=child.pid;save();rc=child.wait(timeout=1200)
 if rc or expected and not expected.exists():raise RuntimeError(name+' failed or missing output')
try:
 save();started=time.time()
 while not (p/'integrated_probe.json').exists():
  pid=json.loads((p/'probe_launch.json').read_text())['pid']
  if not Path('/proc/'+str(pid)).exists():raise RuntimeError('Probe exited without output')
  if time.time()-started>900:raise RuntimeError('Probe timeout')
  time.sleep(10)
 run('verification',['reports/verify_integration.py'],p/'integration_verification.json')
 assert json.loads((p/'integration_verification.json').read_text())['pass']
 ck=json.loads((p/'probe_launch.json').read_text())['checkpoint']
 out=p/'dual_statistics_smoke.json'
 run('dual_statistics_smoke',['isaac/mod4/validate_speed.py','--headless','--num_envs','12','--steps','300','--speed_limit','1.5','--seed','20260927','--checkpoint',ck,'--output',str(out)],out)
 d=json.loads(out.read_text());assert d['physics_pass'] and d['contact_capture_metadata']['integrated_enabled']
 assert all('strict_pass_integrated_mean' in g and 'strict_pass_window_legacy_capture' in g for g in d['groups'])
 status['statistics_pass']=True;save()
 run('ppo128_smoke',['isaac/mod4/train_mod4_ppo.py','--headless','--num_envs','128','--additional_iterations','2','--steps_per_env','24','--save_interval','1','--seed','20260928','--learning_rate','.0001','--init_checkpoint',ck,'--run_name','integrated_contact_preflight','--log_root',str(r/'smoke_logs')])
 files=sorted((r/'smoke_logs').glob('**/model_*.pt'),key=lambda x:x.stat().st_mtime);assert files
 audit=p/'checkpoint_audit.json'
 code="import torch,json;from pathlib import Path;p=Path("+repr(str(files[-1]))+");d=torch.load(p,map_location='cpu',weights_only=False);r={'path':str(p),'keys':list(d),'iteration':d.get('iter'),'std_present':any('std_param' in k for k in d['actor_state_dict']),'finite':all(bool(torch.isfinite(v).all()) for k in ['actor_state_dict','critic_state_dict'] for v in d[k].values() if torch.is_tensor(v))};Path("+repr(str(audit))+").write_text(json.dumps(r,indent=2));assert r['finite'] and r['std_present'] and 'optimizer_state_dict' in r['keys']"
 subprocess.run([py,'-c',code],check=True)
 status.update(stage='complete',ppo_pass=True,checkpoint_audit=json.loads(audit.read_text()))
except Exception as ex:status.update(stage='failed',error=repr(ex))
finally:status.update(pid=None,finished=time.time());save()
