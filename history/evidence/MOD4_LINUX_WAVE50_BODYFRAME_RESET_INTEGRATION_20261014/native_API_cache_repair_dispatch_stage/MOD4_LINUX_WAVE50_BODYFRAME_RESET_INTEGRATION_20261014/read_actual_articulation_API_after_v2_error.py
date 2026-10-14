"""Read installed source after own natural exit; do not initialize an engine."""
import json,time,traceback
import transport_bodyframe_pipeline_v2 as t

CODE=r'''
from pathlib import Path
import json,subprocess,hashlib,shutil,psutil,fcntl
root=Path(CONTEXT['root']);row=json.loads((root/'ROOT_UNIQUE_DISPATCH_ACTUAL.json').read_bytes())
try:assert psutil.Process(row['pid']).create_time()!=row['created']
except psutil.NoSuchProcess:pass
out=[]
bases=['/home/egde/anaconda3/envs/fangzhen-isaaclab/lib/python3.12/site-packages/isaacsim','/home/egde/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source']
for base in bases:
 if not Path(base).is_dir():continue
 p=subprocess.run(['rg','-l','-g','*.py','class ArticulationView|def root_link_pose_w|def root_state_w',base],capture_output=True,text=True,timeout=40)
 for name in p.stdout.splitlines()[:30]:
  q=Path(name);text=q.read_text(errors='replace');lines=text.splitlines();hits=[]
  for i,line in enumerate(lines):
   if 'def get_root_transforms' in line or 'def get_transforms' in line or 'def root_link_pose_w' in line or 'def root_state_w' in line:
    hits.append(dict(line=i+1,source='\n'.join(lines[i:i+45])))
  out.append(dict(path=name,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),hits=hits))
attempt=root/'native144/attempt';folders=list((attempt/'learning_logs').glob('*'))
proofs=[]
for folder in folders:
 if folder.is_dir():
  for p in folder.glob('*STARTUP*VERIFIED.json'):proofs.append(dict(name=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),value=json.loads(p.read_bytes())))
print(json.dumps(dict(actual_installed_sources=out,original_startup_proofs=proofs,read_only_no_Kit_GPU_or_budget=True)))
'''

c=None
try:
 c=t.connect();value,p=t.run(c,CODE,dict(root=t.ROOT),'ARTICULATION_ACTUAL_INSTALLED_SOURCE_AND_13_PROOFS',timeout=120)
 print(json.dumps(dict(report=str(p),files=[dict(path=x['path'],hits=x['hits']) for x in value['actual_installed_sources']],original13_count=len(value['original_startup_proofs']))))
finally:t.close(c)
