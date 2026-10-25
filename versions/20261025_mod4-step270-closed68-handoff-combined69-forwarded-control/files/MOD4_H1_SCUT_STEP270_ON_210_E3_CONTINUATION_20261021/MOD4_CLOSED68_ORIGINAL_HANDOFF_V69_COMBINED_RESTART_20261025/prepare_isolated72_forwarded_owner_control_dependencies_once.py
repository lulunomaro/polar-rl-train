"""Pinned SSH control dependencies in a new isolated directory; training environment stays intact."""
from pathlib import Path
import importlib.util,json,os,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports'
CODE=r'''
from pathlib import Path
import hashlib,importlib.metadata,json,os,shutil,subprocess,sys,time
root=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_forwarded_owner_control_deps_20261025');assert not root.exists() and shutil.disk_usage(root.parent).free>25*1024**3
root.mkdir();target=root/'site_packages';env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PIP_DISABLE_PIP_VERSION_CHECK='1')
cmd=['/home/lc01/Zonglin Li/zonglin2/run-python.sh','-B','-m','pip','install','--no-compile','--no-cache-dir','--only-binary=:all:','--target',str(target),'paramiko==5.0.0']
p=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=180)
result=dict(epoch=time.time(),root=str(root),command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,training_environment_not_modified=True)
if p.returncode==0:
 sys.path.insert(0,str(target));import paramiko
 assert paramiko.__version__=='5.0.0' and str(Path(paramiko.__file__).resolve()).startswith(str(target.resolve())+'/')
 files=[]
 for path in sorted(target.rglob('*')):
  if path.is_file():
   raw=path.read_bytes();files.append(dict(relative=path.relative_to(root).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 result.update(paramiko_version=paramiko.__version__,installed_files=files,bytes=sum(x['bytes'] for x in files),no_GPU_policy_import_or_model_read=True)
 raw=json.dumps(result,ensure_ascii=False,indent=2).encode();(root/'INSTALLED_SOURCE_CPU_RECEIPT.json').write_bytes(raw)
 result['receipt_SHA']=hashlib.sha256(raw).hexdigest()
print(json.dumps(result))
'''
with (R/'ISOLATED72_CONTROL_DEPS_STARTED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv),f)
try:
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 p=W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py';sp=importlib.util.spec_from_file_location('memory',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 secret=m.recover();c=d.connect72(secret);secret=None
 try:value=d.code(c,d.PY72,CODE,{},timeout=210)
 finally:c.close()
 with (R/'ISOLATED72_CONTROL_DEPS_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(value,actual_finite_returned=True),f,ensure_ascii=False,indent=2)
 assert value['returncode']==0
 print(json.dumps(dict(returncode=value['returncode'],paramiko_version=value['paramiko_version'],bytes=value['bytes'],file_count=len(value['installed_files']),receipt_SHA=value['receipt_SHA'],training_environment_not_modified=True)))
except BaseException:
 with (R/'ISOLATED72_CONTROL_DEPS_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GO_or_budget_write=True),f,indent=2)
 raise
