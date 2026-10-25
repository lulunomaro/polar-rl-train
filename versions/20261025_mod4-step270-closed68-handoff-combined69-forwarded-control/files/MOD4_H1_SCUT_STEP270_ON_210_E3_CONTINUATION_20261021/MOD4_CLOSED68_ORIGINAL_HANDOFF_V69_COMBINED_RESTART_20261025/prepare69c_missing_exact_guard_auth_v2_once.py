"""V2 finish local69c missing E3 guard, exact auth, manifests; preserve V1 partial/error."""
from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,time
D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports'
P=T/'H1_STEP270_REWARD_SAGITTAL_TUCK_V6A_RESOURCE_V68_20261025'
old=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V2_RESOURCE_V69_20261025'
N=T/'H1_STEP270_SAGITTAL_V6A_SAMPLING_OPT_V3_RESOURCE_V69_20261025';nr=N/'reports'
assert N.exists() and not(nr/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').exists()
q=json.loads((old/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());q['epoch']=time.time();q['owner_root']=q['owner_root'].replace('_2510v69b/','_2510v69c/')
auth=dict(epoch=time.time(),approved=True,human_authorization='开始训练；上台阶修复和提速一起',scope='Original HMAC messages over local loopback or original-pinned SSH; only send function and own connection close',control_module_SHA='46372c53ad0987cf366ab906965e951fd4b87890750c913ed1ec3b4eb93833b7',slots={})
p=N/'payloads/recovery/original_account_policy50_source_CPU.py';raw=p.read_bytes();assert raw==(D/'before69_network_control_source/69b_recovery_original_account_policy50_source_CPU.py').read_bytes()
s=raw.decode('utf8');needle='\n _sampling_receipt(B,old,key,m,before,cpu)';assert s.count(needle)==1
s=s.replace(needle,"\n from network_control_exact_source_CPU_v1 import check as network_control_check\n assert network_control_check(B,old,key)['passed']"+needle,1);ast.parse(s);p.write_text(s,encoding='utf8')
shutil.copy2(D/'network_control_exact_source_CPU_v1.py',N/'payloads/recovery/network_control_exact_source_CPU_v1.py')
for key in q['specs']:
 q['roots'][key]=q['roots'][key].replace('_2510v69b/','_2510v69c/');q['payloads'][key]=str(N/'payloads'/key);base=N/'payloads'/key
 guard='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
 original=(D/'before69_network_control_source'/('69b_'+key+'_'+guard)).read_bytes()
 auth['slots'][key]=dict(old_node_SHA=hashlib.sha256((P/'payloads'/key/'three_slot_finite_node_v1.py').read_bytes()).hexdigest(),new_node_SHA=hashlib.sha256((base/'three_slot_finite_node_v1.py').read_bytes()).hexdigest(),old_sampling_guard_SHA=hashlib.sha256(original).hexdigest(),new_guard_SHA=hashlib.sha256((base/guard).read_bytes()).hexdigest())
 a=hashlib.sha256((base/'SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json').read_bytes()).hexdigest()
 if 'original_sampling_auth_SHA' in auth:assert auth['original_sampling_auth_SHA']==a
 else:auth['original_sampling_auth_SHA']=a
 p=base/'job0/TASK.json';task=json.loads(p.read_bytes());task['id']=N.name+'_'+key;task['network_loader_revision']='V3_EXACT_NODE_TRANSPORT_AST_AUTH';p.write_text(json.dumps(task,indent=2),encoding='utf8')
for key in q['specs']:
 base=N/'payloads'/key;(base/'FORWARDED_NETWORK_CONTROL_AUTH_AND_CPU_ACTUAL.json').write_text(json.dumps(auth,ensure_ascii=False,indent=2),encoding='utf8')
 mf=base/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';m=json.loads(mf.read_bytes());prior={x['relative']:x for x in m['files']};rows=[]
 for p in sorted(base.rglob('*')):
  if not p.is_file() or p==mf or '__pycache__' in p.parts:continue
  rel=p.relative_to(base).as_posix()
  if p.suffix in ('.pt','.npz','.usd','.stl'):
   row=prior[rel];assert p.stat().st_size==row['bytes'];sha=row['SHA']
  else:sha=hashlib.sha256(p.read_bytes()).hexdigest()
  rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=sha))
 m['files']=rows;mf.write_text(json.dumps(m,indent=2),encoding='utf8');q['specs'][key]['manifest_SHA']=hashlib.sha256(mf.read_bytes()).hexdigest()

spec=importlib.util.spec_from_file_location('network_cpu',D/'network_control_exact_source_CPU_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks={k:m.check(N/'payloads'/k,P/'payloads'/k,k) for k in q['specs']};assert all(x['passed'] for x in checks.values())
q.update(preGO_V2_failure_preserved_in=str(old),new_unused_remote_roots=True,no_old_root_retry=True,exact_network_guard_auth_source_cpu=auth)
for name in ['ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json','RESOURCE_BRANCH_PREPARE_DECISION_ACTUAL.json']:shutil.copy2(old/'reports'/name,nr/name)
with (nr/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(q,f,ensure_ascii=False,indent=2)
with (R/'NEXT69C_EXACT_NETWORK_ADMISSION_EXTENSION_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,auth=auth,checks=checks,new_namespace=str(N),old_failure_preserved=str(old),source68_only=q['sources'],new_roots=q['roots'],no_remote_install_or_GO_yet=True,no_original_reward_retention_or_sampling_approval_overwrite=True),f,ensure_ascii=False,indent=2)
print(json.dumps(dict(passed=True,new_namespace=str(N),network_AST_checks=checks,no_GO=True)))
