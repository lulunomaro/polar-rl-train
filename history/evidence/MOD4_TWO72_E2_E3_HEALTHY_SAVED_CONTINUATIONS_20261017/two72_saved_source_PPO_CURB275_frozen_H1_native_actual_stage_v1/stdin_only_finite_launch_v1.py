"""Future finite launches: capability only in SSH stdin and child's stdin, never argv."""
import json
def launch(code,c,py,root,entry,cfg):
 source="from pathlib import Path;import sys,json,subprocess;B=Path("+repr(root)+");cfg="+repr(json.dumps(cfg))+";assert not (B/(json.loads(cfg)['role']+'_CONSOLE.log')).exists();p=subprocess.run(["+repr(py)+",'-u','-B',str(B/"+repr(entry)+")],input=cfg+chr(10),text=True,capture_output=True,cwd=B,timeout=30);assert p.returncode==0,p.stderr;print(p.stdout)"
 return code(c,py,source)
