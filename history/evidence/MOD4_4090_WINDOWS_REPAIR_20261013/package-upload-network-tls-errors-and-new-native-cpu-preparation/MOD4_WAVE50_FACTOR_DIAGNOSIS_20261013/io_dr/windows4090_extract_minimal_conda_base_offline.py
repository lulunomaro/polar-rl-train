from pathlib import Path
import zipfile,json,hashlib,time
R=Path(__file__).resolve().parent;p=R/'packages/TESTED_PYTHON311_CONDA_BASE_OFFLINE_20261013.zip'
assert p.stat().st_size==38019706 and hashlib.sha256(p.read_bytes()).hexdigest()=='6457345709b3db9799581d1001367924864d1d98a2f8120896df6b56e322eff0'
d=R/'offline_conda_base';assert not d.exists();d.mkdir()
with zipfile.ZipFile(p) as z:
 manifest=json.loads(z.read('CPU_PACKAGE_SOURCE_MANIFEST.json'))
 assert len(manifest['packages'])==20
 rows=[]
 for row in manifest['packages']:
  name=row['archive'];assert '/' not in name and '\\' not in name and ':' not in name
  b=z.read('conda_archives/'+name);assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'] and hashlib.md5(b).hexdigest()==row['md5']
  q=d/name
  with q.open('xb') as f:f.write(b)
  rows.append(dict(path=str(q),bytes=len(b),sha256=row['sha256'],md5=row['md5'],name=row['name'],version=row['version']))
explicit=R/'OFFLINE_PY311_BASE_EXPLICIT.txt';assert not explicit.exists()
explicit.write_text('@EXPLICIT\n'+'\n'.join(Path(x['path']).as_uri()+'#'+x['md5'] for x in rows)+'\n',encoding='utf8')
out=R/'install_reports/OFFLINE_PY311_BASE_EXTRACTED_CPU_ACTUAL.json';assert not out.exists()
out.write_text(json.dumps(dict(epoch=time.time(),passed20_archives_byteSHA=True,source_archive_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),packages=rows,explicit_file=str(explicit),no_oldenv_or_cache_modified=True,no_GPU_or_PPO=True),indent=2),encoding='utf8')
print(json.dumps(dict(report=str(out),packages=len(rows))))
