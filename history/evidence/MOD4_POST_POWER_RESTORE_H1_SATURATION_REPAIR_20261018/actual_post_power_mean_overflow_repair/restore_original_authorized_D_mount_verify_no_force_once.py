"""Restore only the previously authorized Windows D data mount after power loss."""
from pathlib import Path
import sys,json,time,os,traceback,importlib.util
B=Path(__file__).resolve().parent;R=B/'reports';sp=importlib.util.spec_from_file_location('pure_boundary',B/'collect_restored_original_canonical_locks_GPU_backend_readonly_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);a=m.a
CODE=r'''
from pathlib import Path
import subprocess,json,time,os,hashlib,psutil,shutil
target=Path('/mnt/mod4_linux_durable_20261013');dev=Path('/dev/nvme0n1p5');system=Path('/mnt/mod4_windows_readonly_20261013/system')
def run(cmd,**kw):
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=45,**kw);return dict(returncode=r.returncode,stdout=r.stdout.strip(),stderr=r.stderr.strip())
before=run(['lsblk','-b','-J','-o','PATH,FSTYPE,LABEL,UUID,SIZE,MOUNTPOINTS']);assert before['returncode']==0
flat=[]
def collect(xs):
 for x in xs:flat.append(x);collect(x.get('children',[]))
collect(json.loads(before['stdout'])['blockdevices']);d=next(x for x in flat if x['path']==str(dev));s=next(x for x in flat if x['path']=='/dev/nvme0n1p3');assert d['fstype']=='ntfs' and 350000000000<int(d['size'])<370000000000 and int(s['size'])>int(d['size'])
assert target.exists() and not os.path.ismount(target) and not any(target.iterdir()),'Do not cover or delete unexpected root filesystem output'
assert not any(d.get('mountpoints') or []),'Do not unmount another data mount'
system_before=run(['findmnt','-T',str(system),'-J'])
if os.path.ismount(system):assert 'ro' in json.loads(system_before['stdout'])['filesystems'][0]['options'].split(',')
u=os.getuid();g=os.getgid();options=f'rw,uid={u},gid={g},umask=077,windows_names'
mounted=run(['sudo','-S','-p','','mount','-t','ntfs3','-o',options,str(dev),str(target)],input=v['password']+'\n');v['password']=None
after=run(['findmnt','-T',str(target),'-J']);assert mounted['returncode']==0, mounted
f=json.loads(after['stdout'])['filesystems'][0];assert f['source']==str(dev) and f['target']==str(target) and 'rw' in f['options'].split(',') and os.path.ismount(target)
old=target/'H1r_1810v4/owner';terminal=json.loads((old/'COHORT_FINAL.json').read_bytes());exitrow=json.loads((old/'OWNER_EXIT_ACTUAL.json').read_bytes());assert terminal['original_cost_settled'] and exitrow['original_cost_settled']
print(json.dumps(dict(epoch=time.time(),operation='restore_previous_explicitly_authorized_D_only_after_reboot',partition=d,system_partition=s,previous_lsblk=before,mount_result=mounted,actual_findmnt=after,original_owner_terminal=terminal,original_owner_exit=exitrow,D_free=shutil.disk_usage(target).free,old_data_found_without_copy_delete_or_clear=True,system_mount_unchanged=run(['findmnt','-T',str(system),'-J'])==system_before,no_force_remove_hiberfile_fstab_or_system_mount_change=True,no_GPU_or_canonical_write=True)))
'''
def main():
 with (R/'ORIGINAL_D_MOUNT_RESTORE_STARTED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,exclusive_only_actual_alive_transport=True),f,indent=2)
 c=None
 try:
  c=a.t.connect();command=a.t.PY+' -B -c '+"\"import sys,json;v=json.loads(sys.stdin.readline());exec(v['code'])\"";i,o,e=c.exec_command(command,timeout=90);payload=dict(code=CODE,password=os.environ['RM_SSH_PASSWORD']);i.write(json.dumps(payload)+'\n');i.flush();i.channel.shutdown_write();payload.clear();out=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);value=json.loads(out)
  with (R/'ORIGINAL_AUTHORIZED_D_MOUNT_RESTORED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
  print(json.dumps(dict(restored=True,D_free=value['D_free'],old_complete_owner_history_found=True,system_unchanged=value['system_mount_unchanged'])),flush=True)
 except BaseException:
  with (R/'ORIGINAL_D_MOUNT_RESTORE_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_auto_force_or_delete_or_rerun=True),f,indent=2)
  raise
 finally:
  if c:c.close()
if __name__=='__main__':main()
