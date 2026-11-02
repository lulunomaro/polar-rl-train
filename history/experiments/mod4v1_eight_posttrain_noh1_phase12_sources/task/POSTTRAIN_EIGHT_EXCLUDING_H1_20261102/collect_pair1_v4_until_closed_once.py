"""Only ownpublishedmetadata boundedwatch+oneclosedstdoutcopy; no PT/raw/SDK/GPU/canonical operations."""
from pathlib import Path
import json,time,sys,hashlib,datetime
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
m=D/'PAIR1_V4_COLLECTOR_ONCE.json';assert not m.exists();record=json.loads((D/'PAIR1_V4_STAGE_DISPATCH_RESULT.json').read_bytes());root=record['root'];out=D/'reports'/('PAIR1_V4_CLOSED_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));out.mkdir(parents=True);m.write_text(json.dumps({'root':root,'deadline_seconds':4500,'metadata_only_untilclosed':True},indent=2),encoding='utf-8');last=None;end=time.monotonic()+4500;roles=('E0','CURB_PROTECTED878');c=connect72();s=c.open_sftp()
def readrel(rel,cap=5000000):
 try:
  path=root+'/'+rel;st=s.stat(path)
  if st.st_size>cap:return {'oversize_metadata_path':path,'bytes':st.st_size}
  with s.open(path,'rb')as f:raw=f.read()
  return json.loads(raw)
 except FileNotFoundError:return None
try:
 while True:
  ex=readrel('OWNER_EXIT_ACTUAL.json');cur=readrel('OWNER_CURRENT.json');err=readrel('OWNER_ORIGINAL_ERROR.json');rows=[]
  for role in roles:
   pref='roles/'+role+'/production/';f=readrel(pref+'FINAL.json');live=readrel(pref+('LIVE_WHOLE20K_FULLRESTORE_BEFORE_PPO.json'if role=='E0'else'POSTTRAIN_FULL20K_FULLSTATE_BEFORE_LEARN.json'));latest=readrel(pref+'latest_complete.json');error=readrel(pref+('WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json'if role=='E0'else'ORIGINAL_POSTTRAIN_ERROR.json'));rows.append({'role':role,'actual_full20k_live_restored':live is not None,'complete_checkpoint_published':latest is not None,'final':f,'error':error})
  status={'root':root,'closed':ex is not None,'parent_error':err is not None,'rows':[{'role':r['role'],'fullrestore':r['actual_full20k_live_restored'],'saved':r['complete_checkpoint_published'],'final':r['final']is not None,'error':r['error']is not None}for r in rows]};sig=json.dumps(status,sort_keys=True)
  if sig!=last:print('PAIR1_ACTUAL_STATUS',json.dumps(status),flush=True);last=sig
  if ex is not None:
   plan=readrel('OWNER_PLAN.json');cohort=readrel('COHORT_FINAL.json');result={'kind':'PAIR1_V4_ORIGINAL_POSTTRAIN_CLOSED_ACTUAL_METADATA','root':root,'parent_exit':ex,'parent_error':err,'cohort':cohort,'rows':rows,'collected_own_JSON_or_stdout_only':True,'PT_raw_SDK_GPU_canonical_operations':0};files=[]
   paths=['OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json','COHORT_FINAL.json','OWNER_CURRENT.json','OWNER_PLAN.json','ORIGINAL_PARENT_STDOUT_STDERR.log']
   for e in(plan or{}).get('entries',[]):
    role=e['role'];base='roles/'+role;paths += [base+'/'+n for n in('TASK.json','GO_PRODUCTION.json','ROOT_ADMISSION_ACTUAL.json','ACTUAL_CANONICAL_READ.json','ACTUAL_RESOURCE_LEASES.json','PARENT_WAITED_ACTUAL.json','PPO_FULL_STDOUT_STDERR.log')]
    try:paths += [base+'/production/'+a.filename for a in s.listdir_attr(root+'/'+base+'/production')if a.filename.endswith('.json')]
    except FileNotFoundError:pass
   for rel in paths:
    try:st=s.stat(root+'/'+rel)
    except FileNotFoundError:continue
    if st.st_size>50000000:files.append({'remote':root+'/'+rel,'bytes':st.st_size,'retained':'metadata_only_large_original'});continue
    with s.open(root+'/'+rel,'rb')as z:raw=z.read()
    p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);files.append({'relative':rel,'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()})
   result['collected_files']=files;p=out/'CLOSED_RESULT.json';p.write_text(json.dumps(result,indent=2),encoding='utf-8');(D/'PAIR1_V4_LATEST_CLOSED_RESULT_PATH.json').write_text(json.dumps({'path':str(p)},indent=2),encoding='utf-8');print('RESULT',p,flush=True);print(json.dumps({k:v for k,v in result.items()if k not in('cohort','collected_files','rows')},indent=2),flush=True);break
  if time.monotonic()>=end:raise TimeoutError('Bounded4500s reached; do not duplicate worker or assume resource released')
  time.sleep(15)
finally:s.close();c.close()
