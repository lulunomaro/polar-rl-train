"""OwnnewE3first-episodeperformancecase terminal metadata only; no source/model/SDK orledger operations."""
from pathlib import Path
import json,time,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;d=json.loads(sorted((R/'reports').glob('E3_original_recovery13_skill160_dispatch_*.json'))[-1].read_bytes());job=d['remote_root'];deadline=time.time()+1500;c=connect72();s=c.open_sftp()
def get(rel):
 try:
  with s.open(job+'/'+rel,'rb')as f:return json.loads(f.read())
 except FileNotFoundError:return None
try:
 while True:
  scope=get('PARENT_EXIT_SCOPE.json')
  if scope is not None:
   v={'kind':'OWN_E3_RECOVERY13_SKILL160_TERMINAL_METADATA_COLLECTION','job':job,'parent_exit':scope,'files':{},'PT_or_canonical_access':False}
   for rel in('FINAL.json','TERMINAL_ROWS.json','CHILDREN.json','PARENT_ORIGINAL_ERROR.json','WAIT_RESOURCE.json','gpu1/RESOURCE_ACTUAL.json','gpu1/E3_RECOVERY13_FULLRESTORE_BEFORE_REPLAY.json','gpu1/NATIVE24_PART_OF_RECOVERY13_CASE.json','gpu1/ORIGINAL_E3_RECOVERY13_FIRST_EPISODE_FACTS.json','gpu1/E3_RECOVERY13_SKILL160_COMPLETE.json','gpu1/E3_RECOVERY13_SKILL160_ORIGINAL_ERROR.json','gpu1/ENV_CLOSE_RETURNED.json','gpu1/TRAINER_MAIN_CLOSE_RETURNED.json','gpu1/APP_CLOSING.json','gpu1/SOURCE_FINAL_READ_COUNTS.json'):
    row=get(rel)
    if row is not None:v['files'][rel]=row
   p=R/'reports'/('E3_original_recovery13_skill160_terminal_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');facts=v['files'].get('gpu1/ORIGINAL_E3_RECOVERY13_FIRST_EPISODE_FACTS.json');print('REPORT',p);print(json.dumps({'parent_exit':scope,'parent_execution_passed':v['files'].get('FINAL.json',{}).get('passed'),'original_phase_first_episode':facts,'errors':{k:x for k,x in v['files'].items()if 'ERROR'in k},'not_expert_graduation':True},ensure_ascii=False,indent=2));break
  if time.time()>deadline:raise TimeoutError('Originalparentterminalscopeabsent; noreplayorrestartbycollector')
  time.sleep(45)
finally:s.close();c.close()
