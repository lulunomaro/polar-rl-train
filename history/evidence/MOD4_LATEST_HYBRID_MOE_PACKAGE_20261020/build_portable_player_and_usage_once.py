"""Build a self-contained relocatable delivery without modifying the user's existing player."""
from pathlib import Path
import ast,hashlib,importlib.metadata as md,json,shutil,sys,time,traceback,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parent;W=B.parent;D=W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008';P=B/'delivery/MOD4_HybridMoE_20261020';R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def write(path,text):
 with path.open('x',encoding='utf8',newline='\n') as f:f.write(text)
def main():
 export=json.loads((R/'LATEST_CLOSED_HYBRID_MOE_EXPORT_AND_ROUTING_CPU_ACTUAL.json').read_bytes());assert export['passed'];player=P/'player';player.mkdir();before={};copies=[]
 for name in ('sim_runtime.py','policy_runtime.py','current_sim.py','current_moe_sim.py','rm7v7_moe_sim.py','drive_rm7v7_moe.py','player_status_io.py','player_camera.py','runtime_config.json'):
  before[name]=H(D/name);shutil.copy2(D/name,player/name);copies.append(name)
 # Changes are only to package copies: bundle/route location and displayed source label.
 sim=player/'rm7v7_moe_sim.py';s=sim.read_text('utf8').replace("D.parent/'rmuc2026_training/data/routes.json'","D/'routes.json'").replace("D/'latest_moe_scut_fudan_hour7_20261019.json'","D.parent/'policy/manifest.json'").replace("D/'latest_moe_scut_fudan_hour7_20261019.onnx'","D.parent/'policy/hybrid_moe.onnx'").replace("self.delivery['onnx_sha256']","self.delivery['onnx_SHA']");ast.parse(s);sim.write_text(s,encoding='utf8',newline='\n')
 driver=player/'drive_rm7v7_moe.py';s=driver.read_text('utf8').replace('SCUT+Fudan 第七小时完整 H1跳跃 / E2自旋 / E3恢复 + 原 E0/W35门控','最新完整源 H1第16小时 / E2第17小时 / E3第17小时 + 原 E0/W35门控');ast.parse(s);driver.write_text(s,encoding='utf8',newline='\n')
 (player/'src_snapshot').mkdir()
 for name in ('reset_bank.json','import_contract.json'):shutil.copy2(D/'src_snapshot'/name,player/'src_snapshot'/name)
 shutil.copy2(W/'rmuc2026_training/data/routes.json',player/'routes.json')
 # Copy just the meshes actually named by the original full-map XML.
 tree=ET.parse(D/'rm7v7_latest_moe.xml');root=tree.getroot();compiler=root.find('compiler');meshdir=Path(compiler.get('meshdir'));compiler.set('meshdir','.');assets=[]
 for element in root.iter():
  file=element.get('file')
  if file is None:continue
  assert element.tag=='mesh';src=Path(file)
  if not src.is_absolute():src=meshdir/src
  src=src.resolve();assert src.is_file() and src.is_relative_to(W)
  kind='field' if src.is_relative_to((D/'rm7v7_assets_20261018').resolve()) else 'robot';target=player/'assets'/kind/src.name;target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copy2(src,target)
  assert H(target)==H(src);element.set('file',target.relative_to(player).as_posix());assets.append(dict(source_path=str(src),package_path=target.relative_to(P).as_posix(),bytes=target.stat().st_size,SHA=H(target)))
 tree.write(player/'rm7v7_latest_moe.xml',encoding='utf-8',xml_declaration=True)
 versions={n:md.version(n) for n in ('numpy','onnxruntime','mujoco')};write(P/'requirements.txt','\n'.join(n+'=='+v for n,v in versions.items())+'\n')
 write(P/'SETUP_WINDOWS.bat',r'''@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto install
py -3.12 -m venv ".venv"
if errorlevel 1 goto failed
:install
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -c "import tkinter,mujoco,onnxruntime,numpy;print('Environment OK')"
if errorlevel 1 goto failed
echo Setup complete. Run START_WINDOWS.bat.
pause
exit /b 0
:failed
echo Setup failed. Install Python 3.12 x64 with Tcl/Tk and launcher, then retry.
pause
exit /b 1
'''.replace('\\"','"'))
 write(P/'START_WINDOWS.bat',r'''@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Run SETUP_WINDOWS.bat first.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -B -X utf8 "player\drive_rm7v7_moe.py"
if errorlevel 1 pause
'''.replace('\\"','"'))
 write(P/'CHECK_PACKAGE_WINDOWS.bat',r'''@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Run SETUP_WINDOWS.bat first.
 pause
 exit /b 1
)
".venv\Scripts\python.exe" -B -X utf8 "check_package.py"
pause
'''.replace('\\"','"'))
 write(P/'infer.py','''"""Minimal combined ONNX inference, without PyTorch or a GUI."""
from pathlib import Path
import hashlib,json
import numpy as np
import onnxruntime as ort
ROOT=Path(__file__).resolve().parent
class HybridMoE:
 def __init__(self):
  path=ROOT/'policy/hybrid_moe.onnx';m=json.loads((ROOT/'policy/manifest.json').read_text('utf8'));assert hashlib.sha256(path.read_bytes()).hexdigest()==m['onnx_SHA'];self.session=ort.InferenceSession(str(path),providers=['CPUExecutionProvider'])
 def __call__(self,obs):
  x=np.asarray(obs,dtype=np.float32)
  if x.ndim==1:x=x[None,:]
  if x.ndim!=2 or x.shape[1]!=35 or not np.isfinite(x).all():raise ValueError('Expected finite float32 [batch,35] observation')
  if not np.all((x[:,28:35]==0)|(x[:,28:35]==1)) or not np.all(x[:,28:35].sum(axis=1)==1):raise ValueError('Mode must be exactly one-hot')
  y=self.session.run(['action'],{'observation':x})[0]
  if y.shape!=(len(x),6) or not np.isfinite(y).all():raise ValueError('Invalid action')
  return y
if __name__=='__main__':
 x=np.zeros(35,dtype=np.float32);x[3]=1.25;x[9]=-1;x[28]=1
 print(json.dumps(dict(action=HybridMoE()(x).tolist(),sample_only=True),indent=2))
''')
 write(P/'check_package.py','''"""Verify delivered files and a small inference; no GUI or training."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
def main():
 m=json.loads((ROOT/'PACKAGE_MANIFEST.json').read_text('utf8'))
 for r in m['files']:
  p=ROOT/r['path'];assert p.resolve().is_relative_to(ROOT.resolve());assert p.is_file() and p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'],r['path']
 from infer import HybridMoE
 import numpy as np
 x=np.zeros((4,35),dtype=np.float32);x[:,3]=1.25;x[:,9]=-1;x[np.arange(4),28+np.array([0,4,3,6])]=1;y=HybridMoE()(x);assert y.shape==(4,6)
 print(json.dumps(dict(files_verified=len(m['files']),inference='PASS',source_hours={'H1':16,'E2':17,'E3':17},not_skill_qualification=True),indent=2))
if __name__=='__main__':main()
''')
 assert all(H(D/name)==digest for name,digest in before.items())
 out=dict(epoch=time.time(),passed=True,package_root=str(P),portable_mesh_files=assets,all_mesh_bytes_exact=True,XML_changes_only_meshdir_and_file_paths=True,original_player_file_SHA=before,original_player_unchanged=True,package_only_changes=['policy and route relative paths','source label','relative mesh assets','new setup/inference/check/docs files'],runtime_config_unchanged=H(player/'runtime_config.json')==H(D/'runtime_config.json'),camera_status_fixes_exact=all(H(player/n)==H(D/n) for n in ('player_camera.py','player_status_io.py')),tested_dependency_versions=versions,python_version=sys.version,no_installed_env_or_old_logs_or_checkpoint_optimizer_in_package=True)
 put('PORTABLE_PLAYER_ASSETS_AND_RELATIVE_PATH_BUILD_ACTUAL.json',out);print(json.dumps(dict(portable_player_built=True,meshes=len(assets),asset_bytes=sum(x['bytes'] for x in assets),original_player_untouched=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('PORTABLE_PACKAGE_BUILD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),original_player_not_modified=True));raise
