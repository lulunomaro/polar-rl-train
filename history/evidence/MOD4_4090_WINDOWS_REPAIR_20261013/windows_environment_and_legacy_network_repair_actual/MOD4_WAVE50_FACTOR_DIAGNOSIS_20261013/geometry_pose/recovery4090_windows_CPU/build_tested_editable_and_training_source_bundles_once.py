"""Independent CPU ZIP capture of tested editable SDK and exact source459 assets.

Only creates new immutable files in this task. F:/installed source is readonly.
"""
from pathlib import Path
import json,hashlib,time,subprocess,zipfile,os,re
from importlib import metadata
import tomllib
D=Path(__file__).resolve().parent;W=D.parents[2];LAB=Path('F:/isaacsim/IsaacLab')
B=W/'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400'
RUN=B/'training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339'
def H(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for buf in iter(lambda:f.read(2**20),b''):h.update(buf)
 return h.hexdigest()
def byteH(b):return hashlib.sha256(b).hexdigest()
def capture(path,arc):
 p=Path(path);b=p.read_bytes()
 assert not re.search(br'-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----',b),str(p)
 return dict(source=str(p),archive=arc,bytes=len(b),sha256=byteH(b)),b
pkgs={'isaaclab':'0.54.4','isaaclab_rl':'0.5.2','isaaclab_assets':'0.2.4','isaaclab_tasks':'0.11.16'}
head=subprocess.check_output(['git','-C',str(LAB),'rev-parse','HEAD'],text=True).strip()
status=subprocess.check_output(['git','-C',str(LAB),'status','--porcelain','--',*[f'source/{n}' for n in pkgs]],text=True)
assert not status.strip(),status
Z=D/'TESTED_ISAACLAB_EDITABLE_FOURPKG_SOURCE_20261013.zip';M=D/'TESTED_ISAACLAB_EDITABLE_FOURPKG_SOURCE_20261013_MANIFEST.json'
assert not Z.exists() and not M.exists()
files=[];skip=[];versions=[]
with zipfile.ZipFile(Z,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for n,version in pkgs.items():
  root=LAB/'source'/n;actual=tomllib.loads((root/'config/extension.toml').read_text())['package']['version']
  assert actual==version==metadata.version(n)
  dist=metadata.distribution(n);versions.append(dict(package=n,version=version,editable_source=str(root),setup_sha256=H(root/'setup.py'),extension_toml_sha256=H(root/'config/extension.toml')))
  for directory,dirs,names in os.walk(root,followlinks=False):
   dirs[:]=[x for x in dirs if x not in ('.git','.ssh','__pycache__','.pytest_cache','.cache','build','dist') and not x.endswith('.egg-info') and not (Path(directory)/x).is_symlink()]
   for name in sorted(names):
    p=Path(directory)/name;rel=p.relative_to(root).as_posix()
    if p.is_symlink() or p.suffix.lower() in ('.pyc','.pyo','.dmp','.key','.pem','.usd','.usdc','.usda','.urdf','.mjcf','.pt','.pth','.ckpt','.npz','.npy','.mp4','.avi') or p.stat().st_size>4_000_000:
     skip.append(dict(source=str(p),bytes=p.stat().st_size,why='compiled/private/large unused binary asset excluded; not needed for MOD4 supplied robot/mesh'));continue
    r,b=capture(p,f'source/{n}/{rel}');files.append(r);archive.writestr(r['archive'],b)
  for name in ('METADATA','direct_url.json','WHEEL'):
   p=Path(dist._path)/name
   if p.exists():
    r,b=capture(p,f'installed_metadata_reference/{n}/{name}');files.append(r);archive.writestr(r['archive'],b)
 for name in ('LICENSE','LICENSE-mimic','VERSION'):
  p=LAB/name;r,b=capture(p,name);files.append(r);archive.writestr(name,b)
 manifest=dict(epoch=time.time(),Git_HEAD=head,package_scoped_git_clean=True,package_versions=versions,
  file_rows=files,excluded=skip,zip_layout='source/{isaaclab,isaaclab_rl,isaaclab_assets,isaaclab_tasks}; original setup/pyproject/config + licenses + installed metadata reference',
  installed_F_source_not_changed=True,no_git_ssh_credentials_pycache_or_large_unused_assets=True,not_GPU_or_training=True,
  remote_new_root='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013',
  recommended_editable_install='env/python.exe -m pip install --no-deps --no-build-isolation -e sdk_exact/source/isaaclab -e sdk_exact/source/isaaclab_rl -e sdk_exact/source/isaaclab_assets -e sdk_exact/source/isaaclab_tasks; tested native dependencies installed separately and version verified',
  metadata_direct_url_reference_is_original_F_not_remote_executable=True)
 archive.writestr('SOURCE_BUNDLE_MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf8'))
with zipfile.ZipFile(Z) as archive:
 for r in files:assert byteH(archive.read(r['archive']))==r['sha256']
manifest['zip']=dict(path=str(Z),bytes=Z.stat().st_size,sha256=H(Z));M.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(SDK_zip=manifest['zip'],files=len(files),excluded=len(skip),GitHEAD=head,manifest=str(M)),ensure_ascii=False),flush=True)

TZ=D/'SOURCE459_FULL_TRAINING_ASSETS_D05C_20261013.zip';TM=D/'SOURCE459_FULL_TRAINING_ASSETS_D05C_20261013_MANIFEST.json';assert not TZ.exists() and not TM.exists()
original=j=json.loads((B/'BACKUP_COMPLETE_BYTEEXACT.json').read_bytes());origmap={str(Path(x['local_path']).resolve()):x for x in original['files']}
selected=[]
for p in (RUN/'src_snapshot').rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:selected.append((p,'source459/src_snapshot/'+p.relative_to(RUN/'src_snapshot').as_posix()))
for p in (RUN/'e1_source_snapshot').rglob('*'):
 if p.is_file() and '__pycache__' not in p.parts:selected.append((p,'source459/e1_source_snapshot/'+p.relative_to(RUN/'e1_source_snapshot').as_posix()))
for name in ('run_manifest.json','rolling_source_freeze.json','latest_complete.json','CLOCK_TRAINING_HEALTH.json'):
 selected.append((RUN/name,'source459/provenance/'+name))
selected.append((RUN/'model_32264.pt','source459/checkpoint/model_32264_d05c.pt'))
for name in ('SOURCE_FREEZE.json','SOURCE_SELECTED.json','e1_WAVE50_episode_lifetime_observation_PASSED.json','e1_WAVE50_episode_lifetime_observation_SAVED_EXIT.json','REUSED_ACTUAL_CONTRACTS.json'):
 selected.append((B/'training/reports'/name,'source459/provenance/'+name))
training=[]
with zipfile.ZipFile(TZ,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
 for p,arc in selected:
  old=origmap[str(p.resolve())];r,b=capture(p,arc);assert r['bytes']==old['bytes'] and r['sha256']==old['sha256'];r['original_remote_path']=old['remote_path'];training.append(r);archive.writestr(arc,b)
 tm=dict(epoch=time.time(),source459_current_manifest696_verified_reference=str(D/'SOURCE459_AND_LOCAL91D_RECOVERY_CPU_CURRENT_ACTUAL.json'),source459_count=459,actual_module_snapshots=104,
  full_original_checkpoint=dict(path=str(RUN/'model_32264.pt'),bytes=19_043_064,sha256='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a',environment_count=20000,float_tensors=107),
  file_rows=training,original_source_and_assets_byteexact=True,old_large_raw_not_in_zip=True,
  original_459_raw_index=[x for x in original['files'] if x['backup_relative'].endswith('.npz') and ('evaluation/' in x['backup_relative'] or 'retention_prefix_' in x['backup_relative'])],
  original_backup696_metadata_reference=dict(path=str(B/'BACKUP_COMPLETE_BYTEEXACT.json'),bytes=(B/'BACKUP_COMPLETE_BYTEEXACT.json').stat().st_size,sha256=H(B/'BACKUP_COMPLETE_BYTEEXACT.json')),
  original_Linux_source_not_Windows_adapted=True,old_supervisor_main_resume_once_included_for_source_preservation_only_do_not_execute=True,
  canonical_budget_not_in_bundle_or_copied=True,credentials_not_in_bundle=True,no_GPU_no_OS_or_installed_source_changes=True)
 archive.writestr('TRAINING_ASSET_BUNDLE_MANIFEST.json',json.dumps(tm,ensure_ascii=False,indent=2).encode('utf8'))
with zipfile.ZipFile(TZ) as archive:
 for r in training:assert byteH(archive.read(r['archive']))==r['sha256']
tm['zip']=dict(path=str(TZ),bytes=TZ.stat().st_size,sha256=H(TZ));TM.write_text(json.dumps(tm,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(training_zip=tm['zip'],files=len(training),manifest=str(TM)),ensure_ascii=False),flush=True)
