from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'MOD4_3060_LINUX_RESUME_REFERENCE_20261014'))
import transport_249_only as base
PY=base.PY;ROOT='D:/MOD4_async_eval/MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'
connect=base.connect;close=base.close;py=base.py;ps=base.ps

def guard_code():
    base.ROOT=ROOT;s=base.guard_code()
    old="  if name not in allowed_names:unknown.append(dict(pid=pid,exe=exe))"
    assert s.count(old)==1
    new="  if name=='gameviewerserver.exe':\n   assert pid==9272 and process.create_time()==1791859314.9767294\n   assert Path(exe).as_posix().casefold()=='C:/Program Files/Netease/GameViewer/bin/GameViewerServer.exe'.casefold()\n   children=process.children(recursive=True)\n   assert all(c.name().lower()=='crashpad_handler.exe' and Path(c.exe()).as_posix().casefold()=='C:/Program Files/Netease/GameViewer/bin/crashpad_handler.exe'.casefold() for c in children)\n   desktop.append(dict(pid=pid,creation=process.create_time(),exe=exe,role='Actual authenticated NetEase signed remote desktop service; GPU graphics/encoding, no evaluation ownership; preserved untouched'))\n  elif name not in allowed_names:unknown.append(dict(pid=pid,exe=exe))"
    s=s.replace(old,new);compile(s,'<exact signed remote desktop role guard>','exec');return s
