"""Build a self-contained release ZIP and full file checksum manifest."""
from pathlib import Path
import zipfile,hashlib,json
B=Path(__file__).resolve().parents[1];dest=B.parent/(B.name+'.zip')
files=[p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.partial','.obj','.exp') and p.name!='SHA256SUMS.txt'];files.sort()
(B/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(B).as_posix()+'\n' for p in files),encoding='utf-8');files.append(B/'SHA256SUMS.txt')
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:
  name=B.name+'/'+p.relative_to(B).as_posix();info=zipfile.ZipInfo.from_file(p,name);info.create_system=3;info.external_attr=((0o100755 if p.parent.name=='linux-x64' else 0o100644)<<16);info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
print(json.dumps(dict(archive=str(dest),bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),files=len(files)),ensure_ascii=False))
