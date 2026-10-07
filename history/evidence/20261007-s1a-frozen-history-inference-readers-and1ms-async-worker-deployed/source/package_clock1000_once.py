"""Create an immutable, actual-source1ms/history package without publishing jobs yet."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
assert not (R/'CLOCK1000_PACKAGE_STAGED.json').exists()
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,hashlib,zipfile,os,shutil,time
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');Z=Path('/home/egde/rl_candidates/MOD4_S1A_FROZEN_EVAL_CONTROLLER_20261007')
B=Path('/home/egde/rl_candidates/MOD4_S1A_HISTORY_LAUNCH_REVIEW_20261007');A=E/'artifacts';A.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
approval=json.loads((E/'reports/PLAN_APPROVAL.json').read_text());assert approval['approved'] and 'S0E' in approval['allowed_stages']
assert approval['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
target=E/'reports/CLOCK1000_PACKAGE_STAGED.json';assert not target.exists()
sdk=json.loads((Z/'reports/FROZEN_HISTORY_NATIVE_SDK_PASSED.json').read_text());assert sdk['passed']
freeze=json.loads((Z/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(freeze)==219
files={};payload=[]
for n,h in freeze.items():
 p=Z/n;assert sha(p)==h,n;files['runtime/'+n]=h;payload.append((p,'runtime/'+n))
cfg=json.loads((Z/'isaac/mod4/env.json').read_text());assert float(cfg['RM_PHYSICS_DT_S'])==.001
asset=Path('/home/egde/fangzhen_linux/incoming/_from_target_20260928')
from pxr import Sdf
layer=Sdf.Layer.FindOrOpen(str(asset/'robot.usd'));assert layer and not layer.GetExternalReferences(), 'External USD dependencies require explicit packaging'
for name in ['robot.usd','import_contract.json']:
 p=asset/name;files['assets/'+name]=sha(p);payload.append((p,'assets/'+name))
assert files['assets/robot.usd']=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
source_manifest=dict(files=files,original_runtime_source_count=219,source_freeze_sha256=sha(Z/'reports/SOURCE_FREEZE.json'),asset_originals_unchanged=True,
 clock=dict(physics_dt_s=.001,control_dt_s=.01,decimation=10,force_bin_s=.005,force_history=3),
 inference='Actual actor-decision35 and5x35 history; no privileged label',allowed_windows_adapter=['RM_MOD4_USD'])
package=A/'clock1000-history219-frozen.zip';assert not package.exists()
with zipfile.ZipFile(str(package)+'.partial','w',compression=zipfile.ZIP_DEFLATED) as z:
 for p,n in payload:z.write(p,n)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(source_manifest,indent=2))
os.replace(str(package)+'.partial',package)
ready=json.loads((B/'reports/S1A_MATCHED_HISTORY_REVIEW_READY.json').read_text());rows={}
paths={'anchor':dict(path='/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-06_05-04-08_auto_0282_physical_dr_stage1_learning_cap12.5664_white_v3/model_23509.pt',sha256='2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a')}
paths.update({k:ready[k]['checkpoint'] for k in ('A0','A1','A2')})
for k,v in paths.items():
 p=Path(v['path']);assert sha(p)==v['sha256'];out=A/('clock1000-'+k+'-'+v['sha256']+'.pt');assert not out.exists()
 shutil.copyfile(p,out);assert sha(out)==v['sha256'];rows[k]=dict(path=str(out),original_path=str(p),bytes=out.stat().st_size,sha256=sha(out),architecture_variant='A0' if k=='anchor' else k)
proof=dict(epoch=time.time(),package=dict(path=str(package),bytes=package.stat().st_size,sha256=sha(package)),sources=rows,source_manifest=source_manifest,
 native_history_SDK=sdk,queue_published=False,new_learning=False,new_budget_seconds=0)
target.write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
'''
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=120)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode()
 v=json.loads(raw);(R/'CLOCK1000_PACKAGE_STAGED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 print(json.dumps(dict(epoch=v['epoch'],runtime_bytes=v['package']['bytes'],runtime_sha=v['package']['sha256'],weights={k:x['sha256'] for k,x in v['sources'].items()},queue_published=False)))
finally:c.close()
