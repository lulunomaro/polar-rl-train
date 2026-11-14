"""Finish this authorized40m experiment without any automatic next training window."""
from pathlib import Path
import json,subprocess,sys,time,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
try:
 while not (E/'MONITOR_COMPLETE.json').exists():time.sleep(10)
 monitor=json.loads((E/'MONITOR_COMPLETE.json').read_text());assert not monitor['training_has_error']
 assert all(x['exit_code']==0 for x in monitor['evaluations'])
 for name,args in [('select_student.py',[]),('run_post_evaluations_r2.py',[]),('finalize_run.py',[]),('archive_run.py',['--phase','complete'])]:
  print('PIPELINE_STAGE '+name,flush=True);r=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/name),*args],cwd=R);assert r.returncode==0,name+' failed; original evidence retained'
 (E/'PIPELINE_COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),bounded40m_complete=True,no_more_training=True),indent=2)+'\n')
 # Commit the completion marker and verified upload receipt once; final ref checks remain stdout.
 import datetime
 sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
 net=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
 def git(*args):return subprocess.check_output(net+list(args),text=True,encoding='utf8').strip()
 date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d')
 payload_tag='trial-'+date+'-ordered-rearward-fix-40m-complete-01'
 payload=git('rev-parse',payload_tag+'^{}')
 refs={row.split()[1]:row.split()[0]for row in git('ls-remote','origin','refs/heads/main','refs/tags/'+payload_tag,'refs/tags/'+payload_tag+'^{}').splitlines()}
 assert refs['refs/tags/'+payload_tag+'^{}']==payload
 receipt=E/'FINAL_UPLOAD_RECEIPT.json'
 receipt.write_text(json.dumps(dict(epoch=time.time(),payload_commit=payload,payload_tag=payload_tag,remote_verified_refs=refs,original_budget_seconds=2400,previous_phase_seconds=292.2261128425598,actual_corrected_phase_seconds=json.loads((E/'training/FINAL.json').read_text())['elapsed_seconds'],full_PT_blobs_verified_by_archive=True,proxy='http://127.0.0.1:7897',no_further_training=True),indent=2)+'\n',encoding='utf8')
 def record_git(*args):
  if args[0]=='add':return git('add','--sparse','-f','--',*[x for x in args[1:]if x!='--'])
  return git(*args)
 rec.git=record_git
 ID='ordered-rearward-fix-40m-closure-01'
 sys.argv=['record_experiment.py','--id',ID,'--title','Record bounded ordered-rearward round closure and verified full-PT upload','--kind','training','--note-file',str(receipt),'--validation','Corrected phase and prior292.226s counted within original2400s; all checkpoint evaluations closed; complete ordinary PT blobs and payload tag verified through7897; no next training window','--files',receipt.relative_to(R).as_posix(),(E/'PIPELINE_COMPLETE.json').relative_to(R).as_posix(),'--push']
 rec.main()
 head=git('rev-parse','HEAD');remote=git('ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/heads/main','refs/tags/trial-'+date+'-'+ID+'^{}')
 assert head in remote and refs['refs/heads/main']in remote
 print('BOUNDED40M_COMPLETE_AND_FINAL_RECEIPT_ARCHIVED '+head,flush=True)
except BaseException:
 (E/'PIPELINE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),traceback=traceback.format_exc()),indent=2)+'\n');raise
