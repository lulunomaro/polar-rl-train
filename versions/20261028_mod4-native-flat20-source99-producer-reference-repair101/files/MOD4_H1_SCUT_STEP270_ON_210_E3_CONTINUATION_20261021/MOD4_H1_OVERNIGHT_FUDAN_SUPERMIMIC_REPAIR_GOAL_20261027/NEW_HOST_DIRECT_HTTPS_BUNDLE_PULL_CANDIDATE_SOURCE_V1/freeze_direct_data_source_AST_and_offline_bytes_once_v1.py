"""Local source-only checks. Never import the runtime modules or use sockets."""
from pathlib import Path
import ast,hashlib,hmac,json,re,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent
SERVICE=B/'owned_bundle_only_TLS_Range_data_service_candidate_v1.py';WORKER=B/'target86_owned_direct_HTTPS_pull_candidate_v1.py';ENTRY=B/'bootstrap_probed_direct_HTTPS_all29_foreground_pull_stdin_UNUSED_once_v1.py'
PROBE=L/'NEW_HOST_DIRECT_HTTPS_BUNDLE_PROBE_SOURCE_V1/reports/DIRECT_TLS_HMAC_ROUTE_PROBE_COMPLETE_RETURNED_ACTUAL.json';PROBE_SHA='33c7566c392a9bb36c8cda476b1682457e23c7a3990bc824c0237c52c26ae670'

def put(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2)

def message(tree):return next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='message' for x in n.targets))

def main():
 R.mkdir(exist_ok=True);trees={}
 for p in [SERVICE,WORKER,ENTRY]:
  tree=ast.parse(p.read_bytes());compile(tree,str(p),'exec');trees[p]=tree
 embedded={}
 for n in ast.walk(trees[ENTRY]):
  if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):
   names=[x.id for x in n.targets if isinstance(x,ast.Name)]
   if len(names)==1 and names[0] in {'SOURCE_PRE','SOURCE_START','TARGET_PRE','TARGET_VERIFY','COLLECT_OWN_TEXT','SOURCE_STOP'}:embedded[names[0]]=n.value.value
 assert len(embedded)==6
 for name,code in embedded.items():compile(ast.parse(code),'<embedded '+name+'>','exec')
 start=ast.parse(embedded['SOURCE_START']);assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='chr' and n.args[0].value==10 for n in ast.walk(start))
 producer='c0d830df0635917f199f3c5e3a3498b7934eb57355dfb24d567eeb99349f7c36';key=bytes(range(32));seen=[]
 for path,rangevalue in [('/prefix/0001/65537',''),('/chunk/0001','bytes=65537-'),('/chunk/0028','')]:
  class Request:pass
  request=Request();request.path=path;request.headers={'Range':rangevalue};fields=dict(expires='2000000000',nonce='0'*32,PRODUCER=producer)
  a=eval(compile(ast.Expression(message(trees[SERVICE])),'<service HMAC>','eval'),dict(self=request,**fields));b=eval(compile(ast.Expression(message(trees[WORKER])),'<worker HMAC>','eval'),dict(path=path,rangevalue=rangevalue,**fields));assert a==b
  signature=hmac.new(key,a.encode(),hashlib.sha256).hexdigest();assert hmac.compare_digest(signature,hmac.new(key,b.encode(),hashlib.sha256).hexdigest());assert not hmac.compare_digest(signature,hmac.new(key,(b+'x').encode(),hashlib.sha256).hexdigest());seen.append(dict(path=path,range=rangevalue,HMAC_equal=True))
 patterns=[n.args[0].value for n in ast.walk(trees[SERVICE]) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='fullmatch' and isinstance(n.args[0],ast.Constant)]
 cp=next(x for x in patterns if x.startswith('/chunk'));pp=next(x for x in patterns if x.startswith('/prefix'));rp=next(x for x in patterns if x.startswith('bytes='))
 assert re.fullmatch(cp,'/chunk/0001') and not re.fullmatch(cp,'/chunk/../../etc/passwd') and re.fullmatch(pp,'/prefix/0001/65537') and not re.fullmatch(pp,'/prefix/0001/9999999999') and re.fullmatch(rp,'bytes=65537-') and not re.fullmatch(rp,'bytes=1-3')
 tiny=[bytes(range(256))*257,b'small second fixture payload'*3001];prefix=65537;d=hashlib.sha256();d.update(tiny[0]);d.update(tiny[1][:prefix]);d.update(tiny[1][prefix:]);assert d.hexdigest()==hashlib.sha256(b''.join(tiny)).hexdigest();assert hashlib.sha256(tiny[1][:prefix]).hexdigest()==hashlib.sha256(bytes(tiny[1][:prefix])).hexdigest()
 probe_raw=PROBE.read_bytes();assert hashlib.sha256(probe_raw).hexdigest()==PROBE_SHA;probe=json.loads(probe_raw);assert probe['passed'] and probe['probe']['passed_direct_route_TLS_HMAC_probe'] and probe['service_ending']['terminal']['listener_closed']
 report=dict(epoch=time.time(),passed_source_AST_and_offline_bytes_only=True,all_three_source_AST=True,all_six_embedded_AST=True,source_child_STDIN_separator_chr10=True,actual_probe_PASS_receipt_SHA=PROBE_SHA,actual_probe_elapsed_seconds=probe['probe']['elapsed_seconds'],offline_message_cases=seen,wrong_path_and_wrong_range_rejected_by_actual_patterns=True,copied_prefix_plus_suffix_ordered_SHA_matches_fixture=True,no_network_or_secret_ingress_or_model_SDK_GPU_or_canonical_IO=True,not_actual_bulk_transfer_or_SDK_ready=True)
 put(R/'DIRECT_DATA_SOURCE_AST_HMAC_RANGE_OFFLINE_BYTES_ACTUAL.json',report)
 files=[]
 for p in sorted(B.rglob('*')):
  if p.is_file() and p.name!='FROZEN_DIRECT_HTTPS_DATA_PULL_SOURCE_INDEX_V1.json':
   raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 index=dict(epoch=time.time(),status='FROZEN_SOURCE_UNUSED_BULK_TRANSFER',entry=str(ENTRY),entry_SHA=hashlib.sha256(ENTRY.read_bytes()).hexdigest(),service_SHA=hashlib.sha256(SERVICE.read_bytes()).hexdigest(),worker_SHA=hashlib.sha256(WORKER.read_bytes()).hexdigest(),probe_actual_PASS_SHA=PROBE_SHA,files=files,source_service_seconds=1800,target_worker_seconds=1800,local_control_maximum_seconds=1900,source_SSH_closed_before_target_HTTP_foreground=True,no_parallel_SSH_or_GPU_model_Canonical_operation=True,Git='root ordinary supplement pending')
 put(B/'FROZEN_DIRECT_HTTPS_DATA_PULL_SOURCE_INDEX_V1.json',index);print(json.dumps({k:index[k] for k in ['status','entry','entry_SHA','service_SHA','worker_SHA','probe_actual_PASS_SHA']}))

if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);put(R/('DIRECT_DATA_SOURCE_FREEZE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_network=True));raise
