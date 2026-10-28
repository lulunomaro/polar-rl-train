"""Local source-only check. Never imports bootstrap/service or opens a socket."""
from pathlib import Path
import ast,hashlib,hmac,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
SERVICE=B/'owned_bundle_only_TLS_memfd_service_v1.py'
ENTRY=B/'bootstrap_source_TLS_then86_ten_second_probe_stdin_UNUSED_once_v1.py'

def put(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2)

def main():
 R.mkdir(exist_ok=True)
 service_raw=SERVICE.read_bytes();entry_raw=ENTRY.read_bytes()
 st=ast.parse(service_raw);et=ast.parse(entry_raw)
 compile(st,str(SERVICE),'exec');compile(et,str(ENTRY),'exec')
 embedded={}
 for n in ast.walk(et):
  if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):
   names=[x.id for x in n.targets if isinstance(x,ast.Name)]
   if len(names)==1 and names[0] in {'PROBE','guard','launch','stop'}:
    embedded[names[0]]=n.value.value
 assert set(embedded)=={'PROBE','guard','launch','stop'}
 for name,code in embedded.items():compile(ast.parse(code),'<embedded '+name+'>','exec')
 launch_tree=ast.parse(embedded['launch'])
 writes=[n for n in ast.walk(launch_tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='write']
 assert len(writes)==1
 newline_constants=[n.value for n in ast.walk(writes[0]) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
 assert '\n' in newline_constants and '\\n' not in newline_constants
 service_message=next(n.value for n in ast.walk(st) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='message' for x in n.targets))
 probe_tree=ast.parse(embedded['PROBE'])
 probe_message=next(n.value for n in ast.walk(probe_tree) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='message' for x in n.targets))
 class Request:pass
 req=Request();req.path='/probe'
 producer='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36'
 public_fixture=dict(expires='2000000000',nonce='0'*32)
 a=eval(compile(ast.Expression(service_message),'<service message>','eval'),dict(self=req,rangevalue='',PRODUCER=producer,**public_fixture))
 b=eval(compile(ast.Expression(probe_message),'<probe message>','eval'),dict(v={'producer_SHA':producer},**public_fixture))
 assert a==b=='GET\n/probe\n\n2000000000\n'+'0'*32+'\n'+producer
 fixture_key=bytes(range(32));signature=hmac.new(fixture_key,a.encode(),hashlib.sha256).hexdigest()
 assert hmac.compare_digest(signature,hmac.new(fixture_key,b.encode(),hashlib.sha256).hexdigest())
 assert not hmac.compare_digest(signature,hmac.new(fixture_key,b.replace('/probe','/chunk0001').encode(),hashlib.sha256).hexdigest())
 report=dict(epoch=time.time(),passed_source_AST_and_offline_HMAC_only=True,source_modules_compiled_without_import=True,embedded_AST=list(embedded),child_STDIN_separator_exact_byte10=True,HMAC_service_and_probe_message_equal=True,changed_route_HMAC_rejected_offline=True,no_network_or_secret_ingress_or_source_service_started=True,no_GPU_SDK_model_or_canonical_IO=True,not_actual_route_or_transfer_or_SDK_ready=True,service_SHA=hashlib.sha256(service_raw).hexdigest(),entry_SHA=hashlib.sha256(entry_raw).hexdigest())
 put(R/'DIRECT_TLS_SOURCE_AST_OFFLINE_HMAC_ACTUAL.json',report)
 files=[]
 for p in sorted(B.rglob('*')):
  if p.is_file() and p.name!='FROZEN_DIRECT_TLS_PROBE_SOURCE_INDEX_V1.json':
   raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),source_or_tiny_report_only=True))
 put(B/'FROZEN_DIRECT_TLS_PROBE_SOURCE_INDEX_V1.json',dict(epoch=time.time(),status='FROZEN_SOURCE_ONLY_UNUSED_NETWORK',entry=str(ENTRY),entry_SHA=report['entry_SHA'],service_SHA=report['service_SHA'],files=files,source_service_original_maximum_seconds=1800,known_target_to_source_probe_hard_seconds=10,control_maximum_seconds_after_single_secret_STDIN=180,no_execution_authorized_by_this_index=True,ordinary_Git_pending_root=False if False else 'root ordinary supplement pending'))
 print(json.dumps(report))

if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);put(R/('SOURCE_AST_FREEZE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_network=True));raise
