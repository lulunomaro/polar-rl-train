from pathlib import Path
import ast,hashlib,json,time
S=Path(__file__).resolve().parent;T=S.parent
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 prior=json.loads((S/'reports/FROZEN_NATIVE86_SINGLE_COMPLETE_ATTEMPT_RETURNED_ACTUAL.json').read_bytes())
 assert prior['actual_finite_returned'] and prior['returncode']==1 and prior['all_own_children_actual_out'] and prior['actual_original_SDK_admission'] is None and prior['actual_result'] is None
 assert 'check_eula' in prior['original_error']['error'] and 'EOFError' in prior['original_error']['error']
 D=T/'H1_STEP270_NATIVE86_FULL_SINGLE_ATTEMPT_REPLAY_R2_20261027';D.mkdir();(D/'reports').mkdir()
 q=json.loads((S/'BINDING.json').read_bytes());q['remote_root']='/home/lc01/Zonglin Li/zonglin2/tasks/H1native86_complete_single_replay_20261027r2'
 manifest=json.loads((T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2/THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 q['environment_source_SHA']=next(r['SHA'] for r in manifest['files'] if r['relative']=='three_slot_common_v1.py')
 with (D/'driver.py').open('xb') as f:f.write((S/'driver.py').read_bytes())
 entry=(S/'native86_frozen_single_sdk_entry_v1.py').read_text('utf8')
 old="source=Path(Q['model']['path']);assert source.stat().st_size==Q['model']['bytes'] and H(source)==Q['model']['SHA']"
 new="source=Path(Q['model']['path']);source_bytes=source.read_bytes();assert len(source_bytes)==Q['model']['bytes'] and hashlib.sha256(source_bytes).hexdigest()==Q['model']['SHA']"
 assert entry.count(old)==1;entry=entry.replace(old,new,1)
 old="saved=torch.load(source,map_location='cpu',weights_only=False)";new="import io\n  saved=torch.load(io.BytesIO(source_bytes),map_location='cpu',weights_only=False);del source_bytes"
 assert entry.count(old)==1;entry=entry.replace(old,new,1);ast.parse(entry)
 with (D/'native86_frozen_single_sdk_entry_v1.py').open('x',encoding='utf8',newline='\n') as f:f.write(entry)
 parent=(S/'run_qualified_native86_single_frozen_attempt_on72_finite_unused_once.py').read_text('utf8')
 old="env=dict(os.environ);env['CUDA_VISIBLE_DEVICES']=q['GPU_UUID'];env['CUDA_DEVICE_ORDER']='PCI_BUS_ID'"
 new="""import ast
environment_source=Path(q['source_root'])/'three_slot_common_v1.py'
raw=environment_source.read_bytes();assert hashlib.sha256(raw).hexdigest()==q['environment_source_SHA']
fn=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name=='environment')
(root/'job0').mkdir();scope=dict(os=os,J=root/'job0')
exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(environment_source),'exec'),scope)
env=scope['environment'](dict(GPU_UUID=q['GPU_UUID']));env['CUDA_DEVICE_ORDER']='PCI_BUS_ID'
(root/'EXACT_ORIGINAL_ENVIRONMENT_REUSE_ACTUAL.json').write_text(json.dumps(dict(source_path=str(environment_source),source_SHA=q['environment_source_SHA'],original_environment_function_AST_reused=True,existing_SDK_environment_settings_inherited=True,new_license_or_SDK_not_installed=True)),encoding='utf8')"""
 assert parent.count(old)==1;parent=parent.replace(old,new,1);tree=ast.parse(parent)
 for n in tree.body:
  if isinstance(n,ast.Assign) and any(isinstance(a,ast.Name) and a.id in ('PREP','RUN') for a in n.targets):ast.parse(ast.literal_eval(n.value))
 name='run_native86_replay_R2_original_environment_once.py'
 with (D/name).open('x',encoding='utf8',newline='\n') as f:f.write(parent)
 q['entry_SHA']=H(D/'native86_frozen_single_sdk_entry_v1.py');q['previous_prepolicy_startup_error_preserved']=str(S/'reports/FROZEN_NATIVE86_SINGLE_COMPLETE_ATTEMPT_RETURNED_ACTUAL.json')
 with (D/'BINDING.json').open('x',encoding='utf8') as f:json.dump(q,f,ensure_ascii=False,indent=2)
 record=dict(epoch=time.time(),new_root=str(D),prior_attempt_before_any_model_Pi_forward=True,original_startup_error_retained=True,original_approved_environment_function_reused_byte_pinned=True,same_runtime_SDK_not_different_backend=True,no_new_license_acceptance_prompt_or_flag_invented=True,source_model_bytes_read_once_reused_for_inference_load=True,actual_policy_attempts_so_far=0,not_yet_executed=True)
 with (D/'reports/R2_ORIGINAL_ENVIRONMENT_STARTUP_FIX_SOURCE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(record,f,indent=2)
 old=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v179.py';source=old.read_text('utf8')
 needle="        'run_qualified_native86_single_frozen_attempt_on72_finite_unused_once.py',";assert source.count(needle)==1
 source=source.replace(needle,needle+"\n        '"+name+"',",1);ast.parse(source)
 with old.with_name('same_authorized_session_compressed_transport_v180.py').open('x',encoding='utf8',newline='\n') as f:f.write(source)
 print(json.dumps(record))
if __name__=='__main__':main()
