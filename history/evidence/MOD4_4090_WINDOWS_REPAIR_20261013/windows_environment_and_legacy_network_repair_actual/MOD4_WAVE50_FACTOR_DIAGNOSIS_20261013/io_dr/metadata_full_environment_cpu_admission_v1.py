from pathlib import Path
import sys,json,time,hashlib,importlib.metadata as m,importlib.util as u
R=Path(__file__).resolve().parent
expected={'isaacsim':'5.1.0.0','isaaclab':'0.54.4','isaaclab_rl':'0.5.2','isaaclab_assets':'0.2.4','isaaclab_tasks':'0.11.16','torch':'2.7.0+cu128','torchvision':'0.22.0+cu128','rsl-rl-lib':'5.0.1','tensordict':'0.12.3','warp-lang':'1.13.0','numpy':'1.26.0','scipy':'1.15.3','gymnasium':'1.2.1','psutil':'5.9.8'}
out=R/'install_reports/FULL_WINDOWS4090_ENV_METADATA_CPU_ADMITTED.json';assert not out.exists()
assert sys.version_info[:2]==(3,11)
report=dict(epoch=time.time(),python=sys.version,executable=sys.executable,expected=expected,packages={},top_specs={},no_Isaac_Torch_CUDA_or_GPU_import=True,GPU_admission_or_PPO_not_claimed=True)
for n,v in expected.items():
 d=m.distribution(n);assert d.version==v,(n,d.version,v)
 report['packages'][n]=dict(version=d.version,location=str(d.locate_file('')))
for n in ('isaaclab','isaaclab_rl','isaaclab_assets','isaaclab_tasks'):
 s=u.find_spec(n);assert s is not None,n
 expected_source=R/'sdk_exact/source'/n/n
 assert Path(s.origin).resolve().is_relative_to(expected_source.resolve()),(n,s.origin,expected_source)
 report['top_specs'][n]=dict(origin=s.origin,search_locations=list(s.submodule_search_locations or []),own_exact_source_binding=True)
report['packages_metadata_CPU_passed']=True
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report))
