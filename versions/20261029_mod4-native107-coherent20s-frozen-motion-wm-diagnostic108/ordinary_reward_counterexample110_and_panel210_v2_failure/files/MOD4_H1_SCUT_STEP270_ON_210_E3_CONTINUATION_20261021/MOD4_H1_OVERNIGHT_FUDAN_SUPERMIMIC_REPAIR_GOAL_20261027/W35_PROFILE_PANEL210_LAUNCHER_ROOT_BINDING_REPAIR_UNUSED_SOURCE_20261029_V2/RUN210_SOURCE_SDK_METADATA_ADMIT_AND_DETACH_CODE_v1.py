
from pathlib import Path
import base64,fcntl,hashlib,importlib.metadata as md,importlib.util,json,math,os,psutil,subprocess,time
os.environ['CUDA_VISIBLE_DEVICES']='';J=Path(v['job']);lockpath=Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock')
for key,name in {'HOME':'home','TMPDIR':'tmp','TMP':'tmp','TEMP':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda'}.items():
 p=J/name;p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
os.environ['PYTHONDONTWRITEBYTECODE']='1'
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(n,x):
 with (J/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
copyproof=v['copyproof'];assert copyproof['passed'] and copyproof['old_source_wholeCPU_and_closure_bound']
linked={x['relative']:x for x in copyproof['records'] if x['large_readonly_input_same_inode']}
for row in v['files']:
 p=(J/row['relative']).resolve();assert p.is_relative_to(J) and not p.is_symlink() and p.stat().st_size==row['bytes']
 if row['relative'] in linked:
  old=Path(v['old'])/row['relative'];before=linked[row['relative']];assert os.path.samestat(old.stat(),p.stat()) and p.stat().st_mtime_ns==before['source_mtime_ns'] and before['producer_SHA']==row['SHA']
 else:assert H(p)==row['SHA']
witness=J/'W35_EXISTING_FORMAL_WHOLE_CPU_WITNESS.json';assert H(witness)==v['expected']['wholeCPU_SHA'];whole=json.loads(witness.read_bytes());assert whole['passed'] and whole['model']['SHA']==v['expected']['model_SHA'] and whole['model']['original_producer']['Adam_step']==648360
assert H(J/'PANEL210_SEALED_INPUT_MANIFEST.json')==v['input_manifest_SHA']
versions={k:md.version(k) for k in ['torch','isaacsim','isaaclab','rsl-rl-lib']};assert versions=={'torch':'2.10.0+cu128','isaacsim':'6.0.1.0','isaaclab':'6.1.14','rsl-rl-lib':'5.0.1'}
rsl=Path(importlib.util.find_spec('rsl_rl').origin).parent;lab=Path(importlib.util.find_spec('isaaclab').origin).parent
for row in v['RSL_sources']:assert (rsl/row['relative']).stat().st_size==row['bytes'] and H(rsl/row['relative'])==row['SHA']
assert H(lab/'utils/math.py')==v['SDK_math_SHA']
assert (J/'runtime/assets/import_contract.json').read_bytes()==(J/'runtime/isaac/mod4/import_contract.json').read_bytes()
from pxr import Usd,UsdPhysics
stage=Usd.Stage.Open(str(J/'runtime/assets/robot.usd'));assert stage
for name in ['left_gas_slide','right_gas_slide']:
 p=stage.GetPrimAtPath('/Robot/joints/'+name);d=UsdPhysics.DriveAPI.Get(p,'linear');q=UsdPhysics.PrismaticJoint(p)
 assert d.GetStiffnessAttr().Get()==2000 and d.GetDampingAttr().Get()==3 and math.isclose(q.GetUpperLimitAttr().Get(),.020639440248416612,abs_tol=1e-8)
cpu=dict(passed=True,epoch=time.time(),scope='NEW profile-panel source/SDK/USD CPU metadata qualification; exact historical final78 wholeCPU witness, no model decode',versions=versions,RSL_source_bytes_exact=True,SDK_math_source_bytes_exact=True,asset_parent_contract_route_exact=True,nominal400_USD_composition=True,source_model_GPU_fullrestore_still_pending=True,wholeCPU_witness_SHA=v['expected']['wholeCPU_SHA'],source_model_SHA=v['expected']['model_SHA'],actual_model_CPU_decode_count=0,same_inode_producer_metadata_bound=copyproof['old_source_wholeCPU_and_closure_bound'],static_task_source_preserved=True,input_manifest_SHA=v['input_manifest_SHA'],panel_source_overlay=v['source_extension'])
import ast
launcher_source=J/'lib/zonglin2_app_launcher.py';launcher_ast=ast.parse(launcher_source.read_bytes())
expected_literal=next(ast.literal_eval(n.value.args[0]) for n in ast.walk(launcher_ast) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='expected' for t in n.targets))
assert expected_literal==str(J/'kit_isolation') and H(launcher_source)==v['source_extension']['launcher_namespace_binding']['new_launcher_SHA']
cpu['launcher_root_binding_metadata']=dict(passed=True,expected=expected_literal,worker_env_formula="str(job/'kit_isolation')",launcher_SHA=H(launcher_source),original_guard_retained=True,actual_App_launcher_path_and_isdir_guard_still_pending=True)
put('ACTUAL_SOURCE210_SOURCE_SDK_CPU_NO_MODEL_ADMISSION.json',cpu)

task=json.loads((J/v['static_task_input']).read_bytes());assert task['kind']=='MOD4_W35_ADAPTED92_PROFILE_ENV_DOMAIN_PANEL_V1' and task['controls']==600 and task['warmup_controls']==100 and task['num_envs']==20000 and task['source_SHA']==v['expected']['model_SHA']
assert task['actual_source210_SDK_admission_passed'] is False and task['actual_private_GPU_EX_held_by_parent'] is False and task['canonical72_known_owner_readonly_passed'] is False and task['known72_readonly_authority'] is None
assert task['panel_worker_SHA']==H(J/v['worker']) and task['panel_component_SHA']==H(J/'w35_profile_env_domain_panel_v1.py')
assert v['authority']['passed'] and v['authority']['passed_readonly_original72_finite_authority']
task.update(actual_source210_SDK_admission_passed=True,canonical72_known_owner_readonly_passed=True,known72_readonly_authority=v['authority'],actual_source210_python=v['python'])
assert not (J/'FROZEN_CASE_TASK_TEMPLATE.json').exists()
put('FROZEN_CASE_TASK_TEMPLATE.json',task)
env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1');argv=[v['python'],'-u','-B',str(J/v['supervisor']),'--job-root',str(J)]
with (J/'FROZEN_W35_SUPERVISOR_COMPLETE_STDOUT_STDERR.log').open('xb') as log:p=subprocess.Popen(argv,env=env,cwd=J,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
q=psutil.Process(p.pid);identity=dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),root=q.cwd());assert p.poll() is None
put('ACTUAL_FROZEN_W35_FINITE_SUPERVISOR_DETACHED.json',dict(epoch=time.time(),identity=identity,actual_detached=True,worker_maximum_seconds=1680,original_child_wait_seconds=1800,source_SDK_CPU_passed=True,actual_GPU_fullrestore_native24_and_profiles_pending=True,no_optimizer_budget_or_new_GO=True))
print(json.dumps(dict(passed_source_admission_and_detached_only=True,epoch=time.time(),identity=identity,job_root=str(J),source_SDK_CPU=cpu,actual_GPU_fullrestore_native24_and_profile_coverage_pending=True,no_policy_training_or_skill_graduation_claim=True)))
