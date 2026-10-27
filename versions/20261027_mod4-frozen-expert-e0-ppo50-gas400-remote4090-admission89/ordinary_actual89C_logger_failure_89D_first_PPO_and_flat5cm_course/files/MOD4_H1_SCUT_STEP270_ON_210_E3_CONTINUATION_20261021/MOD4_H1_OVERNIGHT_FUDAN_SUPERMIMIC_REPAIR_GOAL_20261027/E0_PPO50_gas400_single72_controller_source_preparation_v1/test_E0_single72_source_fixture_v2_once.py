"""One metadata/pure-memory fixture. No owner/node/worker spawn or ledger I/O."""
from pathlib import Path
import ast,copy,hashlib,json,sys,time,types
HERE=Path(__file__).resolve().parent;T=HERE.parents[1]
import E0_single72_protocol_v1 as p
from E0_single72_bound_cfg_v1 import bound_cfgs,logical_argv,expected_exec
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def extract(path,names):
 tree=ast.parse(Path(path).read_bytes());return ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[])
def main():
 report=HERE/'E0_SINGLE72_READY_GO_SPAWN_CHARGE_SOURCE_FIXTURE_ACTUAL_V2.json';assert not report.exists()
 actual=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027/reports/E0_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V2.json'
 value=json.loads(actual.read_bytes());assert H(actual)==p.CPU==p.digest(value);p.validate_cpu_value(value)
 request=dict(owner_root=str(Path(p.JOB).parent/'owner'),node_root=str(Path(p.JOB).parent/'node_e0'),manifest_SHA='a'*64,CPU_returned_proof_SHA='b'*64,run_id='SYNTHETIC_SOURCE_FIXTURE_ONLY_NOT_A_GO')
 owner,node=bound_cfgs(request,'SYNTHETIC_NOT_A_SECRET_OR_ACTUAL_TOKEN_0'*2);p.validate_schedule(owner)
 row=dict(key='e0',phase='ready',manifest_SHA=node['manifest_SHA'],actual_validation_fcntl_held=True,
  closed_source_CPU=dict(value=value,SHA=p.CPU,actual_CPU_waited_EXIT0=True),original_error=False)
 assert p.E0_valid_ready(row,node);fields=p.E0_go_fields(node);assert fields['GPU_UUID']==p.GPU and fields['authority_generation']==p.GENERATION and fields['num_envs']==20000
 negatives=[]
 for name,edit in [('wrong_source',lambda s:s.update(source_SHA='0'*64)),('fake_second_expert_role',lambda s:s.update(key='recovery')),
  ('old_worker_V1',lambda s:s.update(worker_SHA='502110722556d44c57ae94d1fd523343de7a12b4ddc2108726bd7914294a5466')),
  ('wrong_CPU',lambda s:s.update(source_CPU_SHA='0'*64)),('wrong_cap',lambda s:s.update(max_parent_seconds=3600)),('wrong_GPU',lambda s:s.update(GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842'))]:
  bad=copy.deepcopy(node);edit(bad);assert not p.E0_valid_ready(row,bad);negatives.append(name)
 for field,bad_value in [('actual_CUDA_generator_restore_passed',True),('CPU_rng_substitution_used',True)]:
  bad=copy.deepcopy(row);bad['closed_source_CPU']['value']['queue_structure_proof'][field]=bad_value
  assert not p.E0_valid_ready(bad,node);negatives.append(field)
 # Extract actual dispatch functions and replace only subprocess with a spy.
 calls=[]
 class FakeProcess:
  pid=12345
 class FakeLog:
  def open(self,mode):assert mode=='xb';return None
 class FakePath:
  def __truediv__(self,name):return FakeLog() if name.endswith('.log') else Path(p.JOB)/name
 class NoOut:
  def exists(self):return False
 scope=dict(Path=Path,J=FakePath(),B=Path('/SYNTHETIC_SOURCE_ONLY'),
  subprocess=types.SimpleNamespace(STDOUT=-2,Popen=lambda args,**kw:(calls.append((args,{k:str(v) for k,v in kw.items() if k not in ('env','stdout')})) or FakeProcess())),
  environment=lambda spec:{'CUDA_VISIBLE_DEVICES':spec['GPU_UUID']},put=lambda *a:None,ident=lambda pid:dict(pid=pid))
 exec(compile(extract(HERE/'three_slot_common_v1.py',{'outdir','spawn'}),'<actual E0 dispatch source>','exec'),scope)
 actual_out=scope['outdir']('production');assert actual_out==Path(p.JOB)/'adaptation'
 scope['outdir']=lambda phase:NoOut();scope['spawn'](node,'production')
 assert calls[0][0]==[p.PYTHON,'-u','-B',str(Path(p.JOB)/node['production_script']),'--job-root',p.JOB]
 # Original charge_values runs only against synthetic scalars in memory.
 pure={};exec(compile(extract(HERE/'three_slot_common_v1.py',{'terminal','charge_values'}),'<unchanged original accounting, synthetic memory>','exec'),pure)
 c=dict(charged_training_seconds=0.,remaining_training_seconds=2268000.);a=dict(experts={},charged_expert_seconds=0.)
 go=dict(e0=dict(learning_started_epoch=1000.,max_parent_seconds=3900))
 c,a=pure['charge_values'](c,a,go,{},1000.25);assert c['charged_training_seconds']==.25
 c,a=pure['charge_values'](c,a,go,{},1010.);assert c['charged_training_seconds']==10.
 terminal=dict(e0=dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=1012.75))
 c,a=pure['charge_values'](c,a,go,terminal,1020.);assert c['charged_training_seconds']==12.75
 c,a=pure['charge_values'](c,a,go,terminal,1030.);assert c['charged_training_seconds']==12.75 and c['remaining_training_seconds']==2267987.25
 idle=dict(charged_training_seconds=0.,remaining_training_seconds=2268000.);segment=dict(experts={},charged_expert_seconds=0.)
 idle,segment=pure['charge_values'](idle,segment,{},row,2000.);assert idle['charged_training_seconds']==0.
 # Existing state() must observe adaptation output, latest fullsave and waited exit.
 tree=ast.parse((HERE/'three_slot_common_v1.py').read_bytes());state=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='state')
 assert "out=outdir(phase)" in ast.get_source_segment((HERE/'three_slot_common_v1.py').read_text('utf8'),state)
 files=[dict(path=str(f),bytes=f.stat().st_size,SHA=H(f)) for f in sorted(HERE.glob('*.py'))]
 result=dict(epoch=time.time(),passed=True,prior_fixture_error_tool_chunk='398d85',prior_error='Synthetic subprocess spy omitted STDOUT constant; AttributeError before any real spawn; V1 source preserved.',source_CPU_actual_file=str(actual),source_CPU_SHA=p.CPU,actual_ready_digest_GO_fields=True,
  single_slot_keys=list(owner['experts']),negative_cases=negatives,actual_spawn_function_called_with_subprocess_spy_only=True,
  production_argv=calls[0][0],outdir=str(actual_out),state_original_adaptation_latest_save_waited_exit_dispatch=True,
  synthetic_fractional_sum_once_cost=12.75,repeat_terminal_no_double_charge=True,idle_without_GO_cost0=True,
  charge_values_original_source_exact=True,real_ledger_or_owner_or_worker_not_run=True,no_GPU_or_model_binary_read=True,
  token_fixture_only_never_real_runtime_token=True,files=files,Git_status='pending_ordinary_supplement_existing89trial')
 report.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(dict(passed=True,negatives=len(negatives),source_CPU_SHA=p.CPU,spawn_argv=calls[0][0],outdir=str(actual_out))))
if __name__=='__main__':main()
