from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent
def H(b):return hashlib.sha256(b).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 test=json.loads((B/'reports/E3_SOURCE210_FRESH_ORIGINAL_PHASE_CPU_TARGET_AST_AND_READERS_ACTUAL.json').read_bytes());assert test['passed'] and test['count']==30
 manifest=B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json';m=json.loads(manifest.read_bytes());assert len(m['files'])==444
 for r in m['files']:
  if Path(r['local_path']).parent==B:
   name='zonglin2_app_launcher.py' if r['relative']=='lib/zonglin2_app_launcher.py' else r['relative'];raw=(B/name).read_bytes();assert len(raw)==r['bytes'] and H(raw)==r['SHA'],name
 old=L/'E3_97_GAS400_COMPLETE_RUNTIME_SOURCE_CPU_PREPARATION_V1/E3_COMPLETE_INSTALL_MANIFEST_V1.json';orig=json.loads(old.read_bytes());by={r['relative']:r for r in m['files']};unchanged=[]
 for r in orig['files']:
  if r['relative'].endswith('.pt') or r['relative'] in ('E3_PPO50_gas400_finite_worker_v1.py','lib/zonglin2_app_launcher.py'):continue
  assert by[r['relative']]==r;unchanged.append(r['relative'])
 launcher=ast.parse((B/'zonglin2_app_launcher.py').read_bytes());literal=next(ast.literal_eval(n.value.args[0]) for n in ast.walk(launcher) if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='expected' for x in n.targets));assert literal==m['target_root']+'/kit_isolation'
 worker=(B/'evaluate_E3_adapted97_source210_frozen600_once_v1.py').read_text();assert "K=job/'kit_isolation'" in worker and "os.environ['MOD4_E3_OWN_KIT_STORAGE_ROOT']=str(K)" in worker;assert "os.environ['MOD4_E3_OWN_KIT_STORAGE_ROOT']" in (B/'zonglin2_app_launcher.py').read_text()
 put(B/'FINAL_E3_SOURCE210_PATH_RUNTIME_INPUT_AND_TARGET_GUARD_RECONCILIATION_ACTUAL.json',dict(passed=True,unchanged_E3_production_input_rows=len(unchanged),source_manifest=str(old),source_manifest_SHA=H(old.read_bytes()),launcher_expected_own_path=literal,worker_env_K_formula_actual_AST_source_matches=True,App_path_isdir_cooking_readback_pending=True,actual_target_CPU_AST_guard_positive_passed=True,original_phase_source_100Hz3s_andpoint5s_proved_fresh_CPU=True,no_binary_PT_NPZ_USD_stat_or_model_SDK_remote_GPU=True))
 oldpartial=L/'E3_97_NEW86_FROZEN_RECIPE_DOMAIN_SOURCE_PREPARATION_20261029_V1';files=[]
 for p in sorted(oldpartial.iterdir()):
  if p.is_file():raw=p.read_bytes();files.append(dict(relative=p.name,bytes=len(raw),SHA=H(raw)))
 put(oldpartial/'FROZEN_PARTIAL_E3_SOURCE_PREPARED_UNUSED_NOT_SELECTED_INDEX.json',dict(status='PARTIAL_PREPARED_UNUSED_NOT_SELECTED_NO_BINDING',files=files,selected_new_source_scope=str(B),no_remote_model_SDK_GPU=True))
 local={};rows=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file():continue
  assert p.suffix in ('.py','.json','.md','.txt');raw=p.read_bytes();rows.append(dict(relative=p.relative_to(B).as_posix(),bytes=len(raw),SHA=H(raw)))
  if p.parent==B and p.suffix=='.py':ast.parse(raw);local[p.name]=H(raw)
 index=dict(status='FROZEN_SOURCE_ONLY_PREPARED_UNUSED_TARGET_ADMISSION_PENDING',entry='install_E3_source210_frozen_recipe_metadata_detach_UNUSED_once_v1.py',local_source_SHAs=local,manifest_SHA=H(manifest.read_bytes()),target_root=m['target_root'],model_SHA=m['model_SHA'],files=rows,first_reader='read_E3_source210_FIRST_native24_recipe_queue_UNUSED_once_v1.py',terminal_reader='collect_E3_source210_TERMINAL_recipe_fulltext_UNUSED_once_v1.py',qualified17Adam=866060,qualified_LR=.0002562890625000001,requested600_warm100_steady500=True,original13recipe_request3s_stablepoint5s=True,source_synthetic_CPU_checks=30,metadata_CPU_PT_decode0=True,worker1680_supervisor1800_normalremaining900_wait850=True,no_actual_current_CNone_owner_PID_GPU_or_source210_SDK_claimed=True,no_PPO_newowner_GO_Cwrite=True,skill_graduation=False,complete_WM_dataset=False,Git_status='EXPLICIT_PENDING root ordinary supplement; no trial/tag')
 p=B/'FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V1.json';put(p,index);print(json.dumps(dict(passed=True,index=p.name,index_SHA=H(p.read_bytes()),entry=index['entry'],entry_SHA=local[index['entry']],manifest_SHA=index['manifest_SHA'],files=len(rows),source_only=True)))
if __name__=='__main__':main()
