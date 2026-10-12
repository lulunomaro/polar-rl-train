"""Transfer new immutable reference and admit CPU/source/fixture before any replay."""
from scut_wave_io import *

def main():
    assert not (R/'TARGET_CPU_ADMITTED.json').exists()
    files=[D/x for x in ('reference_original.zip','exact_wave50_test.usda','actual_mod4_wave50_query.npz','FIXTURE.json','scut_wave50_placement_reviewed_probe.py','reference_coordinator_once.py')]
    manifest={p.name:dict(bytes=p.stat().st_size,sha256=H(p.read_bytes())) for p in files};save('REFERENCE_STAGE_STARTED.json',dict(epoch=time.time(),remote_root=REMOTE,files=manifest))
    w=connect()
    try:
        execute(w,"from pathlib import Path\nimport json\np=Path("+repr(REMOTE)+");assert not p.exists();p.mkdir();print(json.dumps(dict(newroot_created=True)))")
        with w.open_sftp() as f:
            for p in files:
                with f.open(REMOTE+'/'+p.name,'wbx') as out:out.write(p.read_bytes())
        code=r'''from pathlib import Path
import json,hashlib,zipfile,torch,numpy as np,shutil,time
D=Path(ROOT_TOKEN);manifest=MANIFEST_TOKEN;h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,row in manifest.items():assert (D/name).stat().st_size==row['bytes'] and h(D/name)==row['sha256']
assert shutil.disk_usage(D).free>2*(200000000)+2*1024**3
with zipfile.ZipFile(D/'reference_original.zip') as z:
 for x in z.infolist():assert (D/'original'/x.filename).resolve().is_relative_to((D/'original').resolve()) and not x.filename.startswith(('/', '\\')) and (x.external_attr>>16)&0o170000!=0o120000
 z.extractall(D/'original')
source=json.loads((D/'original/SOURCE_MANIFEST.json').read_bytes());assert source['commit']=='b8ff79f3df855faf9dc92f4a282bd80c42649466'
for name,row in source['files'].items():assert h(D/'original'/name)==row['sha256'] and (D/'original'/name).stat().st_size==row['bytes']
models=[]
for name in source['models']:
 p=D/'original'/name/'model_1000.pt';s=torch.load(p,map_location='cpu',weights_only=False);assert 'model_state_dict' in s and 'optimizer_state_dict' in s
 tensors=[]
 def walk(v):
  if torch.is_tensor(v):
   if v.is_floating_point():assert torch.isfinite(v).all();tensors.append(v)
  elif isinstance(v,dict):
   for x in v.values():walk(x)
  elif isinstance(v,(tuple,list)):
   for x in v:walk(x)
 walk(s);actor={k:v for k,v in s['model_state_dict'].items() if k.startswith('actor.')};assert actor['actor.0.weight'].shape[1]==35 and actor['actor.6.weight'].shape[0]==6
 models.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),iteration=int(s['iter']),finite_tensors=len(tensors),actor_shapes={k:list(v.shape) for k,v in actor.items()}))
fixture=json.loads((D/'FIXTURE.json').read_bytes());assert fixture['seconds']==15 and fixture['approach_m']==.4 and fixture['after_m']==.2 and len(fixture['centers'])==80 and fixture['mesh_SHA']==h(D/fixture['mesh_file'])
with np.load(D/'actual_mod4_wave50_query.npz',allow_pickle=False) as z:
 tri=z['world_triangles'];assert tri.dtype==np.float32 and hashlib.sha256(tri.tobytes()).hexdigest()==fixture['actual80cells_triangle_f32_byte_SHA'] and np.isfinite(tri).all()
for name in ('scut_wave50_placement_reviewed_probe.py','reference_coordinator_once.py'):compile((D/name).read_bytes(),name,'exec')
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,models=models,source_files_verified=len(source['files']),fixture_actual80worldtriangles_and_profile_source_exact=True,native_SCUT_5msx4_50Hz_and_original_DR_preserved=True,probe_coordinator_AST_passed=True,no_GPU_yet_launched=True,no_4090_PPO_or_budget_write=True,remote_root=str(D),stage_files=manifest)
p=D/'TARGET_CPU_ADMITTED.json';assert not p.exists();p.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('ROOT_TOKEN',repr(REMOTE)).replace('MANIFEST_TOKEN',repr(manifest))
        v=execute(w,code);save('TARGET_CPU_ADMITTED.json',v);print(json.dumps(dict(passed=True,models=[dict(sha256=x['sha256'],iteration=x['iteration'],finite_tensors=x['finite_tensors']) for x in v['models']],source_files=v['source_files_verified'],no_GPU_yet=True)))
    finally:w.close()

if __name__=='__main__':
    try:main()
    except BaseException:save('SCUT_TARGET_CPU_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),original_partial_evidence_retained=True,no_GPU_replay=True));raise
