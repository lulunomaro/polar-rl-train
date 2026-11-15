"""Close this continuation within the original7200s combined budget, paired evaluations, complete PT archive and receipt."""
from pathlib import Path
import json,time,sys,subprocess,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+chr(10),encoding='utf8')
try:
 while not(E/'MONITOR_COMPLETE.json').exists():time.sleep(10)
 current=read(E/'MONITOR_COMPLETE.json');assert not current['training_has_error']
 # Retain the original import failure; accept only its completed same-SHA replay.
 import hashlib
 for item in current['evaluations']:
  if item['exit_code']==0:continue
  retry=E/'checkpoint_evals'/(Path(item['model']).stem+'_importfix01')/'EVALUATION.json'
  fixed=read(retry)
  assert fixed['complete'] and Path(fixed['model']).resolve()==Path(item['model']).resolve()
  assert fixed['sha256']==hashlib.sha256(Path(item['model']).read_bytes()).hexdigest()
 for name,args in [('run_post_evaluations_envfix02.py',[]),('finalize_run.py',[]),('archive_run.py',['--phase','complete'])]:
  print('PIPELINE_STAGE '+name,flush=True);result=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/name),*args],cwd=R);assert result.returncode==0,name+' failed; evidence retained'
 import datetime
 date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d');tag='trial-'+date+'-pitch-stability-level9-angle30-cont-complete-01';net=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
 payload=subprocess.check_output(net+['rev-parse',tag+'^{}'],text=True).strip();refs=subprocess.check_output(net+['ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}'],text=True);assert payload in refs
 put(E/'FINAL_UPLOAD_RECEIPT.json',dict(epoch=time.time(),payload_tag=tag,payload_commit=payload,verified_remote_refs=refs,full_PT_blobs_verified_by_archive=True,proxy='http://127.0.0.1:7897',no_further_training=True))
 put(E/'PIPELINE_COMPLETE.json',dict(epoch=time.time(),total_two_hour_round_complete=read(T/'DECISION.json')['total_PPO_seconds']>=7199,no_more_training=True))
 result=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_run.py'),'--phase','closure'],cwd=R);assert result.returncode==0,'Final closure archive pending'
except BaseException:
 put(E/'PIPELINE_NATIVEFIX02_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
