from pathlib import Path
import importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def main():
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 c=None;put('SOURCE210_DEPS_PREFLIGHT_MISSING_STARTED_ACTUAL.json',dict(epoch=time.time(),read_only_mount_free_and_exact_destination_stat=True,no_model_GPU_budget_or_mutation=True))
 try:
  c=route.connect();code="from pathlib import Path;import json,shutil,subprocess,time;D=Path('/home/egde/rl_candidates/mod4_owner72_control_deps_v86_20261026');owned=D.parent;durable=Path('/mnt/mod4_linux_durable_20261013');mount=json.loads(subprocess.check_output(['findmnt','--json','--target',str(durable),'--output','SOURCE,TARGET,UUID,FSTYPE,OPTIONS'],text=True))['filesystems'][0];print(json.dumps(dict(epoch=time.time(),destination=str(D),destination_exists=D.exists(),owned_exists=owned.exists(),owned_free=shutil.disk_usage(owned).free,durable_free=shutil.disk_usage(durable).free,mount=mount,destination_within_owned=D.resolve().is_relative_to(owned.resolve()),original_assertions=dict(destination_unused=not D.exists(),home_free100MiB=shutil.disk_usage(owned).free>100*1024**2,UUID_exact_case=mount['uuid']=='EF3105C85DD986BD',mount_rw='rw' in mount['options'].split(','),durable25GiB=shutil.disk_usage(durable).free>25*1024**3),no_mutation=True)))"
  result=d.code(c,route.PY,code,{},timeout=45);put('SOURCE210_DEPS_PREFLIGHT_MISSING_RETURNED_ACTUAL.json',result);print(json.dumps(result))
 finally:
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('SOURCE210_DEPS_PREFLIGHT_MISSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
