"""Repair the three unexecuted final suites; keep original failures and valid suites."""
from pathlib import Path
import sys,json,subprocess,time,hashlib,datetime
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';Q=E/'checkpoint_evals/model_final';A=E/'final_regression_repair01';model=T/'weights/model_final.pt';sha=hashlib.sha256(model.read_bytes()).hexdigest();before=json.loads((A/'EVALUATION_initial_incomplete.json').read_text());assert sha==before['sha256'];assert(E/'training/SAFE_CLOSED.json').exists();assert not(E/'training/ERROR.json').exists();start=time.time();results=dict(before['results']);paths={name:Q/name for name in ['single_step','flat60']}
for name,script,extra in [('pitch','fixed_pitch_eval.py',[]),('stairs','fixed_stair_eval.py',['--highest-command-only']),('descent','descent_eval.py',['--highest-command-only'])]:
 dest=Q/(name+'_retry01');cmd=[sys.executable,'-X','utf8','-B','-u',str(T/script),'--model',str(model),'--out',str(dest)]+extra
 with(Q/(name+'_retry01.log')).open('xb')as log:r=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 results[name]=dict(exit_code=r.returncode,original_exit_code=before['results'][name]['exit_code'],path=str(dest),original_failure_preserved=True);paths[name]=dest;print('REPAIRED_SUITE',name,r.returncode,flush=True)
 if r.returncode:raise RuntimeError('Suite still failed: '+name+'; see '+str(Q/(name+'_retry01.log')))
result=dict(before);result.update(results=results,complete=all(v['exit_code']==0 for v in results.values()),repair_original_evaluation=str(A/'EVALUATION_initial_incomplete.json'),suite_paths={k:str(v)for k,v in paths.items()},completed_successful_suites_not_replayed=['single_step','flat60'],repair_PPO_updates=0,repair_optimizer_updates=0,repair_wall_seconds=time.time()-start)
for name in ['pitch','stairs','descent']:
 d=json.loads((paths[name]/'RESULT.json').read_text());assert d['sha256']==sha
 if name=='pitch':result['pitch_summary']=d['summary']
 elif name=='stairs':
  ob=[r for r in d['rows']if r['case'].startswith('whole_oblique_')];assert len(ob)==20;result.update(straight_passed=d['summary']['whole_h420']['passed'],straight_requested=5,actual_oblique_passed=sum(r['actual_oblique_success']for r in ob),oblique_requested=20)
 else:result.update(descent_passed=d['summary']['descent']['passed'],descent_requested=5)
assert result['complete'];(Q/'EVALUATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');receipt=dict(completed_at=datetime.datetime.now().astimezone().isoformat(),reason='Missing copied manual_replay dependencies prevented three suites from starting',fixed_by='Copied byte-identical archived guards into this experiment only',original_failed_logs_and_partial_directories_preserved=True,model_sha256=sha,rerun_suites=['pitch','stairs','descent'],successful_suites_reused=['single_step','flat60'],results=results,PPO_updates=0,optimizer_updates=0,all_requested_suites_complete=True);(A/'REPAIR_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print('ALL_FINAL_REGRESSIONS_COMPLETE',json.dumps({k:result.get(k)for k in ['flat60_passed','single_step_qualified_passed','physical_crossed','physical_stable_events','straight_passed','actual_oblique_passed','descent_passed','pitch_summary']}),flush=True)
