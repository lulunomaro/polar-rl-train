"""Narrow metadata-plane interpretation repair; frozen original220 stays unused."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert H(N/'INDEX220_FROZEN.json')=='6b0738b4fe9b564749855edd1d0233ef237969965b2ff4617132dad2cd49b525'
for r in json.loads((N/'INDEX220_FROZEN.json').read_bytes())['files']:assert H(r['path'])==r['SHA']
original=N/'evaluate220_NEW210_E0_mean_plane_flight_UNUSED_once.py'
assert H(original)=='b85b336719407137eb8625c90c7ab344a6515d0c312222a8f2262e1c52a25607'
s=original.read_text('utf8')
before="plane_z=float(cfg.scene.ground.init_state.pos[2])+.5*float(cfg.scene.ground.spawn.size[2]);assert plane_z==0."
after="""ground_spawn_name=getattr(cfg.scene.ground.spawn.func,'__name__','UNKNOWN')
 if ground_spawn_name=='spawn_local_native_plane':
  plane_z=float(cfg.scene.ground.init_state.pos[2])
 else:
  plane_z=float(cfg.scene.ground.init_state.pos[2])+.5*float(cfg.scene.ground.spawn.size[2])
 assert plane_z==0.,dict(spawn_function=ground_spawn_name,actual_top=plane_z)"""
assert s.count(before)==1;s=s.replace(before,after);ast.parse(s)
out=N/'ROOT220V2_SOURCE_PACKAGE';out.mkdir(exist_ok=False)
files=['prepare220_task_from_actual210_SELECTED_authority_UNUSED.py','target220_single_N1_parent_UNUSED.py',
 'evaluate220_NEW210_E0_mean_plane_flight_UNUSED_once.py','zonglin2_app_launcher.py',
 'source/contract220.py','source/wheel_geometry220.py','source/flight_evidence220.py']
rows=[]
for relative in files:
 data=s.encode('utf8')if relative==original.name else(N/relative).read_bytes()
 p=out/relative;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(data)
 rows.append(dict(relative=relative,bytes=len(data),SHA=H(p)))
runtime=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/package/payload/job0/runtime/isaac/mod4/mod4_task.py'
manifest=runtime.parents[3]/'original_run_manifest.json'
# Store the exact source branch and the actual original env proof, without SDK/assets.
text=runtime.read_text('utf8');anchor=text.index('if os.environ.get("RM_FLAT_NATIVE_PLANE"')
v=dict(epoch=time.time(),source_only_before_ANY220_SDK_or_model=True,
 original220_worker=str(original),original_SHA=H(original),original_still_UNUSED=True,
 selected_source_package=str(out),files=rows,
 physical_source=str(runtime),physical_source_SHA=H(runtime),
 native_plane_source=text[anchor:anchor+380],
 original_cube_size_is_not_physical_native_plane_height=True,
 change='Only compute plane top from actual native-plane spawn position; retain cuboid top for actual cuboid spawn.',
 no_reward_plant_parameters_or_guards_changed=True,old_fixture_replayed=False,
 model_raw_NPZ_USD_SDK_GPU_network_reads=0)
with(N/'reports/ROOT220V2_NATIVE_PLANE_METADATA_BEFORE_USE_REPAIR.json').open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(dict(source_repair=True,selected_source=str(out),worker_SHA=H(out/original.name))))
