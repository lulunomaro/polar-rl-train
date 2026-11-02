"""Continue exact explicitvariant sequence after currentprotected closes.
No duplicateSDK/watcher: currentprotected watched elsewhere; only localcollected
terminaldependency read here. Subsequentcases each own watcher sequentially.
No GPU0/canonical/PPO/newroles, no automatic retry on failure.
"""
from pathlib import Path
import json,runpy,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;rows=[];start=time.monotonic();report=B/'SEQUENTIAL_VARIANT_PROGRESS_V1.json'
def put():report.write_text(json.dumps(dict(kind='EXPLICIT_VARIANT_SEQUENTIAL_PROGRESS_NO_RETRY',rows=rows,elapsed_s=time.monotonic()-start,canonical_or_PPO=False),indent=2),encoding='utf-8')
def script(name,args):
 old=sys.argv;sys.argv=[name]+args
 try:runpy.run_path(str(B/name),run_name='__main__')
 finally:sys.argv=old

def latest(name,root):
 p=B/(name+'_LATEST_COLLECTION_LOCATOR.json')
 try:j=json.loads(p.read_bytes())
 except (FileNotFoundError,json.JSONDecodeError):return None
 if j['remote_root']!=root:return None
 c=json.loads(Path(j['collection']).read_bytes());v=c['files'];closed=v.get('PARENT_EXIT_SCOPE.json');final=v.get('FINAL.json')
 if not closed or not closed.get('all_own_children_waited'):return None
 assert final and final['passed'] and closed['original_private_lock_released'] and closed['original_shared_lock_released'] and not closed['errors'],'Case did notactualPASS+cleanrelease; no replay/nextSDK'
 return j['collection']

def run_case(name,mode):
 locator=B/(name+'_CURRENT_'+mode.upper()+'_CASE_V1.json');assert not locator.exists()
 script('stage_dispatch_variant_gpu1_once_v1.py',['--variant',name,'--mode',mode]);loc=json.loads(locator.read_bytes());rows.append(dict(variant=name,mode=mode,status='DISPATCHED_ONLY',root=loc['remote_root'],parent=loc['parent']));put();print('NEW_CASE_METADATA',json.dumps(rows[-1]),flush=True)
 script('watch_e1_terminal_metadata_v1.py',['--locator',str(locator)]);collection=latest(name,loc['remote_root']);assert collection;rows[-1].update(status='ACTUAL_PASS_CLOSEWAIT_RELEASE',collection=collection);put();print('ACTUAL_CLEAN_PASS',json.dumps(rows[-1]),flush=True);return collection
try:
 root=json.loads((B/'CURB_PROTECTED878_CURRENT_N20K_CASE_V1.json').read_bytes())['remote_root'];ready=None
 while ready is None:
  ready=latest('CURB_PROTECTED878',root)
  if ready is None:
   if time.monotonic()-start>1800:raise TimeoutError('Localcollectedprotectedterminaldependency not delivered; no newSDK')
   time.sleep(45)
 rows.append(dict(variant='CURB_PROTECTED878',mode='n20k',status='ACTUAL_PASS_CLOSEWAIT_RELEASE',collection=ready));put()
 script('seal_one_variant_actual_protocol_pass_v1.py',['--variant','CURB_PROTECTED878','--native-collection',ready,'--fresh-collection',str(T/'reports/CURB_PROTECTED878_actual_case_collect_20261102_063706/COLLECTION.json')])
 for name in ['CURB_INDEPENDENT113','SLOPE_INDEPENDENT50']:
  fresh=run_case(name,'fresh80');native=run_case(name,'n20k');script('seal_one_variant_actual_protocol_pass_v1.py',['--variant',name,'--native-collection',native,'--fresh-collection',fresh])
 rows.append(dict(status='ALL_THREE_ACTUAL_PROTOCOL_PASS_NOT_SKILL',all_originalleases_released=True));put();print('ALL_THREE_ACTUAL_PROTOCOL_PASS',flush=True)
except BaseException:
 rows.append(dict(status='SEQUENTIAL_STOP_ORIGINAL_ERROR_NO_REPLAY',error=traceback.format_exc()));put();print(json.dumps(rows[-1],indent=2),flush=True);raise
