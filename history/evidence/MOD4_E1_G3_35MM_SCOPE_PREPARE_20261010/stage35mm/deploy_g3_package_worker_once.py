from pathlib import Path
import hashlib,json,os,sys,time,traceback
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';H=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(W/'RM2026_TERRAIN_AUDIT_20261009'));from reuse_authorized_session_transport import recover
sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
WIN='D:/MOD4_async_eval/closure_episode_clock2500_v15'
try:
 p=R/'G3_PACKAGE_WORKER_DEPLOY_STARTED.json';assert not p.exists();p.write_text(json.dumps(dict(epoch=time.time(),once=True)),encoding='utf8')
 secret,_=recover('MOD4_EVAL_SSH_PASSWORD');assert secret;os.environ['MOD4_EVAL_SSH_PASSWORD']=secret;c=connect_eval()
 with c.open_sftp() as f:
  for source,dest in [(D/'eval_worker_e1_g3_package_review.py','eval_worker_e1_g3_package_review.py'),(D/'admit_e1_g3_package_review_once.py','admit_e1_g3_package_review_once.py'),(R/'G3_WORKER_EXPECTED.json','E1_G3_WORKER_EXPECTED.json')]:
   raw=source.read_bytes()
   with f.open(WIN+'/'+dest,'wbx') as o:o.write(raw)
   assert f.open(WIN+'/'+dest).read()==raw
 _,o,e=c.exec_command('D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe -X utf8 '+WIN+'/admit_e1_g3_package_review_once.py',timeout=60);out=o.read();err=e.read();code=o.channel.recv_exit_status()
 (R/'G3_PACKAGE_WORKER_DEPLOY_OUTPUT.txt').write_bytes(out+err);assert code==0,(out+err).decode(errors='replace')
 with c.open_sftp() as f:
  for name in ['ADMISSION','STARTED','ADMITTED']:
   raw=f.open(WIN+'/E1_G3_PACKAGE_REVIEW_WORKER_'+name+'.json').read();(R/('E1_G3_PACKAGE_REVIEW_WORKER_'+name+'.json')).write_bytes(raw)
  for name in ['OLD_ARTIFACT_TASK_BEFORE_G3_PACKAGE.xml','E1_G3_PACKAGE_REVIEW_TASK.xml']:(R/name).write_bytes(f.open(WIN+'/'+name).read())
 print(out.decode())
except Exception:
 (R/'G3_PACKAGE_WORKER_DEPLOY_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),do_not_repeat_existing_authority=True),indent=2),encoding='utf8');raise
finally:
 if 'c' in globals():c.close()
 os.environ.pop('MOD4_EVAL_SSH_PASSWORD',None)
