from pathlib import Path
import importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent
s=importlib.util.spec_from_file_location('strict210',W/'MOD4_TWO_LINUX_POLICY50_COHORT_50_20261021/strict_original_Linux_transport_memory.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
READ=r'''
from pathlib import Path
import json,os,shutil,subprocess,time
uuid='B6682CFC682CBD4D';dev=Path('/dev/disk/by-uuid')/uuid;target=Path('/mnt/mod4_windows_system_readonly_20261021');assert dev.resolve()==Path('/dev/nvme0n1p3')
raw=subprocess.check_output(['lsblk','-b','-J','-o','NAME,SIZE,FSTYPE,UUID,MOUNTPOINTS',str(dev.resolve())],text=True);info=json.loads(raw)['blockdevices'][0];assert info['uuid']==uuid and info['fstype']=='ntfs' and info['size']==998769688576 and not any(info['mountpoints'])
def sudo(args):
 p=subprocess.run(['sudo','-S','-p','',*args],input=v['sudo_secret']+'\n',capture_output=True,text=True,timeout=30);return dict(argv=args,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
probe=shutil.which('ntfs-3g.probe');rw_probe=sudo([probe,'--readwrite',str(dev)]) if probe else dict(available=False)
assert not target.exists() or target.is_dir() and not any(target.iterdir());mkdir=sudo(['mkdir','-p',str(target)]);assert mkdir['returncode']==0,mkdir
mount=sudo(['mount','-t','ntfs3','-o','ro',str(dev),str(target)])
out=dict(epoch=time.time(),UUID=uuid,device=str(dev.resolve()),partition_size=info['size'],target=str(target),readwrite_probe=rw_probe,mount_readonly=mount,readwrite_mount_not_attempted=True,no_force_hiberfile_fstab_system_file_or_training_change=True)
if mount['returncode']==0:
 opts=subprocess.check_output(['findmnt','-J','--target',str(target)],text=True);usage=shutil.disk_usage(target);out.update(findmnt=json.loads(opts),filesystem_total=usage.total,filesystem_free=usage.free,filesystem_used=usage.used,Windows_directory_exists=(target/'Windows').is_dir(),Users_directory_exists=(target/'Users').is_dir(),readonly_access_actual=True)
print(json.dumps(out))
'''
try:
 with (R/'NTFS999_READONLY_INSPECTION_STARTED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),explicit_user_request='看一下999gb的ntfs分区能用不能'),f,ensure_ascii=False)
 sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
 secret,_=recover('RM_SSH_PASSWORD');assert secret;c=t.connect()
 try:v=t.code(c,READ,dict(sudo_secret=secret),timeout=90)
 finally:secret=None;c.close()
 with (R/'NTFS999_READONLY_INSPECTION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(v))
except BaseException:
 with (R/'NTFS999_INSPECTION_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_force_or_retry=True),f)
 raise
