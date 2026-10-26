from pathlib import Path
import importlib.util,json,time,traceback
J=Path(__file__).resolve().parent;T=J.parent;N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M_20261026';R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import json,os,psutil,shutil,subprocess,time
uuid='EF3105C85DD986BD';dest=Path('/mnt/mod4_expanded_original_EF3105C85DD986BD_20261026');old=Path('/mnt/mod4_linux_durable_20261013')
dev=Path('/dev/disk/by-uuid')/uuid;assert dev.is_symlink() and dev.resolve()==Path('/dev/nvme0n1p5') and not dest.exists()
listing=json.loads(subprocess.check_output(['lsblk','--json','--bytes','--output','NAME,SIZE,FSTYPE,MOUNTPOINTS,UUID'],text=True))
def walk(rows):
 for row in rows:
  yield row
  yield from walk(row.get('children',[]))
row=next(x for x in walk(listing['blockdevices']) if x.get('uuid')==uuid);assert row['fstype']=='ntfs' and row['size']==1032813878784 and not any(row.get('mountpoints') or [])
assert not os.path.ismount(old) and psutil.boot_time()>1792994651.61
for argv in (['sudo','-n','mkdir','-m','0755',str(dest)],['sudo','-n','mount','-t','ntfs3','-o','ro','--uuid',uuid,str(dest)]):
 r=subprocess.run(argv,capture_output=True,text=True);assert r.returncode==0,dict(command=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
mount=subprocess.check_output(['findmnt','-n','-o','UUID,FSTYPE,OPTIONS','--target',str(dest)],text=True).strip();assert uuid in mount.upper() and 'ntfs3' in mount and 'ro' in mount.split()[-1].split(',')
files={}
for rel in ('H1step270_three_experts_2610v83b/h1/job0/production/model_update130.pt','H1step270_three_experts_2610v83b/owner/OWNER_EXIT_ACTUAL.json','H1step270_three_experts_2610v83b/owner/COHORT_FINAL.json'):
 p=dest/rel;files[rel]=dict(exists=p.is_file(),bytes=p.stat().st_size if p.is_file() else None)
 if p.is_file() and p.suffix=='.json' and p.stat().st_size<300000:files[rel]['value']=json.loads(p.read_bytes())
usage=shutil.disk_usage(dest);print(json.dumps(dict(epoch=time.time(),read_only_mount_created=True,new_mountpoint=str(dest),mount=mount,free=usage.free,total=usage.total,known83B_exact_paths_stat_and_smalltext=files,no_model_or_raw_content_hash=True,no_original_mountpoint_or_ledger_write_or_delete=True)))
'''
def main():
 put('ORIGINAL_EXPANDED_NTFS_READONLY_NEW_MOUNT_STARTED_ACTUAL.json',dict(epoch=time.time(),user_added_capacity=True,original_UUID='EF3105C85DD986BD',fresh_known_unmounted_device='/dev/nvme0n1p5',new_readonly_mount=True,no_old_path_overlay_or_budget_action=True))
 sp=importlib.util.spec_from_file_location('defs',T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83_20261026/relocate_minimal_closed81O_82Q_NPZ_for83_TLS_V5_unused_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);d=m.d;c=None
 try:
  c=d.t.connect();result=d.code(c,d.t.PY,CODE,{},timeout=45);put('ORIGINAL_EXPANDED_NTFS_READONLY_NEW_MOUNT_RETURNED_ACTUAL.json',result);print(json.dumps({k:result[k] for k in ('read_only_mount_created','new_mountpoint','mount','free','total')}))
 except BaseException:
  put('ORIGINAL_EXPANDED_NTFS_READONLY_NEW_MOUNT_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_force_ntfsfix_unmount_delete_or_assumed_success=True));raise
 finally:
  if c:c.close()
if __name__=='__main__':main()
