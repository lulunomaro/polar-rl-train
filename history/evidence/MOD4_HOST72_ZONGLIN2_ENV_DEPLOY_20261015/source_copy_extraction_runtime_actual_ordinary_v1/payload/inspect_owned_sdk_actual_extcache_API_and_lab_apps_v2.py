from pathlib import Path
import hashlib,json,time
r=Path('/home/lc01/Zonglin Li/zonglin2');s=r/'envs/mod4/lib/python3.12/site-packages/isaacsim'
paths=[s/'apps/isaacsim.exp.base.kit']
for folder in ('exts','extscache','extsDeprecated'):
 for pat in ('isaacsim.core.api*/isaacsim/core/api/world/world.py','isaacsim.core.simulation_manager*/isaacsim/core/simulation_manager/simulation_manager.py','isaacsim.core.experimental.utils*/isaacsim/core/experimental/utils/app.py'):
  paths+=list((s/folder).glob(pat))
lab=r/'src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1'
paths+=list((lab/'apps').glob('*.kit'))
v=dict(epoch=time.time(),files=[],no_SDK_import_GPU_PPO_delete_or_installed_source_mutation=True)
for p in sorted(set(paths)):
 if not p.is_file():continue
 b=p.read_bytes();v['files'].append(dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),text=b.decode(errors='replace') if len(b)<250000 else None))
with (r/'audit/SDK_ACTUAL_EXTCACHE_API_AND_LAB_APPS_V2_READONLY.json').open('x') as f:json.dump(v,f,indent=2)
print(json.dumps(dict(files=len(v['files']),paths=[x['path'] for x in v['files']])),flush=True)
