"""Metadata only. Do not import Torch, TensorDict, Isaac or CUDA."""
from pathlib import Path
import sys,time,json,importlib.metadata as m,importlib.util as u
R=Path(__file__).resolve().parent
p=R/'install_reports/BASE_PACKAGE_METADATA_CPU_ACTUAL.json'
assert not p.exists()
expected={'torch':'2.7.0+cu128','torchvision':'0.22.0+cu128','rsl-rl-lib':'5.0.1','tensordict':'0.12.3','warp-lang':'1.13.0','numpy':'1.26.0','scipy':'1.15.3','gymnasium':'1.2.1','isaacsim':'5.1.0.0'}
report=dict(epoch=time.time(),executable=sys.executable,python=sys.version,expected=expected,packages={},specs={},CPU_metadata_only_no_GPU_or_PhysX_or_PPO=True)
assert sys.version_info[:2]==(3,11)
for n,v in expected.items():
 d=m.distribution(n);assert d.version==v,(n,d.version,v)
 report['packages'][n]=dict(version=d.version,location=str(d.locate_file('')))
for n in ('isaacsim','torch','tensordict','warp','rsl_rl'):
 s=u.find_spec(n);assert s is not None,n
 report['specs'][n]=dict(origin=s.origin,search_locations=list(s.submodule_search_locations or []))
report['passed']=True
p.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
