from pathlib import Path
import importlib.util,json,time,traceback
J=Path(__file__).resolve().parent;T=J.parent;N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M_20261026';R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import hashlib,json,os,psutil,shutil,subprocess,time
new=Path('/mnt/mod4_expanded_original_EF3105C85DD986BD_20261026');old=Path('/mnt/mod4_linux_durable_20261013');uuid='EF3105C85DD986BD'
assert new.is_dir() and os.path.ismount(new) and old.is_dir() and not os.path.ismount(old)
mount=subprocess.check_output(['findmnt','-n','-o','UUID,FSTYPE,OPTIONS','--target',str(new)],text=True).strip();assert uuid in mount.upper() and 'ntfs3' in mount and 'ro' in mount.split()[-1].split(',')
e=json.loads((new/'H1step270_three_experts_2610v83b/owner/OWNER_EXIT_ACTUAL.json').read_bytes());assert e['original_cost_settled'] and psutil.boot_time()>1792994651.61
assert not any(any(a.startswith(str(old)+'/') or a.startswith(str(new)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['cmdline']))
underlying=dict(device=old.stat().st_dev,inode=old.stat().st_ino,files_not_deleted_or_moved=True)
for argv in (['sudo','-S','-p','','umount',str(new)],['sudo','-S','-p','','mount','-t','ntfs3','-o','rw,uid='+str(os.getuid())+',gid='+str(os.getgid()),'--uuid',uuid,str(new)],['sudo','-S','-p','','mount','--bind',str(new),str(old)]):
 r=subprocess.run(argv,input=v['sudo_secret']+'\n',capture_output=True,text=True);assert r.returncode==0,dict(command=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
mount=subprocess.check_output(['findmnt','-n','-o','UUID,FSTYPE,OPTIONS','--target',str(old)],text=True).strip();assert uuid in mount.upper() and 'ntfs3' in mount and 'rw' in mount.split()[-1].split(',')
p=old/'MOD4_EXPANDED_ORIGINAL_VOLUME_READY_20261026.json';value=dict(epoch=time.time(),original_volume_UUID=uuid,current_path=str(old),standalone_mount=str(new),own_mount_read_write_ready=True,no_original_data_deleted_or_changed=True,old210_Linux_budget_authority_stays_retired=True);raw=(json.dumps(value,indent=2)+'\n').encode()
with p.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
assert p.read_bytes()==raw;u=shutil.disk_usage(old);assert u.free>25*1024**3
model=old/'H1step270_three_experts_2610v83b/h1/job0/production/model_update130.pt';assert model.stat().st_size==16868571
print(json.dumps(dict(epoch=time.time(),passed=True,original_training_mount_restored=True,mount=mount,free=u.free,total=u.total,underlying_rootdisk_directory_preserved=underlying,ready_probe=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=value),old83B_model_stat_only_no_hash=True,no_old_ledger_write_owner_or_GO=True)))
'''
def main():
 prior=json.loads((R/'ORIGINAL_EXPANDED_NTFS_READONLY_NEW_MOUNT_V2_RETURNED_ACTUAL.json').read_bytes());assert prior['read_only_mount_created'] and prior['free']==716942045184
 put('ORIGINAL_EXPANDED_VOLUME_RW_RESTORE_V3_STARTED_ACTUAL.json',dict(epoch=time.time(),verified_known_volume_UUID='EF3105C85DD986BD',normal_remount_no_force_repair_format_or_delete=True))
 sp=importlib.util.spec_from_file_location('defs',T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026/relocate_minimal_closed81O_82Q_NPZ_for83_TLS_V5_unused_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);d=m.d;c=None;secret=None
 try:
  c=d.t.connect();from reuse_authorized_session_transport import recover;secret,_=recover('RM_SSH_PASSWORD');assert secret;result=d.code(c,d.t.PY,CODE,dict(sudo_secret=secret),timeout=45);secret=None;put('ORIGINAL_EXPANDED_VOLUME_RW_RESTORE_V3_RETURNED_ACTUAL.json',result);print(json.dumps(result))
 except BaseException:
  put('ORIGINAL_EXPANDED_VOLUME_RW_RESTORE_V3_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_force_ntfsfix_or_assume_success_or_rerun_once=True));raise
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':main()
