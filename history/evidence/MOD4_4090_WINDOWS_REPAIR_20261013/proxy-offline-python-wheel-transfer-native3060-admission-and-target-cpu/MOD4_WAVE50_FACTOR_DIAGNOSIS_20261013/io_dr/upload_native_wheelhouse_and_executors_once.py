from pathlib import Path
import json,time,hashlib,sys,traceback
F=Path(__file__).resolve().parent;W=F.parents[1]
sys.path.insert(0,str(W/'MOD4_4090_WINDOWS_REPAIR_20261013'))
from windows4090_native_transport import connect,powershell,upload
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013'
proof=json.loads((F/'WINDOWS4090_TOPLEVEL_METADATA_REVIEWED_NATIVE311_WHEELHOUSE_CPU_ACTUAL.json').read_bytes());assert proof['complete']
items=[dict(local=proof['bundle']['path'],bytes=proof['bundle']['bytes'],sha256=proof['bundle']['sha256']),dict(local=str(W/'MOD4_4090_WINDOWS_REPAIR_20261013/repair_payload/WINDOWS4090_REPAIR_EXECUTABLES_CPU_PREPARED_FINAL.zip'),bytes=34304,sha256='02559b9a3238f1a411f1eb8aaf35eb43b4092f446f3eaf6599eb620c92a450cb')]
out=F/('WINDOWS4090_NATIVE_WHEELHOUSE_EXECUTORS_UPLOAD_ACTUAL_'+str(time.time_ns())+'.json');j=dict(epoch=time.time(),items=[],no_GPU_PPO=True,no_whole_existingenv_copy=True)
try:
 s=connect()
 for item in items:
  p=Path(item['local']);assert p.stat().st_size==item['bytes'];remote=R+'/packages/'+p.name
  pre=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();@{exists=Test-Path -LiteralPath '"+remote+"';free=(Get-PSDrive C).Free}|ConvertTo-Json",timeout=30));assert not pre['exists'],'unknown previous upload outcome: inspect SHA independently, never repeat once'
  guard=2*item['bytes']+2*1024**3;assert pre['free']>=guard
  entry=dict(**item,remote=remote,pre_actual=pre,guard_bytes=guard,guardpassed=True,start=time.time(),status='upload_in_progress');j['items'].append(entry);out.write_text(json.dumps(j,indent=2),encoding='utf8')
  upload(p,remote,timeout=600);entry['status']='uploaded_pending_remote_SHA';out.write_text(json.dumps(j,indent=2),encoding='utf8')
  actual=json.loads(powershell(s,"$OutputEncoding=[Console]::OutputEncoding=[Text.UTF8Encoding]::new();$p=Get-Item -LiteralPath '"+remote+"';@{path=$p.FullName;bytes=$p.Length;sha256=(Get-FileHash -LiteralPath $p.FullName -Algorithm SHA256).Hash.ToLower()}|ConvertTo-Json",timeout=60));assert actual['bytes']==item['bytes'] and actual['sha256']==item['sha256'];entry.update(status='remote_byte_SHA_actualexact',actual=actual,seconds=time.time()-entry['start']);out.write_text(json.dumps(j,indent=2),encoding='utf8')
 s.close();j['complete']=True;j['seconds']=time.time()-j['epoch'];out.write_text(json.dumps(j,indent=2),encoding='utf8');print(json.dumps(dict(report=str(out),actual=j),ensure_ascii=True))
except Exception as e:j.update(error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(),complete=False);out.write_text(json.dumps(j,indent=2),encoding='utf8');raise
