from pathlib import Path
import importlib.util,json,time,traceback
J=Path(__file__).resolve().parent;T=J.parent;N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M_20261026';R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 put('RETURNED210_EXPANDED_STORAGE_MISSING_MOUNTS_STARTED_ACTUAL.json',dict(epoch=time.time(),new_human_added_space_request=True,only_read_block_and_mount_metadata=True,no_raw_model_hash_cleanup_mount_or_budget_write=True))
 sp=importlib.util.spec_from_file_location('defs',T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026/relocate_minimal_closed81O_82Q_NPZ_for83_TLS_V5_unused_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);d=m.d;c=None
 try:
  c=d.t.connect();source="import json,subprocess,time;print(json.dumps(dict(epoch=time.time(),lsblk=json.loads(subprocess.check_output(['lsblk','--json','--bytes','--output','NAME,SIZE,FSTYPE,MOUNTPOINTS,FSAVAIL,UUID'],text=True)),df=subprocess.check_output(['df','-B1','-T','/','/home/egde','/mnt/mod4_linux_durable_20261013'],text=True),findmnt=subprocess.check_output(['findmnt','-n','-o','SOURCE,TARGET,UUID,FSTYPE,OPTIONS','--target','/mnt/mod4_linux_durable_20261013'],text=True),no_mutation_or_recursive_file_search=True)))"
  result=d.code(c,d.t.PY,source,{},timeout=30);put('RETURNED210_EXPANDED_STORAGE_MISSING_MOUNTS_RETURNED_ACTUAL.json',result);print(json.dumps(result))
 except BaseException:
  put('RETURNED210_EXPANDED_STORAGE_MISSING_MOUNTS_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
 finally:
  if c:c.close()
if __name__=='__main__':main()
