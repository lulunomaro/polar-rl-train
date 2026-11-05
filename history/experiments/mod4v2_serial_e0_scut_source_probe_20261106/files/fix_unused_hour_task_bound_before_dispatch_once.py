"""Correct the unused owner's duplicated Task value before any dispatch; preserve exact staged source."""
from pathlib import Path
import ast,json,sys,hashlib,shlex
D=Path(__file__).resolve().parent;s=json.loads((D/'STAGE_E0_HOUR_WINDOW_RESULT.json').read_bytes());assert s['returncode']==0 and s['owner_dispatched']is False and not(D/'DISPATCH_E0_HOUR_WINDOW_ONCE.json').exists();p=D/'source_owner_e0_hour_v1/migration_nine_original_owner_v1.py';old=p.read_bytes();text=old.decode();a='max_additional_updates=20,num_envs=20000';assert text.count(a)==1;text=text.replace(a,'max_additional_updates=1000000,num_envs=20000').replace("'Original finite20 windows'","'Original finite wall-clock hour'").replace("'_FULL20K_ORIGINAL20_'","'_FULL20K_ORIGINAL_HOUR_'");ast.parse(text);compile(text,str(p),'exec');new=text.encode();out=D/'HOUR_PRE_DISPATCH_TASK_BOUND_FIX.json';assert not out.exists();sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();ftp=c.open_sftp()
try:
 root=s['root']
 for name in('OWNER_STARTED.json','OUTER_OWNER_IDENTITY.json','OUTER_OWNER_WAIT_ACTUAL.json'):
  try:ftp.stat(root+'/'+name)
  except FileNotFoundError:continue
  raise RuntimeError('Owner already used; no patch permitted')
 with ftp.open(root+'/migration_nine_original_owner_v1.py','rb')as f:assert f.read()==old
 with ftp.open(root+'/OWNER_PLAN.json','r')as f:plan=json.loads(f.read())
 for e in plan['entries']:
  assert e['max_additional_updates']==1000000 and e['window_mode']=='ORIGINAL_FINITE_WALL_CLOCK_HOUR'
  with ftp.open(e['job_root']+'/'+e['manifest_file'],'r')as f:m=json.loads(f.read())
  assert all(x['relative']!='migration_nine_original_owner_v1.py'for x in m['shared_files'])
 backup=D/'attempts/hour_owner_before_dispatch_task_bound20.py';assert not backup.exists();backup.parent.mkdir(exist_ok=True);backup.write_bytes(old)
 with ftp.open(root+'/migration_nine_original_owner_v1.py','wb')as f:f.write(new)
 code="import runpy,sys,json,ast;from pathlib import Path;B=Path("+repr(root)+");sys.path.insert(0,str(B));ns=runpy.run_path(str(B/'migration_nine_original_owner_v1.py'),run_name='unused_owner_source_preflight');ns['verify_sources'](json.loads((B/'OWNER_PLAN.json').read_bytes()));t=ast.parse((B/'migration_nine_original_owner_v1.py').read_text());f=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='task_and_go');assert any(isinstance(n,ast.keyword)and n.arg=='max_additional_updates'and isinstance(n.value,ast.Constant)and n.value.value==1000000 for n in ast.walk(f));print('unused_owner_actual_task_hour_value_verified_no_GO_SDK_PT_locks_or_C')"
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=120);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(stdout,stderr);p.write_bytes(new);r=dict(root=root,owner_had_not_started=True,exact_old_source_backup=str(backup),old_SHA=hashlib.sha256(old).hexdigest(),new_SHA=hashlib.sha256(new).hexdigest(),preflight_rc=rc,stdout=stdout,Task_max_iterations=1000000,requested_update_quota=None,unchanged_save3600_total3900_headroom300_and_resources=True,no_running_source_or_manifest_or_policy_patch=True);out.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))
finally:ftp.close();c.close()
