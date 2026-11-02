"""V3unusedsource: obeyoriginaljob-onlyKitlauncher, retainE1caseowner, observeW35firstoriginalreset. Purestdlibdrylauncher contracts."""
from pathlib import Path
import ast,json,hashlib,os,sys,types
R=Path(__file__).resolve().parent;S=R/'NINE_N80_PARALLEL_SOURCE_V2';D=R/'NINE_N80_PARALLEL_SOURCE_V3';assert not D.exists();D.mkdir()
for p in S.iterdir():
 if p.is_file():(D/p.name).write_bytes(p.read_bytes())
(D/'launch_storage_contract.py').write_text('from pathlib import Path\ndef parent_five_storage(runtime_root,case_root):\n return Path(runtime_root)/"kit_isolation"\n',encoding='utf-8',newline='\n')
p=D/'worker_five_original_n80.py';s=p.read_text(encoding='utf-8');s=s.replace('from parallel_eval_safe import task_args,put,WholeCheckpointFreshCache,wait_start','from parallel_eval_safe import task_args,put,WholeCheckpointFreshCache,wait_start\nfrom launch_storage_contract import parent_five_storage');assert "storage=out/'kit_isolation'"in s;s=s.replace("storage=out/'kit_isolation'","storage=parent_five_storage(B,out)")
anchor="robot=env.scene['robot'];guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor);guard.assert_new_nominals_unchanged();env.reset()";assert anchor in s;s=s.replace(anchor,"robot=env.scene['robot'];book=None;e2cycles=None\n  if role=='W35':\n   from rm70_intervals227 import RM70Intervals227\n   book=RM70Intervals227(torch,80,env.device,out,task['source_SHA']);book.install(type(env.command_manager.get_term('twist')))\n  guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=tensor);guard.assert_new_nominals_unchanged();env.reset()\n  if book is not None:book.arm(env,env.command_manager.get_term('twist'))")
s=s.replace('(env.recovery.delta>0)&first_episode_live','env.recovery.credited&first_episode_live');s=s.replace('book=None;e2cycles=None\n  if role==\'E2\':','if role==\'E2\':');block="  if role=='W35':\n   from rm70_intervals227 import RM70Intervals227\n   book=RM70Intervals227(torch,80,env.device,out,task['source_SHA']);book.install(type(env.command_manager.get_term('twist')));book.arm(env,env.command_manager.get_term('twist'))\n";assert block in s;s=s.replace(block,'');s=s.replace("put(out/'WORKER_ERROR.json',dict(role=role,epoch=time.time(),controls_completed=completed,error=traceback.format_exc(),no_retry_samepurpose=True))","put(out/'WORKER_ERROR.json',dict(role=role,epoch=time.time(),controls_completed=completed,error=traceback.format_exc(),source_cache=(cache.receipt() if cache is not None else None),no_retry_samepurpose=True))");ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n')
# Launchonlyoriginalsmalllauncherclasses underanAppLauncherstdstub. NeverimportSDK.
class Stub:
 def _create_app(self):self.base_called=True
fake=types.ModuleType('isaaclab');app=types.ModuleType('isaaclab.app');app.AppLauncher=Stub;sys.modules['isaaclab']=fake;sys.modules['isaaclab.app']=app
sys.path.insert(0,str(D));from launch_storage_contract import parent_five_storage
base=R/'diagnostics/NINE_V3_LAUNCHER_DRYRUN_FIXTURES';assert not base.exists();base.mkdir(parents=True);rows=[]
files={k:R/('staged_sources/'+k+'_MOD4V1_SOURCE_'+('FINAL'if k in('E0','E3')else'V1'))/f'runtime/isaac/mod4/launcher_mod4v1_{k.lower()}.py'for k in('E0','E2','E3')};files['W35']=R/'diagnostics/NINE_V3_EXACT_LAUNCHER_SOURCES/W35/runtime/isaac/mod4/launcher208.py';files['H1_normal']=R/'diagnostics/NINE_V3_EXACT_LAUNCHER_SOURCES/H1_normal/lib/zonglin2_app_launcher.py'
for role in('CURB_PROTECTED878','CURB_INDEPENDENT113','SLOPE135','SLOPE_INDEPENDENT50'):files[role]=R/'E1_actual_qualification_v1/SLOPE135_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4/launcher_mod4v1_e1_actual.py'
oldenv=dict(os.environ)
try:
 for role,f in files.items():
  raw=f.read_bytes();src=raw.decode('utf-8');ns={};exec(compile(src,str(f),'exec'),ns);classes=[v for v in ns.values()if isinstance(v,type)and v is not Stub and issubclass(v,Stub)];assert len(classes)==1;cls=classes[0];case=base/'cases'/role;runtime=base/'runtimes'/role;case.mkdir(parents=True);runtime.mkdir(parents=True);is_e1=role.startswith('CURB')or role.startswith('SLOPE');owner=case if is_e1 else runtime;kit=case/'kit_isolation'if is_e1 else parent_five_storage(runtime,case);kit.mkdir()
  if role=='W35':os.environ.update(MOD4_NEW208_JOB_ROOT=str(owner),MOD4_W35_OWN_KIT_STORAGE_ROOT=str(kit))
  elif role in('E0','E2','E3'):os.environ.update({f'MOD4V1_{role}_JOB_ROOT':str(owner),f'MOD4V1_{role}_KIT_STORAGE_ROOT':str(kit)})
  elif is_e1:os.environ.update(MOD4V1_E1_ACTUAL_JOB_ROOT=str(owner),MOD4V1_E1_KIT_STORAGE_ROOT=str(kit))
  inst=cls();inst._sim_app_config={};inst._create_app();assert inst.base_called
  negative=None
  if role in('E0','E2','E3','W35'):
   wrong=case/'wrong_sibling_kit';wrong.mkdir();key='MOD4_W35_OWN_KIT_STORAGE_ROOT'if role=='W35'else f'MOD4V1_{role}_KIT_STORAGE_ROOT';os.environ[key]=str(wrong)
   try:obj=cls();obj._sim_app_config={};obj._create_app();raise AssertionError('OriginalstrictlauncherfailedtoenforcesamejobKit')
   except ValueError:negative='ORIGINAL_SIBLING_STORAGE_ERROR_REPRODUCED_NO_SDK'
  rows.append({'role':role,'source':str(f),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'original_launcher_dry_contract_passed':True,'strict_Kit_guard':role!='H1_normal','owner':str(owner),'kit':str(kit),'wrong_sibling_negative':negative,'H1_uses_case_unique_HOME_not_portable_root_claim':role=='H1_normal'})
finally:os.environ.clear();os.environ.update(oldenv);sys.modules.pop('isaaclab.app');sys.modules.pop('isaaclab')
assert len(rows)==9 and all(r['original_launcher_dry_contract_passed']for r in rows);allfiles=[]
for p in D.glob('*.py'):
 raw=p.read_bytes();ast.parse(raw.decode('utf-8'));allfiles.append(dict(relative=p.name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
proof={'kind':'V3_9_ACTUAL_ORIGINAL_LAUNCHER_CONTRACT_STUB_TESTS_NO_SDK','rows':rows,'files':allfiles,'wrong_sibling_negative_tests':4,'SDK_PT_GPU_canonical_calls':0,'W35_book_hook_before_ONE_reset':True,'H1_no_portable_root_guard_in_originallauncher':True,'V2_failed_beforephysics_oldsourceimmutable':True};(D/'PARENT_FIVE_SOURCE_INDEX_V4.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
s=(R/'stage_and_dispatch_nine_single_gpu_eval_v2_once.py').read_text(encoding='utf-8').replace('NINE_N80_PARALLEL_SOURCE_V2','NINE_N80_PARALLEL_SOURCE_V3').replace('PARENT_FIVE_SOURCE_INDEX_V3.json','PARENT_FIVE_SOURCE_INDEX_V4.json').replace('NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V2.json','NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V3.json').replace('MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V2_','MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V3_');p=R/'stage_and_dispatch_nine_single_gpu_eval_v3_once.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n')
s=(R/'collect_nine_single_gpu_v2_until_closed_once.py').read_text(encoding='utf-8').replace('NINE_GROUP_V2_COLLECTOR_CONSUMED','NINE_GROUP_V3_COLLECTOR_CONSUMED').replace('NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V2','NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V3').replace('NINE_SINGLE_GPU_V2_CLOSED','NINE_SINGLE_GPU_V3_CLOSED').replace('NINE_SINGLE_GPU_V2_LATEST','NINE_SINGLE_GPU_V3_LATEST');p=R/'collect_nine_single_gpu_v3_until_closed_once.py';assert not p.exists();ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n');print('V3_SOURCE_AST_ALL9_LAUNCHER_CONTRACTS_PASS / 4priorpathfailuresreproducedwithoutSDK / no oldsourcepatch / readyfornewgroup')
