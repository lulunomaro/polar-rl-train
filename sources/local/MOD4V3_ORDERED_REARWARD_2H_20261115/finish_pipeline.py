"""Close valid segments, compare saved students, evaluate and archive complete PTs."""
from pathlib import Path
import json,time,sys,subprocess,shutil,traceback
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';previous=T.parent/'MOD4V3_ORDERED_REARWARD_FIX_40M_20261115'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+chr(10),encoding='utf8')
try:
 while not(previous/'evidence/MONITOR_COMPLETE.json').exists():time.sleep(10)
 prior=read(previous/'evidence/MONITOR_COMPLETE.json');assert not prior['training_has_error'];assert all(x['exit_code']==0 for x in prior['evaluations'])
 while not(E/'MONITOR_COMPLETE.json').exists():time.sleep(10)
 current=read(E/'MONITOR_COMPLETE.json');assert not current['training_has_error'];assert all(x['exit_code']==0 for x in current['evaluations'])
 shutil.copytree(previous/'evidence',E/'previous_valid_segment',ignore=shutil.ignore_patterns('*.partial','*_worker.log','post_native','post_native_r2'))
 mapping={};models=[]
 for row in prior['models']:
  old=row['file'];new={'model_final.pt':'model_segment040_final.pt','model_first_complete.pt':'model_segment040_first_complete.pt'}.get(old,old);assert not(T/'weights'/new).exists();shutil.copy2(previous/'weights'/old,T/'weights'/new);mapping[old]=new;models.append(dict(row,file=new,path=str(T/'weights'/new),original_segment_path=row['path']))
 for d in(previous/'evidence/checkpoint_evals').iterdir():
  if not d.is_dir()or not(d/'EVALUATION.json').exists():continue
  result=read(d/'EVALUATION.json');name=mapping[Path(result['model']).name];dest=E/'checkpoint_evals'/Path(name).stem;shutil.copytree(d,dest);result.update(model=str(T/'weights'/name),original_evaluation=str(d/'EVALUATION.json'),copied_without_new_simulation=True);put(dest/'EVALUATION.json',result)
 models+=current['models'];put(E/'MODEL_COLLECTION.json',dict(models=models,full_PT_bytes=True,previous_segment=prior,current_segment=current));put(E/'BOTH_SEGMENTS_COMPLETE.json',dict(epoch=time.time(),previous=prior,current=current))
 for name,args in [('select_student.py',[]),('run_post_evaluations_r2.py',[]),('finalize_run.py',[]),('archive_run.py',['--phase','complete'])]:
  print('PIPELINE_STAGE '+name,flush=True);result=subprocess.run([sys.executable,'-X','utf8','-B','-u',str(T/name),*args],cwd=R);assert result.returncode==0,name+' failed; evidence retained'
 import datetime
 date=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d');tag='trial-'+date+'-ordered-rearward-2h-complete-01';net=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
 payload=subprocess.check_output(net+['rev-parse',tag+'^{}'],text=True).strip();refs=subprocess.check_output(net+['ls-remote','origin','refs/heads/mod4v1-experts-fulldr-rm70','refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}'],text=True);assert payload in refs
 put(E/'FINAL_UPLOAD_RECEIPT.json',dict(epoch=time.time(),payload_tag=tag,payload_commit=payload,verified_remote_refs=refs,full_PT_blobs_verified_by_archive=True,proxy='http://127.0.0.1:7897',no_further_training=True))
 put(E/'PIPELINE_COMPLETE.json',dict(epoch=time.time(),total_two_hour_round_complete=True,no_more_training=True))
 result=subprocess.run([sys.executable,'-X','utf8','-B',str(T/'archive_run.py'),'--phase','closure'],cwd=R);assert result.returncode==0,'Final closure archive pending'
except BaseException:
 put(E/'PIPELINE_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()));raise
