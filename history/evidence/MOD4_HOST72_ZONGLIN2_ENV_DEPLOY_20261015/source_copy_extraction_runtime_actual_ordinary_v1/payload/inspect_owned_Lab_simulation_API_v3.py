from pathlib import Path
import hashlib,json,time
r=Path('/home/lc01/Zonglin Li/zonglin2');lab=r/'src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab';s=r/'envs/mod4/lib/python3.12/site-packages/isaacsim'
paths=[lab/'sim/simulation_context.py',lab/'sim/simulation_cfg.py',lab/'sim/__init__.py',lab/'app/app_launcher.py']
for folder in ('exts','extscache','extsPhysics','extsDeprecated'):
 paths+=list((s/folder).glob('isaacsim.core.simulation_manager*/isaacsim/core/simulation_manager/simulation_manager.py'))
v=dict(epoch=time.time(),files=[],no_SDK_import_GPU_PPO_or_source_mutation=True)
for p in sorted(set(paths)):
 if p.is_file():
  b=p.read_bytes();v['files'].append(dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),text=b.decode(errors='replace')))
with (r/'audit/OWNED_LAB_SIMULATION_API_V3_READONLY.json').open('x') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(files=len(v['files']),paths=[x['path'] for x in v['files']])),flush=True)
