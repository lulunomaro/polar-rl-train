"""Small source extension from the actual N1 failure; no simulator/model IO."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;L=B.parent
OLD=L/'W35_210_N1_ASSET_COLLIDER_DIAGNOSTIC_SOURCE_V1/diagnose_original_W35_N1_asset_colliders_once.py'
def main():
 raw=OLD.read_bytes();assert hashlib.sha256(raw).hexdigest()=='79701a0ca44e6bb96185b0927189a83e48e5a5d2d5a9a922b6a0c61ba8bcf7b5';s=raw.decode();ops=[]
 def replace(a,b):
  nonlocal s
  assert s.count(a)==1;s=s.replace(a,b);ops.append((a,b))
 replace("original=json.loads((J/'original_run_manifest.json').read_bytes())","""K=J/'kit_isolation';assert not K.exists();K.mkdir()
 for name in ('data','DerivedDataCache'):(K/name).mkdir()
 with (K/'data/user.config.json').open('x') as f:f.write('{}')
 os.environ['MOD4_W35_OWN_KIT_STORAGE_ROOT']=str(K)
 original=json.loads((J/'original_run_manifest.json').read_bytes())""")
 replace("ns=runpy.run_path(str(entry),run_name='W35_original_N1_asset_diagnostic_only')","""import zonglin2_app_launcher as owned_launcher
  assert Path(owned_launcher.__file__).resolve()==J/'lib/zonglin2_app_launcher.py'
  ns=runpy.run_path(str(entry),run_name='W35_original_N1_asset_diagnostic_only')""")
 replace("settings=carb.settings.get_settings();config=[]","""settings=carb.settings.get_settings();config=[]
  keys=('/UJITSO/datastore/localCachePath','/UJITSO/datastore/allowLocalDataStore','/UJITSO/datastore/allowHubDataStore','/UJITSO/datastore/allowGRPCDataStore','/UJITSO/datastore/grpcDnsName','/app/userConfigPath','/physics/cooking/ujitsoCollisionCooking','/physics/cooking/ujitsoRemoteCacheEnabled','/persistent/physics/cooking/ujitsoCookingMaxProcessCount')
  actual={key:settings.get(key) for key in keys}
  put('N1_ACTUAL_OWN_KIT_AND_DATASTORE_PATHS_BEFORE_ENV.json',dict(epoch=time.time(),values={key:repr(value) for key,value in actual.items()},expected_cache=str(K/'DerivedDataCache'),expected_user_config=str(K/'data/user.config.json'),source_user_config_new_empty_owned_file=True,old_effective_datastore_path_was_not_collected=True,no_physics_or_cooking_boolean_written=True))
  assert Path(actual['/UJITSO/datastore/localCachePath']).resolve()==K/'DerivedDataCache'
  assert Path(actual['/app/userConfigPath']).resolve()==K/'data/user.config.json'
  assert actual['/physics/cooking/ujitsoCollisionCooking'] is True and actual['/physics/cooking/ujitsoRemoteCacheEnabled'] is False and actual['/persistent/physics/cooking/ujitsoCookingMaxProcessCount']==16
  assert not actual['/UJITSO/datastore/grpcDnsName'] and not actual['/UJITSO/datastore/allowHubDataStore'], 'Local-path test cannot claim isolation while an external datastore is selected'""")
 replace("put('N1_APP_CLOSING.json',dict(epoch=time.time()))","""try:
   files=[];total=0
   for q in sorted((K/'DerivedDataCache').rglob('*')):
    if not q.is_file():continue
    assert q.resolve().is_relative_to(K/'DerivedDataCache') and not q.is_symlink();total+=1
    if len(files)<64:files.append(dict(relative=q.relative_to(K).as_posix(),bytes=q.stat().st_size))
   put('N1_OWN_NEW_DATASTORE_FILE_METADATA_BEFORE_CLOSE.json',dict(epoch=time.time(),new_owned_cache_only=True,own_cache_file_count=total,first64_metadata=files,metadata_truncated=total>64,cache_contents_not_read=True,old_cache_not_read_deleted_or_changed=True,successful_environment_not_proof_of_unique_root_cause=True))
  except BaseException:put('N1_OWN_CACHE_METADATA_ORIGINAL_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()))
  put('N1_APP_CLOSING.json',dict(epoch=time.time()))""")
 new=s.encode();ast.parse(new);back=s
 for a,b in reversed(ops):assert back.count(b)==1;back=back.replace(b,a)
 assert back.encode()==raw
 target=B/OLD.name;assert not target.exists();target.write_bytes(new)
 value=dict(epoch=time.time(),source_only=True,old_worker_SHA=hashlib.sha256(raw).hexdigest(),new_worker_SHA=hashlib.sha256(new).hexdigest(),exact_inverse_bytes=True,changes=[dict(old=a,new=b) for a,b in ops],unchanged_original_MildDR_constructor_assertion_called=True,original_USD_mesh_DR_force_solver_and_seed_unchanged=True,no_cooking_boolean_toggled=True,no_PT_raw_USD_NPZ_model_or_remote_read=True,new_cache_candidate_not_validated=True)
 (B/'OWN_STORAGE_ONLY_WORKER_SOURCE_EXTENSION_PROOF.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(dict(worker_SHA=value['new_worker_SHA'],exact_inverse_bytes=True,AST=True)))
if __name__=='__main__':main()
