"""Exact fresh signed GUI identities only; unknown compute still rejected."""
from pathlib import Path
import json
import transport_249_exact_desktop_role_stdin_fresh2233_v7 as base
PY=base.PY;ROOT='D:/MOD4_async_eval/'+Path(__file__).resolve().parent.parent.name+'/'+Path(__file__).resolve().parent.name;connect=base.connect;close=base.close;py=base.py;ps=base.ps
def guard_code():
 base.base.ROOT=ROOT;s=base.guard_code();v=json.loads((Path(__file__).resolve().parent/'reports/E3_FROZEN_249_CHANGED_DESKTOP_EXACT_SIGNATURES_2145_READONLY_ACTUAL.json').read_bytes());expected={r['name']:{k:r[k] for k in ('process','parent','binary_SHA')} for r in v['exact_new_desktop_roles']};marker="  if name=='gameviewerserver.exe':";assert s.count(marker)==1
 insert="""  if name in FRESH_EXACT_SIGNED_DESKTOP:
   import hashlib
   def identity(p):return dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),parent=p.ppid())
   parent=process.parent()
   actual=dict(process=identity(process),parent=identity(parent) if parent else None,binary_SHA=hashlib.sha256(Path(exe).read_bytes()).hexdigest())
   assert actual==FRESH_EXACT_SIGNED_DESKTOP[name], 'Fresh signed desktop identity changed; unknown compute rejected'
   desktop.append(dict(pid=pid,creation=process.create_time(),exe=exe,role='Exact current OS-signature-verified desktop graphics/remote-control/browser bridge identity; untouched; not evaluation ownership or a general executable allowlist'))
  elif name=='gameviewerserver.exe':""".replace('FRESH_EXACT_SIGNED_DESKTOP',repr(expected))
 s=s.replace(marker,insert,1);compile(s,'<fresh exact signed desktop role guard>','exec');return s
