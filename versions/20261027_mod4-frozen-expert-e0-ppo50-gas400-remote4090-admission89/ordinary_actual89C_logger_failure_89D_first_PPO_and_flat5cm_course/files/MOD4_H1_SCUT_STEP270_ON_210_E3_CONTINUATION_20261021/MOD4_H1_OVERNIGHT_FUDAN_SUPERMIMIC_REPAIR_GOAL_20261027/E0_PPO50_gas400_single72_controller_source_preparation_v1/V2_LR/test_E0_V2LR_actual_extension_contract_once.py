"""Actual metadata + exact source function fixture; no process/model/ledger activity."""
from pathlib import Path,PurePosixPath
import ast,copy,hashlib,json,sys,time,types
HERE=Path(__file__).resolve().parent;T=HERE.parents[2]
def load(name,path):
 module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
 exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__);return module
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 target=HERE/'E0_V2LR_ACTUAL_EXTENSION_READY_GO_DISPATCH_COST_CPU_PASSED.json';assert not target.exists()
 p=load('E0_single72_protocol_v1',HERE/'E0_single72_protocol_v1.py')
 cfg=load('E0_single72_bound_cfg_v1',HERE/'E0_single72_bound_cfg_v1.py')
 extension=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89C_20261027/reports/E0_V4_WORKER_ONLY_LR_SOURCE_MIGRATION_ACTUAL.json'
 value=json.loads(extension.read_bytes());assert H(extension)==p.CPU==p.digest(value);p.validate_cpu_value(value)
 request=dict(owner_root=str(Path(p.JOB).parent/'owner'),node_root=str(Path(p.JOB).parent/'node_e0'),manifest_SHA='a'*64,CPU_returned_proof_SHA='b'*64,run_id='SYNTHETIC_CONTRACT_ONLY_NOT_GO')
 owner,node=cfg.bound_cfgs(request,'SYNTHETIC_NON_SECRET_FIXTURE_TOKEN_0000000000');p.validate_schedule(owner)
 r=dict(key='e0',phase='ready',manifest_SHA=node['manifest_SHA'],actual_validation_fcntl_held=True,closed_source_CPU=dict(value=value,SHA=p.CPU,actual_CPU_waited_EXIT0=True))
 assert p.E0_valid_ready(r,node);go=p.E0_go_fields(node);assert go['worker_SHA']==p.WORKER and go['GPU_UUID']==p.GPU and go['authority_generation']==p.GENERATION
 negative=[]
 for field,bad in [('key','recovery'),('source_SHA','0'*64),('worker_SHA',p.BASE_WORKER),('source_CPU_SHA',p.BASE_CPU),('max_parent_seconds',3600)]:
  s=copy.deepcopy(node);s[field]=bad;assert not p.E0_valid_ready(r,s);negative.append(field)
 for field,bad in [('no_model_reload',False),('exact_single_CLI_literal_change',False),('target_worker_SHA',p.BASE_WORKER)]:
  q=copy.deepcopy(r);q['closed_source_CPU']['value'][field]=bad;assert not p.E0_valid_ready(q,node);negative.append(field)
 raw=(HERE/'three_slot_common_v1.py').read_bytes();tree=ast.parse(raw)
 def functions(names):return ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[])
 calls=[]
 class Log:
  def open(self,mode):assert mode=='xb';return None
 class Job:
  def __str__(self):return p.JOB
  def __truediv__(self,name):return Log() if name.endswith('.log') else PurePosixPath(p.JOB)/name
 class NoOutput:
  def exists(self):return False
 scope=dict(J=Job(),B=PurePosixPath(p.JOB).parent/'node_e0',
  subprocess=types.SimpleNamespace(STDOUT=-2,Popen=lambda args,**kw:(calls.append(args) or types.SimpleNamespace(pid=123))),
  environment=lambda spec:{'CUDA_VISIBLE_DEVICES':spec['GPU_UUID']},put=lambda *a:None,ident=lambda pid:dict(pid=pid))
 exec(compile(functions({'outdir','spawn'}),'<exact installed dispatch source; spy only>','exec'),scope)
 out=str(scope['outdir']('production'));assert out==p.JOB+'/adaptation';scope['outdir']=lambda phase:NoOutput();scope['spawn'](node,'production')
 expected=[p.PYTHON,'-u','-B',p.JOB+'/E0_PPO50_gas400_finite_worker_v4_preserved_LR_scalar.py','--job-root',p.JOB];assert calls==[expected]
 pure={};exec(compile(functions({'terminal','charge_values'}),'<original accounting; memory fixture only>','exec'),pure)
 c=dict(charged_training_seconds=0.,remaining_training_seconds=2268000.);segment=dict(experts={},charged_expert_seconds=0.)
 g=dict(e0=dict(learning_started_epoch=1000.,max_parent_seconds=3900))
 c,segment=pure['charge_values'](c,segment,g,{},1000.25);assert c['charged_training_seconds']==.25
 c,segment=pure['charge_values'](c,segment,g,{},1010.);assert c['charged_training_seconds']==10.
 terminal=dict(e0=dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=1012.75))
 c,segment=pure['charge_values'](c,segment,g,terminal,1020.);c,segment=pure['charge_values'](c,segment,g,terminal,1030.);assert c['charged_training_seconds']==12.75
 result=dict(epoch=time.time(),passed=True,actual_extension_SHA=p.CPU,actual_base_fullstate_CPU_SHA=p.BASE_CPU,
  actual_metadata_ready_digest_GO_fields=True,source_dispatch_actual_function_spy_argv=expected,outdir=out,
  node_original_state_uses_outdir_latest_save_waited_exit=True,negative_cases=negative,original_accounting_fractional_sum_once=12.75,
  no_owner_node_worker_spawn_or_GPU_or_PT_or_ledger_IO=True,fixture_tokens_synthetic_not_runtime_secrets=True,
  prior_fixture_locator_import_scaffold_errors_retained=True,Git_status='ordinary_supplement_existing89trial')
 target.write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result))
if __name__=='__main__':main()
