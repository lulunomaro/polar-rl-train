"""NEW92 W35 copy+exact assertion-baseline source extension; no PT decode/hash or GO."""
from pathlib import Path,PurePosixPath
import sys,json,time,os,traceback,hashlib,importlib.util
HERE=Path(__file__).resolve().parent;W=HERE.parents[2];L=HERE.parent;R=HERE/'reports'
OLD='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_2610v91/w35'
NEW='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_PPO50_GAS400_RETENTION_2610v92/w35'
COPY=r"""from pathlib import Path
import os,json,shutil,time,hashlib,subprocess,psutil
old=Path(v['old']);new=Path(v['new']);tasks=Path('/home/lc01/Zonglin Li/zonglin2/tasks');assert new.resolve().is_relative_to(tasks) and not new.parent.exists()
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'
line=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();apps=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True);a=[x.strip() for x in line.split(',')];assert a[0]==v['GPU'] and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and v['GPU'] not in apps
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(tasks).free>25*1024**3
base=old/'W35_ACTUAL_POSTCOPY_ALL_SOURCE_SHA_VERIFIED.json';verified=json.loads(base.read_bytes());assert verified['passed'] is True;prior={r['relative']:r for r in verified['files']}
new.parent.mkdir();new.mkdir();rows=[]
for r in v['rows']:
 rel=r['relative'];src=old/rel;dest=new/rel;assert dest.resolve().is_relative_to(new)
 if rel=='runtime/isaac/mod4/retention_checkpoint.py':continue
 assert rel in prior and prior[rel]['bytes']==r['bytes'] and prior[rel]['SHA']==r['SHA']
 before=src.stat();assert before.st_size==r['bytes'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest);after=src.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns) and dest.stat().st_size==r['bytes']
 rows.append(dict(relative=rel,bytes=r['bytes'],original_actual_producer_SHA=r['SHA'],copy_source_stat_unchanged=True,model_not_deserialized_or_rehashed=True))
print(json.dumps(dict(passed=True,new_job_root=str(new),rows=rows,actual_GPU_line=line,selected_compute_UUID_rows=0,original_remaining_snapshot=c['remaining_training_seconds'],no_model_decode_hash_GPU_or_ledger_write=True)))
"""
PUBLISH=r"""from pathlib import Path
import json,hashlib,time,importlib.metadata as md
old=Path(v['old']);new=Path(v['new'])
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
base=old/'W35_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json';proof=old/'W35_SOURCE_CPU_WAITED_ACTUAL_V1.json';assert H(base)=='d022ee93254dbf268c9b743ca0624951680b3f17e9ac791b317a95e2794f35cc' and H(proof)=='d932530973730ac7220274b61b62a006a2198a2693ac06680d372ef71a09941a'
oldfile=old/'runtime/isaac/mod4/retention_checkpoint.py';newfile=new/'runtime/isaac/mod4/retention_checkpoint.py';a=oldfile.read_bytes();b=newfile.read_bytes();needle=b'episode=env._e1_episode.clone();old=g.resume_e1_new_episode';replacement=b"episode=ck['E1_terrain_state']['episode'].to(env.device).clone();old=g.resume_e1_new_episode";assert a.count(needle)==1 and b.replace(replacement,needle)==a and H(oldfile)=='8f1c1f0f0f0af8cd30cefa94e4c9ea1b2139625ce55bf8af293dfa63657030f7' and H(newfile)=='8d3a49766a076f508118b5f84c4a1e9557d6e8a84369b9502516827336604894'
assert H(new/'W35_RETENTION_BASELINE_V2_COMPLETE_INSTALL_MANIFEST.json')==v['manifest_SHA']
for r in v['rows']:
 p=new/r['relative'];assert p.stat().st_size==r['bytes']
 if not r['relative'].endswith('.pt'):assert H(p)==r['SHA']
versions={k:md.version(k) for k in ['torch','isaacsim','isaaclab','rsl-rl-lib']};assert versions=={'torch':'2.10.0+cu128','isaacsim':'6.0.1.0','isaaclab':'6.1.14','rsl-rl-lib':'5.0.1'}
value=dict(passed=True,kind='MOD4_W35_PPO50_GAS400_FULLSTATE_SOURCE_CPU_V1',source_migration_kind='W35_RETENTION_SAVED_EPISODE_WITNESS_BASELINE_ONLY_V2',source_SHA='36825921fb3e4a368791be7802c8ff16977e899240ac21ed2c067b2287bb9393',worker_SHA='0ec27aae56bba060bac4ca1b68c5e977ad89da6c6abda0272bc46596460b6254',base_actual_fullstate_CPU_SHA=H(base),base_actual_fullstate_CPU_path=str(base),base_actual_fullstate_CPU_value=json.loads(base.read_bytes()),base_actual_waited_proof_SHA=H(proof),new_job_root=str(new),old_retention_file_SHA=H(oldfile),new_retention_file_SHA=H(newfile),inverse_single_expression_bytes_exact=True,original_g3_reset_RNG_action_optimizer_reward_code_unchanged=True,no_model_reload=True,no_new_fullstate_CPU_load_claim=True,actual_CUDA_fullrestore_pending=True,payload_manifest_SHA=v['manifest_SHA'],failed91_resource_cost_only=True,failed91_original_fee_seconds=488.166357755661,source_only_target_package_versions=versions,copy_receipt=v['copy_receipt'],model_postcopy_hash_deferred_to_original_unchanged_worker_guard=True,epoch=time.time())
p=new/'W35_RETENTION_BASELINE_ONLY_SOURCE_EXTENSION_ACTUAL_V2.json'
with p.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(passed=True,source_CPU_SHA=H(p),report_path=str(p),report_text=p.read_text(),no_model_reload_or_rehash_or_newCPU=True)))
"""
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert len(sys.argv)==1;save('W35_FIXED92_SOURCE_EXTENSION_ENTERED_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),script=str(Path(__file__).resolve()),no_model_CPU_GPU_or_GO=True))
 manifest=HERE/'W35_RETENTION_BASELINE_V2_COMPLETE_INSTALL_MANIFEST.json';m=json.loads(manifest.read_bytes());rows=[dict(relative=r['installed_relative'],bytes=r['bytes'],SHA=r['SHA']) for r in m['small_source_files']+m['binary_dependencies']];rows.append(dict(relative=m['model']['installed_relative'],bytes=m['model']['bytes'],SHA=m['model']['SHA']))
 path=W/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py';sp=importlib.util.spec_from_file_location('same_authorized_zstd_memory_W35_fixed92_only',path);adapter=importlib.util.module_from_spec(sp);sp.loader.exec_module(adapter);transport,previous=adapter.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('same_authorized72_memory_fixed92_source',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec);secret=sec.recover();c=None
 try:
  c=d.connect72(secret);secret=None;copy=d.code(c,d.PY72,COPY,dict(old=OLD,new=NEW,rows=rows,GPU='GPU-16828f91-2b45-b646-8dc0-9481138e2842'),timeout=60);save('W35_FIXED92_VERIFIED_SOURCE_COPY_ACTUAL.json',copy)
  sf=c.open_sftp();sf.get_channel().settimeout(30)
  try:
   for local,target in [(L/'W35_v91_retention_saved_episode_baseline_fix_source_v1/retention_checkpoint_saved_episode_baseline_v2.py',NEW+'/runtime/isaac/mod4/retention_checkpoint.py'),(manifest,NEW+'/'+manifest.name)]:
    with Path(local).open('rb') as inp,sf.open(target,'wx') as out:out.write(inp.read())
  finally:sf.close()
  value=d.code(c,d.PY72,PUBLISH,dict(old=OLD,new=NEW,rows=rows,manifest_SHA=hashlib.sha256(manifest.read_bytes()).hexdigest(),copy_receipt=copy),timeout=60)
  raw=value.pop('report_text');assert hashlib.sha256(raw.encode()).hexdigest()==value['source_CPU_SHA'];(R/'W35_RETENTION_BASELINE_ONLY_SOURCE_EXTENSION_ACTUAL_V2.json').write_text(raw,encoding='utf8',newline='')
  save('W35_FIXED92_SOURCE_EXTENSION_RETURNED_ACTUAL.json',value);print(json.dumps(value))
 finally:
  secret=None
  if c:c.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:save('W35_FIXED92_SOURCE_EXTENSION_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_rearm91_or_second_writer=True));raise
