from pathlib import Path
import hashlib,json,importlib.util,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;F=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/H1_99_STANCE_GOAL_AND_CLEAN_START_SOURCE_V1';R=F/'reports';R.mkdir(parents=True,exist_ok=True)
REMOTE='/mnt/mod4_linux_durable_20261013/H1step270_own_fudan_native_2610v87r5/h1/job0/production/control_prefix_raw/preupdate_fullsource_0.pt';SHA='5fb246002e39d487ca7b4ad3b5d4171f8065b0ce7ddf26368a95944e4eb32a1d';BYTES=97824121;LOCAL=F/'restart_input/earliest_native87R5_h1_before_control0.pt'
def put(n,x):
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 index=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027/current_native87R5_closed_text/h1/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json';v=json.loads(index.read_bytes());row=v['preupdate_full_sources'][0];retained=v['retention_status'][0]
 assert row==dict(path=REMOTE,bytes=BYTES,SHA=SHA,before_control=0,no_optimizer_call=True) and retained['preupdate_path']==REMOTE and retained['preupdate_retained'] and retained['protected']
 assert not LOCAL.exists();LOCAL.parent.mkdir()
 put('USER_EARLIEST_NATIVE0_RESTART_SOURCE_PURPOSE_STARTED_ACTUAL.json',dict(epoch=time.time(),purpose='Human requested an earliest-checkpoint restart comparison after repeated zero jumps; one protected before-control0 source retrieval, not statistics or Git',original_producer=row,retention_snapshot=retained,model_decode_planned_later_separate_CPU_admission=True,no_GPU_physics_or_account=True))
 helper=module('clean99_same_authorized_compressed_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=helper.install();client=None
 try:
  sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
  sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
  client=route.connect()
  proof=d.code(client,route.PY,"""from pathlib import Path
import hashlib,json,subprocess,time
p=Path(v['path']);base=Path('/mnt/mod4_linux_durable_20261013/H1step270_own_fudan_native_2610v87r5/h1/job0/production/control_prefix_raw');assert p.parent==base and not p.is_symlink() and p.resolve().is_relative_to(base.resolve())
mount=subprocess.check_output(['findmnt','-rn','-o','UUID,FSTYPE,OPTIONS','--target',str(p)],text=True).strip();assert 'EF3105C85DD986BD' in mount.upper() and 'rw' in mount.split()[-1].split(',')
a=p.stat();assert p.is_file() and a.st_size==v['bytes']
with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
b=p.stat();assert sha==v['SHA'] and (a.st_size,a.st_mtime_ns)==(b.st_size,b.st_mtime_ns)
print(json.dumps(dict(passed=True,path=str(p),bytes=a.st_size,SHA=sha,source_stat_unchanged=True,original_mount=mount,epoch=time.time(),no_model_decode_GPU_physics_process_or_account_IO=True)))""",row,timeout=70)
  put('EARLIEST_NATIVE0_ORIGINAL_SOURCE_STAT_SHA_READONLY_ACTUAL.json',proof)
  sf=client.open_sftp();sf.get_channel().settimeout(90)
  try:before=sf.stat(REMOTE);sf.get(REMOTE,str(LOCAL));after=sf.stat(REMOTE)
  finally:sf.close()
  with LOCAL.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
  assert digest==SHA and LOCAL.stat().st_size==BYTES and before.st_size==after.st_size==BYTES and before.st_mtime==after.st_mtime
  put('EARLIEST_NATIVE0_ONE_TRANSFER_TWOHOST_SHA_RETURNED_ACTUAL.json',dict(passed=True,epoch=time.time(),original_producer=row,local_path=str(LOCAL),bytes=BYTES,SHA=SHA,new_concrete_restart_source_transfer_count=1,twohost_fullSHA=True,source_stat_unchanged=True,no_model_decoded_no_GPU_physics_account_or_source_mutation=True,CPU_qualification_pending=True))
  print(json.dumps(dict(passed=True,earliest_before_control0_source_retrieved=True,bytes=BYTES,SHA=SHA,not_yet_CPU_qualified=True)))
 finally:
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('EARLIEST_NATIVE0_FETCH_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_stage_rerun_or_partial_promotion=True));raise
