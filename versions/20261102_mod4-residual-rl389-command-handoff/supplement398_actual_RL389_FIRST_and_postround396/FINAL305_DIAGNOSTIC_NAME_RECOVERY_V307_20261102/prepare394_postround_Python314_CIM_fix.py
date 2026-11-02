"""New unused394 postround fixes localPython314 missingpsutil; training389 untouched."""
from pathlib import Path
import ast,hashlib,json,shutil,time
P=Path(__file__).resolve().parent;T=P.parent;N=T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102';OQ=T/'RESIDUAL_RL389_POSTROUND_V390_20261102';OE=T/'RESIDUAL_RL389_INDEPENDENT_EVAL_V390_20261102';Q=T/'RESIDUAL_RL389_POSTROUND_V394_20261102';E=T/'RESIDUAL_RL389_INDEPENDENT_EVAL_V394_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
assert not(N/'reports/BIND388_POSTROUND_ONCE_CONSUMED.json').exists()
put(P/'reports/STATIC394_UNUSED390_LOCALPSUTIL_DEPENDENCY_REJECTION.json',dict(epoch=time.time(),passed=False,scope='Original390unusednotrun; frozen389trainingnochanges',actual_tool='Python314 -c importpsutil exit1 ModuleNotFoundError',reason='Local390postroundandrunnerexactparentcheckimportpsutilbutPython314hasnone',network=0,SDK=0,model_reads=0,GO=False,repair='New394 uses nativeWindows exactCIM PID/create/exe/argv and os.getppid for sole own synchronously waitedlocalparent; no install needed'))
def rename(text):
 for a,b in((str(OQ),str(Q)),(OQ.as_posix(),Q.as_posix()),(str(OE),str(E)),(OE.as_posix(),E.as_posix())):text=text.replace(a,b)
 # 390 has no occurrence inside pinned sourcehash/GPUUUID; token names only.
 import re
 return re.sub(r'(?<=[A-Za-z_])390(?!\d)','394',text)
for origin,dest in((OQ,Q),(OE,E)):
 assert not dest.exists();dest.mkdir();(dest/'reports').mkdir()
 for p in origin.rglob('*'):
  if not p.is_file()or'__pycache__'in p.parts:continue
  if p.name.startswith('INDEX')or p.parent.name=='reports':continue
  q=dest/rename(str(p.relative_to(origin)));q.parent.mkdir(parents=True,exist_ok=True)
  if p.suffix=='.py':q.write_text(rename(p.read_text('utf8')),encoding='utf8')
  elif p.suffix=='.json':q.write_text(rename(p.read_text('utf8')),encoding='utf8')
  else:shutil.copyfile(p,q)
p=Q/'postround394_close_RL389_eval_once.py';s=p.read_text('utf8')
old=" import psutil\n environment=dict(os.environ,MOD4_394_OWN_POSTROUND_PARENT_PID=str(os.getpid()),MOD4_394_OWN_POSTROUND_PARENT_CREATE=str(psutil.Process().create_time()))"
new=""" query='Get-CimInstance Win32_Process -Filter "ProcessId='+str(os.getpid())+'" | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Compress'
 me=json.loads(subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True).stdout)
 assert me['ProcessId']==os.getpid()and me['ExecutablePath'].lower()==CONTROL.lower()
 environment=dict(os.environ,MOD4_394_OWN_POSTROUND_PARENT_PID=str(os.getpid()),MOD4_394_OWN_POSTROUND_PARENT_CREATE=me['CreationDate'])"""
assert old in s;s=s.replace(old,new);p.write_text(s,encoding='utf8')
p=E/'run394_eval_once.py';s=p.read_text('utf8');start=s.index('        import psutil');end=s.index("\n    put('ROOT394_FRESH_EXACT_LOCAL_CIM",start)
s=s[:start]+"""        actual=other[0];assert actual['ProcessId']==os.getppid()
        assert actual['ExecutablePath'].lower()==sys.executable.lower()
        assert '/postround394_close_RL389_eval_once.py' in actual['CommandLine'].replace('\\\\','/').lower()
        assert actual['CreationDate']==os.environ['MOD4_394_OWN_POSTROUND_PARENT_CREATE']
"""+s[end:];p.write_text(s,encoding='utf8')
task=json.loads((E/'TASK394_PENDING_FINAL_IDENTITY.json').read_bytes());task['worker_SHA']=H(E/'source/evaluate394.py')
# Pending task generated here is unexecuted metadata, independently frozen by timer afterfinal.
taskpath=E/'TASK394_PENDING_FINAL_IDENTITY.json';taskpath.write_text(json.dumps(task,indent=2),encoding='utf8')
for p in list(Q.rglob('*.py'))+list(E.rglob('*.py')):ast.parse(p.read_text('utf8'))
assert 'import psutil'not in(E/'run394_eval_once.py').read_text('utf8')and 'import psutil'not in(Q/'postround394_close_RL389_eval_once.py').read_text('utf8')
put(Q/'INDEX394_POSTROUND_FOR389_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for root in(Q,E)for p in sorted(root.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]))
put(P/'reports/STATIC394_POSTROUND_RL389_CIM_DEPENDENCY_REPAIR.json',dict(epoch=time.time(),passed=True,root=str(Q),evalroot=str(E),indexSHA=H(Q/'INDEX394_POSTROUND_FOR389_FROZEN.json'),training389frozenunchanged=True,390unusedpreserved=True,allAST=True,exactlocalCIM_parentonly=True,newSSH=0,modelreads=0))
print(json.dumps(dict(passed=True,root=str(Q),indexSHA=H(Q/'INDEX394_POSTROUND_FOR389_FROZEN.json'))))
