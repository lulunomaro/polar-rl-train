"""Saved process metadata + fake psutil clock only. No process/network/model execution."""
from pathlib import Path
from types import SimpleNamespace
import sys,json,ast,hashlib,traceback,datetime,types
D=Path(__file__).resolve().parent;L=D.parent.parent;T=L.parent
protocol_path=L/'agent_native87_worker_and_target_CPU_entry_candidate/native87_protocol_v1.py'
protocol=types.ModuleType('native87_protocol_v1');protocol.__file__=str(protocol_path);sys.modules[protocol.__name__]=protocol
exec(compile(protocol_path.read_text('utf8'),str(protocol_path),'exec'),protocol.__dict__)
module_path=D/'native87_closed_source_CPU_v1.py';m=types.ModuleType('native87_closed_source_CPU_v1');m.__file__=str(module_path)
exec(compile(module_path.read_text('utf8'),str(module_path),'exec'),m.__dict__)
N=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/reports'
prepared=N/'THREE_GPU86B_SOURCE_ADMITTED_PREPARED_ACTUAL.json'
observed=N/'THREE_GPU86B_FIRST_GO_PPO_NATIVE_POLICY_PHASE_ACTUAL.json'
q=json.loads(prepared.read_bytes());o=json.loads(observed.read_bytes())
rows=[]
def case(name,fn):
 try:detail=fn();rows.append(dict(name=name,passed=True,detail=detail))
 except Exception:rows.append(dict(name=name,passed=False,error=traceback.format_exc()))
def yes(v):assert bool(v)
def rejects(fn):
 try:fn()
 except AssertionError:return True
 raise AssertionError('expected rejection')
for key in ('h1','e2','recovery'):
 def check_saved(key=key):
  s=q['specs'][key];actual=o['targets'][key]['worker'];logical=actual['argv'] if key=='h1' else [m.WRAPPER72,*actual['argv'][5:]]
  expected=m.expected_exec_identity(s,logical)
  yes(expected['argv']==actual['argv'] and expected['exe']==actual['exe'])
  return dict(saved_actual86_process_metadata_recipe_exact=True,no_runtime_probe=True)
 case('saved_actual_exact_recipe_'+key,check_saved)
for key in ('h1','e2','recovery'):
 def wrong(key=key):s=dict(q['specs'][key],python='/unapproved/python');return rejects(lambda:m.expected_exec_identity(s,[s['python'],'x.py']))
 case('unknown_interpreter_rejected_'+key,wrong)

def simulated_wait(kind):
 spec=q['specs']['e2'];B=Path('/fixture-only/root');args=[m.WRAPPER72,'-u','-B',str(B/'target.py')];expected=m.expected_exec_identity(spec,args)
 class FakeTime:
  now=0.
  def monotonic(self):return self.now
  def sleep(self,n):self.now+=n
 class FakeProcess:
  index=-1
  def create_time(self):return 20. if kind!='reused_identity' or self.index<0 else 21.
  def cmdline(self):
   self.index+=1
   return ['bash',m.WRAPPER72,*args[1:]] if self.index==0 or kind=='timeout' else expected['argv']
  def exe(self):return '/usr/bin/bash' if self.index==0 or kind=='timeout' else expected['exe']
  def cwd(self):return str(B)
 fake=FakeProcess();original_ps=sys.modules.get('psutil');original_time=m.time
 sys.modules['psutil']=SimpleNamespace(Process=lambda pid:fake);m.time=FakeTime()
 try:
  p=SimpleNamespace(pid=123,poll=lambda:None)
  if kind=='stable':
   identity=m.wait_exact_exec_identity(p,B,spec,args);yes(identity['exe']==m.LOADER72 and identity['argv']==expected['argv'] and fake.index==2)
   return dict(two_exact_snapshots_after_exec=True,no_actual_process=True)
  return rejects(lambda:m.wait_exact_exec_identity(p,B,spec,args,timeout_s=.12))
 finally:
  m.time=original_time
  if original_ps is None:sys.modules.pop('psutil',None)
  else:sys.modules['psutil']=original_ps
case('fake_wrapper_exec_then_two_stable_snapshots',lambda:simulated_wait('stable'))
case('fake_wrapper_timeout_rejected',lambda:simulated_wait('timeout'))
case('fake_process_create_time_change_rejected',lambda:simulated_wait('reused_identity'))
def source_checks():
 text=(D/'native87_closed_source_CPU_v1.py').read_text();tree=ast.parse(text)
 yes('endswith' not in text)
 yes(text.count("expected_argv=expected['argv'],expected_exe=expected['exe'],expected_root=str(B)")==2)
 yes("identity['root']==expected_root" in text and 'identity=wait_exact_exec_identity(p,B,spec,args)' in text)
 yes(len([n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Popen'])==1)
 yes('torch.load' not in text and "with proof_path.open('x'" in text)
 return dict(fresh_and_cache_same_exact_recipe=True,no_model_loading_or_broadened_interpreter_match=True)
case('fresh_cache_proof_source_AST',source_checks)
report=dict(passed=all(r['passed'] for r in rows),passed_count=sum(r['passed'] for r in rows),total=len(rows),tests=rows,
    actual_process_SDK_network_or_model_executed=False,saved_actual_metadata_plus_synthetic_clock_only=True)
with (D/'WRAPPER_IDENTITY_DISPATCHER_V2_READER_FIXED_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
assert report['passed']
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with (D/'ORIGINAL_LOCAL_SOURCE_IMPORT_ERROR_AND_READER_FIX_ACTUAL.json').open('x',encoding='utf8') as f:
 json.dump(dict(original_script='test_and_freeze_wrapper_dispatcher_v2_once.py',original_error="ModuleNotFoundError: No module named 'native87_closed_source_CPU_v1'",file_existed=True,
   before_any_fixture_execution=True,reader_fix='Explicit compile of exact source into module namespace; no runtime monkeypatch or model/process execution',production_dispatcher_source_unchanged=True),f,indent=2)
with (D/'SAVED_ACTUAL_PROCESS_IDENTITY_SOURCE_LINEAGE_ACTUAL.json').open('x',encoding='utf8') as f:
 json.dump(dict(inputs=[dict(path=str(p),SHA=H(p),bytes=p.stat().st_size) for p in (prepared,observed)],
    previous_frozen_source_unchanged=True),f,indent=2)
text='''Dispatcher V2已冻结，解决72 run-python.sh实际exec为ld-loader的确定接线错误。h1仍精确原python argv/exe；72只接受既有LD/libpath/envPython/-B前缀+原逻辑argv，不使用endswith或放宽解释器匹配。

fresh分支启动同一CPU子进程后，最多5s等待wrapper exec稳定，要求同pid/create/exe/argv/cwd两次精确一致，再保存实际identity并等待EXIT0。cache使用相同expected recipe及精确root验证，绝不重CPU/model load。原Proof/schema与manifest/script/report/source/STARTED/WAITED/externalSHA绑定保持，旧冻结11文件目录未改。

本机10项source/metadata检查通过：使用已保存86B三路实际process文本核对recipe，fake psutil+fakeclock模拟exec稳定/timeout/create变化，没有真实进程、SDK、网络或模型。root应在新controllers和3payload复制本同名dispatcher后全部重pin，旧SHA87f...不再用于新manifest。观察器可复用expected_exec_identity(spec,logicalargv)核对worker或node。
'''
with (D/'FROZEN_DISPATCHER_WRAPPER_V2_HANDOFF.md').open('x',encoding='utf8') as f:f.write(text)
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
files=[dict(path=p.relative_to(D).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='FROZEN_DISPATCHER_WRAPPER_V2_SHA_INDEX.json']
with (D/'FROZEN_DISPATCHER_WRAPPER_V2_SHA_INDEX.json').open('x',encoding='utf8') as f:json.dump(dict(frozen_at_UTC=stamp,files=files,count_excluding_index=len(files),parent_archive_pending=True),f,indent=2)
print(json.dumps(dict(passed=report['passed'],CPU=str(report['passed_count'])+'/'+str(report['total']),frozen_at_UTC=stamp,
 dispatcher_SHA=H(D/'native87_closed_source_CPU_v1.py'),index_SHA=H(D/'FROZEN_DISPATCHER_WRAPPER_V2_SHA_INDEX.json'))))
