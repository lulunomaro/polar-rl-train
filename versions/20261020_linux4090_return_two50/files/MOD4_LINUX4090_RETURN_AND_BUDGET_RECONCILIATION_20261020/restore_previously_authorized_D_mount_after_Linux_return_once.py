from pathlib import Path
import json,os,sys,time,traceback
import strict_original_Linux_transport_memory as t
B=Path(__file__).resolve().parent;R=B/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import json,os,shutil,subprocess,time
target=Path('/mnt/mod4_linux_durable_20261013');system=Path('/mnt/mod4_windows_readonly_20261013/system')
def run(cmd,**kw):
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=45,**kw);return dict(returncode=r.returncode,stdout=r.stdout.strip(),stderr=r.stderr.strip())
before=run(['lsblk','-b','-J','-o','PATH,FSTYPE,LABEL,UUID,SIZE,MOUNTPOINTS']);assert before['returncode']==0;flat=[]
def flatten(xs):
 for x in xs:flat.append(x);flatten(x.get('children',[]))
flatten(json.loads(before['stdout'])['blockdevices']);d=next(x for x in flat if x['uuid']=='EF3105C85DD986BD');assert d['fstype']=='ntfs' and int(d['size'])==356164640256;dev=d['path'];assert target.exists()
system_before=run(['findmnt','-T',str(system),'-J'])
if os.path.ismount(system):assert 'ro' in json.loads(system_before['stdout'])['filesystems'][0]['options'].split(',')
if target.is_mount():
 mounted=dict(returncode=0,stdout='already mounted; no mount attempted',stderr='')
else:
 assert not any(target.iterdir()),'Do not cover unexpected root filesystem output';assert not any(d.get('mountpoints') or []),'Do not alter another mount';options=f'rw,uid={os.getuid()},gid={os.getgid()},umask=077,windows_names'
 mounted=run(['sudo','-S','-p','','mount','-t','ntfs3','-o',options,dev,str(target)],input=v['password']+'\n');v['password']=None;assert mounted['returncode']==0,mounted
after=run(['findmnt','-T',str(target),'-J']);f=json.loads(after['stdout'])['filesystems'][0];assert f['source']==dev and f['target']==str(target) and 'rw' in f['options'].split(',') and target.is_mount();assert (target/'T3sf17_1910v22/e2/NODE_EXIT_ACTUAL.json').is_file();assert run(['findmnt','-T',str(system),'-J'])==system_before
print(json.dumps(dict(epoch=time.time(),operation='restore_previous_authorized_D_data_mount_only',partition=d,lsblk=before,mount_result=mounted,actual_findmnt=after,durable_free_bytes=shutil.disk_usage(target).free,old17_E2_exit_found=True,system_mount_unchanged=True,no_force_or_hiberfile_or_fstab_or_system_mount_change=True,no_GPU_or_canonical_write=True)))
'''
def main():
 put('RETURNED_LINUX_D_MOUNT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,prior_explicit_D_mount_authority_reused_after_reboot=True));c=t.connect();secret=None
 try:
  sys.path.insert(0,str(B.parent/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover;secret,_=recover('RM_SSH_PASSWORD');assert secret;v=t.code(c,CODE,dict(password=secret),timeout=90);secret=None;put('PREVIOUSLY_AUTHORIZED_D_MOUNT_AFTER_LINUX_RETURN_ACTUAL.json',dict(epoch=time.time(),actual=v,actual_finite_transport_returned=True));print(json.dumps(dict(restored=True,durable_free_bytes=v['durable_free_bytes'],old17_E2_exit_found=True)),flush=True)
 finally:secret=None;c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('RETURNED_LINUX_D_MOUNT_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),no_force_or_repeat_once=True));raise
