from pathlib import Path
D=Path(__file__).resolve().parent
p=D/'collect_full80_frozen1500_readonly.py';s=p.read_text()
assert 'sf=c.open_sftp();copied=[];' in s
s=s.replace('sf=c.open_sftp();copied=[];','sf=c.open_sftp();sf.get_channel().settimeout(60);copied=[];')
a=s.index('  with sf.open(');b=s.index('  copied.append(',a)
old=s[a:b];assert 'hashlib.sha256(data).hexdigest()' in old and 'p.write_bytes(data)' in old
new="""  p=folder/row['relative'];p.parent.mkdir(parents=True,exist_ok=True)
  sf.get(row['path'].replace('\\\\','/'),str(p),max_concurrent_prefetch_requests=16)
  assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],row['path']
"""
s=s[:a]+new+s[b:];q=D/'collect_left_full80_bounded_transport_actual.py';assert not q.exists();compile(s,str(q),'exec');q.write_text(s,encoding='utf8');print(str(q))
