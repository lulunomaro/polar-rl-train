import hashlib, pathlib, re, tarfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
PKG=ROOT/'MOD4_RL_FIX_20260913_1500'
files=sorted(p for p in PKG.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
patterns=[re.compile(rb'gh[pousr]_[A-Za-z0-9]{25,}'),re.compile(rb'-----BEGIN (?:OPENSSH|RSA|EC) PRIVATE KEY-----')]
for p in files:
 if any(r.search(p.read_bytes()) for r in patterns):raise ValueError('credential pattern detected in '+str(p))
lines=[]
for p in files:
 if p.name=='SHA256SUMS':continue
 lines.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(PKG).as_posix())
(PKG/'SHA256SUMS').write_text('\n'.join(lines)+'\n',encoding='utf8')
out=ROOT/(PKG.name+'.tar.gz')
with tarfile.open(out,'w:gz') as tf:
 for p in sorted(PKG.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
  tf.add(p,arcname=PKG.name+'/'+p.relative_to(PKG).as_posix(),recursive=False)
print('ARCHIVE='+str(out))
print('BYTES='+str(out.stat().st_size))
print('SHA256='+hashlib.sha256(out.read_bytes()).hexdigest())
