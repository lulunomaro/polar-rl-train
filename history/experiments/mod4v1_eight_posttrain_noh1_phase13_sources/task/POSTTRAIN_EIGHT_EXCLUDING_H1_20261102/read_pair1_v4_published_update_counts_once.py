"""One actualpublishedcomplete-checkpoint progress, neverselectedPT/raw/SDK/C."""
from pathlib import Path
import sys,json,datetime
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
root=json.loads((D/'PAIR1_V4_STAGE_DISPATCH_RESULT.json').read_bytes())['root'];c=connect72();s=c.open_sftp();rows=[]
try:
 for role in('E0','CURB_PROTECTED878'):
  x={'role':role};base=root+'/roles/'+role+'/production/'
  for name in('latest_complete.json','FINAL.json','LIVE_WHOLE20K_FULLRESTORE_BEFORE_PPO.json','POSTTRAIN_FULL20K_FULLSTATE_BEFORE_LEARN.json','ORIGINAL_POSTTRAIN_ERROR.json','ORIGINAL_PPO_ERROR_BEFORE_FINAL_SAVE.json'):
   try:
    with s.open(base+name,'rb')as f:v=json.loads(f.read())
   except FileNotFoundError:continue
   if'BEFORE_'in name:x[name]={'source_SHA':v.get('source_SHA'),'fullstate_restore_published':True,'requested_max_updates':v.get('requested_max_updates',20)}
   else:x[name]=v
  rows.append(x)
finally:s.close();c.close()
p=D/'reports'/('PAIR1_V4_PUBLISHED_PPO_COUNTS_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps({'root':root,'rows':rows,'PT_SDK_raw_C_reads':0},indent=2),encoding='utf-8');print(p);print(json.dumps(rows,indent=2))
