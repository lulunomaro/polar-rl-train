"""One synthetic struct fixture, no owner/node/worker/process/ledger execution."""
from pathlib import Path
from unittest import mock
import ast,copy,hashlib,hmac,importlib.util,io,json,sys,time,traceback
HERE=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 out=HERE/'FLAT90_READY_GO_DISPATCH_ACCOUNT_STRUCT_CPU_ACTUAL_V1.json';assert not out.exists()
 p=load('flat90_protocol_v1',HERE/'flat90_protocol_v1.py');cfg=load('flat90_bound_cfg_v1',HERE/'flat90_bound_cfg_v1.py')
 report=dict(passed=True,kind=p.KIND,source_SHA=p.SOURCE,worker_SHA='1'*64,payload_manifest_SHA='2'*64,source_contract_SHA='3'*64,
  runtime_clock=dict(physics_dt_s=.0025,control_dt_s=.01,decimation=4,policy_hz=100),nominal_gas_N=400,source_native_fullstate_finite=True,
  all_native_modules_norms_threeoptimizers_strict_restore_CPU_passed=True,frozen_RSL832460_exact=True,actual_source_SDK_CPU_passed=True,no_GPU_yet=True,
  GPU_UUID=p.GPU,execution_backend='target72',num_envs=4096,flat_objective=True,source_progress=dict(p.PROGRESS))
 raw=(json.dumps(report,indent=2)+'\n').encode();reportsha=hashlib.sha256(raw).hexdigest()
 payload=b'SYNTHETIC SMALL MANIFEST';contract=b'SYNTHETIC SMALL CONTRACT'
 report['payload_manifest_SHA']=hashlib.sha256(payload).hexdigest();report['source_contract_SHA']=hashlib.sha256(contract).hexdigest()
 raw=(json.dumps(report,indent=2)+'\n').encode();reportsha=hashlib.sha256(raw).hexdigest()
 waited=dict(actual_waited=True,returncode=0,actual_identity=dict(synthetic_not_process=True),payload_manifest_SHA=report['payload_manifest_SHA'],report_SHA=reportsha)
 wr=(json.dumps(waited)+'\n').encode();waitsha=hashlib.sha256(wr).hexdigest()
 request=dict(owner_root=str(Path(p.JOB).parent/'owner'),node_root=str(Path(p.JOB).parent/'node_h1'),run_id='SOURCE_ONLY_SYNTHETIC_FLAT90',
  worker_SHA=report['worker_SHA'],source_CPU_SHA=reportsha,CPU_waited_proof_SHA=waitsha,manifest_SHA='4'*64,
  payload_manifest_SHA=report['payload_manifest_SHA'],source_contract_SHA=report['source_contract_SHA'],payload_manifest_path=p.JOB+'/SYNTHETIC_MANIFEST.json',
  source_contract_path=p.JOB+'/SYNTHETIC_CONTRACT.json',actual_gas400_asset_composition_report_SHA='5'*64,own_step_objective_qualification_SHA='6'*64)
 owner,node=cfg.bound_cfgs(request,'x'*64);assert set(owner['experts'])=={'h1'} and node['key']=='h1'
 p.validate_schedule(owner)
 memory={p.CPU_PATH:raw,p.WAITED_PATH:wr,request['payload_manifest_path']:payload,request['source_contract_path']:contract}
 def read_bytes(path):
  key=str(path).replace('\\','/');return memory[key]
 with mock.patch.object(Path,'read_bytes',read_bytes):envelope=p.load_actual_flat_preinstalled_CPU(node,HERE)
 row=dict(key='h1',phase='ready',manifest_SHA=node['manifest_SHA'],closed_source_CPU=envelope,actual_validation_fcntl_held=True,original_error=False)
 assert p.nativeflat_valid_ready(row,node)
 negatives={}
 for label,change in [('wrong_CPU_kind',lambda x:x['closed_source_CPU']['value'].update(kind='MOD4_E0_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1')),
  ('CPU_report_cannot_self_prove_wait',lambda x:x['closed_source_CPU'].update(actual_CPU_waited_EXIT0=False)),
  ('altered_raw_CPU_report',lambda x:x['closed_source_CPU'].update(raw_report_UTF8='{}')),
  ('altered_wait_proof',lambda x:x['closed_source_CPU']['actual_waited_proof'].update(returncode=1)),
  ('missing_validation_lock',lambda x:x.update(actual_validation_fcntl_held=False))]:
  bad=copy.deepcopy(row);change(bad);assert not p.nativeflat_valid_ready(bad,node);negatives[label]=True
 go=dict(source_SHA=p.SOURCE,source_CPU_SHA=node['source_CPU_SHA'],run_id=node['run_id'],original_owner_pid=1,original_owner_creation=1.,
  learning_started_epoch=100.,save_deadline=3700.,nominal_end_epoch=4000.,max_parent_seconds=3900,exit_headroom_seconds=300,**p.flat_go_fields(node))
 assert go['source_progress']==p.PROGRESS and go['native_reference_SHA']==p.REFERENCE and go['changed_plant700_to_nominal400'] is False and go['flat05_objective_changed_from_native88C'] is True
 common=(HERE/'three_slot_common_v1.py').read_bytes();tree=ast.parse(common)
 def extract(names,scope):
  selected=[]
  for name in names:selected.append([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name][-1])
  exec(compile(ast.Module(body=selected,type_ignores=[]),'<flat90 actual source extracted>', 'exec'),scope);return scope
 calls=[];writes=[]
 class Process:
  pid=123;returncode=0
  def poll(self):return 0
 class PopenSpy:
  @staticmethod
  def Popen(args,**kw):calls.append(dict(args=args,kwargs=kw));return Process()
 scope=dict(Path=Path,J=Path(p.JOB),B=Path(request['node_root']),subprocess=PopenSpy,environment=lambda s:dict(CUDA_VISIBLE_DEVICES=s['GPU_UUID']),
  put=lambda path,value:writes.append((str(path),value)),ident=lambda pid:dict(pid=pid,synthetic_only=True))
 extract(('outdir','spawn'),scope)
 with mock.patch.object(Path,'exists',return_value=False),mock.patch.object(Path,'open',return_value=io.BytesIO()):scope['spawn'](node,'production')
 assert calls[0]['args']==[p.PYTHON,'-u','-B',str(Path(p.JOB)/p.WORKER_NAME),'--slot','h1','--phase','production','--num-envs','4096','--seed','27','--source-scope','native_models_only_fresh400N_environment']
 assert str(scope['outdir']('production')).replace('\\','/')==p.JOB+'/job0/production' and calls[0]['kwargs']['env']['CUDA_VISIBLE_DEVICES']==p.GPU
 charge_scope={};extract(('charge_values',),charge_scope)
 c=dict(charged_training_seconds=0.,remaining_training_seconds=2268000.);segment=dict(experts={},charged_expert_seconds=0.)
 charge_scope['terminal']=lambda r:bool(r.get('terminal_all_own_children_waited') and r.get('returncode')is not None)
 charge_go={'h1':dict(learning_started_epoch=1.,max_parent_seconds=3900)}
 charge_scope['charge_values'](c,segment,charge_go,{},6.25)
 terminal={'h1':dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=13.75)}
 charge_scope['charge_values'](c,segment,charge_go,terminal,20.);charge_scope['charge_values'](c,segment,charge_go,terminal,25.)
 assert segment['charged_expert_seconds']==12.75 and set(segment['experts'])=={'h1'} and segment['experts']['h1']['charged_seconds']==12.75
 with out.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed=True,synthetic_only_not_actual_CPU_or_GO=True,
  source_files={n:H(HERE/n) for n in cfg.RUNTIME_FILES},strict_ready_sealed_raw_CPU_and_actualwait_envelope_positive=True,
  negative_rejections=negatives,typedGO_matches_new88C_flat05_scope=True,native_exact_CLI_job0_production_dispatch_spied=True,
  original_fractional_charge_sum_once_synthetic_seconds=12.75,one_logical_h1_slot=True,no_owner_worker_or_process_launched=True,
  no_GPU_SDK_PT_remote_or_ledger_IO=True,no_real_token_or_cfg_written=True,actual_source_SDK_resource_sealed_CPU_waited_and_GO_pending=True,
  Git_status='ordinary_supplement_pending_root'),f,indent=2)
 print(json.dumps(dict(passed=True,report_SHA=H(out),source_only=True,actual_launch=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  (HERE/('FLAT90_STRUCT_FIXTURE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc(),no_actual_launch=True),indent=2),encoding='utf8');raise
