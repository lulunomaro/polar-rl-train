"""Link actual isolated results; preserve live learning/evaluator/budget metadata."""
from pathlib import Path
import json,sys,time,hashlib
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;R=D/'reports';assert not (R/'METADATA_SYNCED.json').exists()
read=lambda p:json.loads(p.read_text(encoding='utf8'));v=read(R/'PERFORMANCE_REVIEW.json');g=read(R/'PERFORMANCE_GIT_RECORDED.json');assert g['remote_main_tag_peeled_verified']
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();E='/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007';root='/home/egde/rl_candidates/'+D.name
try:
 with c.open_sftp() as f:
  def upload(path,raw):
   with f.open(path+'.partial','wb') as out:out.write(raw)
   try:f.posix_rename(path+'.partial',path)
   except OSError:f.rename(path+'.partial',path)
  for p in D.glob('*.py'):
   target=root+'/'+p.name
   try:old=f.open(target).read()
   except FileNotFoundError:old=None
   if old is not None:assert old==p.read_bytes()
   else:upload(target,p.read_bytes())
  for name in ('PERFORMANCE_REVIEW.json','PERFORMANCE_REPORT.md','PERFORMANCE_GIT_RECORDED.json','TARGET_CPU_PASSED.json','ACTUAL_SDK_ACCEPTED.json'):
   upload(root+'/reports/'+name,(R/name).read_bytes())
  for name,source in (('D7_RESET_PERFORMANCE_3060_REVIEW.json','PERFORMANCE_REVIEW.json'),('D7_RESET_PERFORMANCE_3060_REPORT.md','PERFORMANCE_REPORT.md'),('D7_RESET_PERFORMANCE_GIT_RECORDED.json','PERFORMANCE_GIT_RECORDED.json')):
   target=E+'/reports/'+name
   try:f.stat(target)
   except FileNotFoundError:pass
   else:raise AssertionError('Central unique result already exists')
   upload(target,(R/source).read_bytes())
  target=E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json';old=json.loads(f.open(target).read());now=dict(old)
  refs=list(now.get('isolated_performance_reviews',[]));refs.append(dict(id='D7_RESET_PERFORMANCE_3060_20261009',report='reports/D7_RESET_PERFORMANCE_3060_REVIEW.json',git_record='reports/D7_RESET_PERFORMANCE_GIT_RECORDED.json',production_adopted=False,full_20k_PPO_speed_not_measured=True))
  now['isolated_performance_reviews']=refs;assert {k:x for k,x in now.items() if k!='isolated_performance_reviews'}=={k:x for k,x in old.items() if k!='isolated_performance_reviews'}
  upload(target,json.dumps(now,indent=2,ensure_ascii=False).encode())
  path=E+'/reports/LATEST_HANDOFF.md';text=f.open(path).read().decode('utf8')
  header=(f"Latest isolated performance review {datetime.now(timezone.utc).isoformat()}: human authorized 3060-only optimization test without disturbing main training. See D7_RESET_PERFORMANCE_3060_REVIEW/REPORT and D7_RESET_PERFORMANCE_GIT_RECORDED.\n"
   f"Main277 source/4090 actual D7 learning unchanged; no PPO/canonical transaction by these tests and no optimization installed in production. Existing controller, worker and budget authority continue. Source checkpoint31416 used only for matched frozen test.\n"
   f"Actual10env300control COM ABBA SDK and matched80env1500control forced-reset collection completed; throughput ratio {v['collection_speed_ratio']:.6f}, full reset median ratio {v['reset_median_speed_ratio']:.6f}. COM translation/episode/privateRNG and original rotation/inertia audit contract passed. First byte equality/CPU-CUDA reader errors retained_failed; prepared-task holds isolated them without stopping healthy eval or 4090.\n"
   "This is 3060 frozen timing, not 20000-env 4090 PPO speed or skill graduation. No repeated45min clock test. Future optimization adoption requires its own safe saved source boundary and relevant contract; do not hotpatch or replay any once entry. D7 actual learned b1 cases are separate from performance stress cases; continue actual plan D9/S3 review and RM terrain annotation references.\n"
   f"Unique tag {g['tag']} commit {g['commit']} remote main/tag/peeled verified. All older raw/weights/results and master v1.5 SHA remain.\n\n")
  upload(path,(header+text).encode())
  out=dict(epoch=time.time(),central_reports_linked=True,all_live_learning_evaluator_budget_fields_preserved=True,production_mutations=0,git=g)
  upload(root+'/reports/METADATA_SYNCED.json',json.dumps(out,indent=2).encode());(R/'METADATA_SYNCED.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out))
finally:c.close()
