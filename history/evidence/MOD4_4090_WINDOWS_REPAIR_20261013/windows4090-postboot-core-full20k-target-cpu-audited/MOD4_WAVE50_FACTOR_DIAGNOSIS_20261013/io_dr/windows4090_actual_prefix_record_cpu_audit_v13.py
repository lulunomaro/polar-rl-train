"""Metadata/RECORD read-only audit; no installed module imports or GPU init."""
from pathlib import Path
import sys,time,json,hashlib,base64,csv,importlib.metadata as md,os
R=Path(__file__).resolve().parent;Prefix=R/'env';out=R/'install_reports'/('PREFIX_INSTALLED_ARTIFACT_RECORD_CPU_ACTUAL_'+str(time.time_ns())+'.json')
assert Path(sys.executable).resolve()==(Prefix/'python.exe').resolve()
pins=R/'ACTUAL_NATIVE311_FULL_WHEELHOUSE_PINS.txt';wanted={}
for line in pins.read_text(encoding='utf8').splitlines():
 n,v=line.split(' --hash=')[0].split('==');wanted[n]=v
report=dict(epoch=time.time(),python=sys.executable,version=sys.version,no_Torch_Isaac_CUDA_GPU_import_or_install=True,canonical_or_oldenv_untouched=True,packages=[],fully_exact=[],missing_or_wrong=[],no_inference_from_old_task_STARTED=True)
def file_digest(p,mode):
 h=hashlib.new(mode)
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return base64.urlsafe_b64encode(h.digest()).decode().rstrip('=')
for name,expected in sorted(wanted.items()):
 try:d=md.distribution(name)
 except md.PackageNotFoundError:
  r=dict(name=name,expected_version=expected,installed=False,full_exact=False);report['packages'].append(r);report['missing_or_wrong'].append(name);continue
 r=dict(name=name,expected_version=expected,actual_version=d.version,metadata_path=str(d._path),metadata_within_own_prefix=Path(d._path).resolve().is_relative_to(Prefix.resolve()),hashed_files=0,unhashed_declared=0,errors=[])
 if d.version!=expected:r['errors'].append(dict(error='actual installed version mismatch'))
 if not r['metadata_within_own_prefix']:r['errors'].append(dict(error='external environment metadata'))
 record=d.read_text('RECORD')
 if record is None:r['errors'].append(dict(error='actual installed RECORD absent'))
 else:
  for rel,digest,size in csv.reader(record.splitlines()):
   p=Path(d.locate_file(rel)).resolve()
   if not p.is_relative_to(Prefix.resolve()):r['errors'].append(dict(path=str(p),error='RECORD path outside ownprefix'));continue
   if not digest:r['unhashed_declared']+=1;continue
   if not p.is_file():r['errors'].append(dict(path=str(p),error='hashed RECORD artifact missing'));continue
   mode,value=digest.split('=',1)
   if size and p.stat().st_size!=int(size):r['errors'].append(dict(path=str(p),error='actual size mismatch'));continue
   got=file_digest(p,mode)
   if got!=value:r['errors'].append(dict(path=str(p),error='actual RECORD hash mismatch',algorithm=mode,expected=value,actual=got));continue
   r['hashed_files']+=1
 r['full_exact']=not r['errors'] and r['hashed_files']>0
 report['packages'].append(r);report['fully_exact' if r['full_exact'] else 'missing_or_wrong'].append(name)
report['actual_fully_exact_count']=len(report['fully_exact']);report['actual_missing_or_wrong_count']=len(report['missing_or_wrong']);report['all_expected_artifacts_exact']=not report['missing_or_wrong']
out.write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),fully_exact=report['fully_exact'],missing_or_wrong=report['missing_or_wrong'],full_environment_not_claimed=True),ensure_ascii=True))
