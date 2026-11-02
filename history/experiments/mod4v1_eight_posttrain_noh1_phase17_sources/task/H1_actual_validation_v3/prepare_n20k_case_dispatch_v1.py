"""After own fresh80 truePASS+wait+locksrelease ONLY: new H1N20k case.
No PT stage/stat/hash/decode; one separate SDKcache purpose later. No canonical.
"""
from pathlib import Path
import ast,datetime,hashlib,json,shlex,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect72
BASE='/home/lc01/Zonglin Li/zonglin2'
MODEL='/home/lc01/Zonglin Li/zonglin2/tasks/H1_TYPED71DB_EXACT_TRANSPORT_20261102_040952_1793563792484126600/NORMAL_H1_TYPED71DB_PRESERVED_SOURCE.pt'
SHA='71db5543b14919eb11d2a8606f9ffe1acf0814260d7d89aa823565a49a7b21c4'

def main():
 assert not (B/'CURRENT_N20K_CASE.json').exists()
 loc=json.loads((B/'CURRENT_FRESH80_CASE.json').read_text(encoding='utf-8'));fresh=loc['remote_root']
 stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns());root=BASE+'/tasks/MOD4V1_H1_71DB_N20K_NATIVE24_NOUPDATE_'+stamp;purpose='NEW_H1_71DB_ORIGINAL453_MOD4V1_N20K_NATIVE24_'+stamp
 s=(T/'E3_actual_fullrestore_native24/supervise_e3_1cd_no_update_v1.py').read_text(encoding='utf-8')
 s=s.replace('MOD4V1_E3_1CD_N20K_NATIVE34_NOUPDATE_','MOD4V1_H1_71DB_N20K_NATIVE24_NOUPDATE_').replace('E3_NOUPDATE_PLAN.json','H1_NOUPDATE_PLAN.json')
 s=s.replace("['/usr/bin/nvidia-smi','--query-compute-apps=gpu_uuid,pid'","['/usr/bin/nvidia-smi','-i',uuid,'--query-compute-apps=gpu_uuid,pid'")
 lines=s.splitlines(keepends=True);i=next(i for i,l in enumerate(lines) if l.lstrip().startswith('task=dict('))
 lines[i]="        task=dict(kind='H1_NORMAL_TYPED71DB_MOD4V1_WHOLE20K_NATIVE24_NOUPDATE_V1',execution_scope='EVAL_ONLY_NO_OPTIMIZER',source_read_purpose=plan['source_read_purpose'],GPU_UUID=uuid,runtime_job=str(B),num_envs=20000,controls=24,worker_limit_s=900,selected_source_path=plan['model_path'],source_SHA=plan['model_SHA'],source_bytes=16879851,source_iteration=41448,source_Adam17_step=832460,source_LR=.00038443359375000017,actual_mother453_manifest_SHA='97cdcde4a891359a5f1209fdad1614bf87629e0c3d3a40ce9018dc1fe9e2426b',asset_dir=str(B/'new_assets'),asset_USD_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',asset_contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755',actor_obs=35,critic_obs=38,action_dim=6,policy_hz=50,feedback_hz=100,public_phase_tick_hz=100,physics_dt_s=.0025,decimation=8,TGS=[32,4],closure_episode_m=.01,mimic_rad=.01,no_optimizer_or_normalizer_update=True,original_H1_true270_scope=True,actual_original_private_EX_held=True,actual_original_finite_env_SH_held=True,no_production_GO=True)\n"
 s=''.join(lines)
 s=s.replace("str(B/'evaluate_e3_1cd_no_update.py'),'--task',str(d/'TASK.json')","str(B/'evaluate_h1_71db_noupdate.py'),'--job-root',str(B),'--task',str(d/'TASK.json'),'--out',str(d/'control_out')")
 s=s.replace("(d/'E3_N20K_FULLRESTORE_NATIVE34_COMPLETE.json')","(d/'control_out/MOD4V1_NORMAL_H1_NATIVE24_192PHYSICS_48FEEDBACK_NOUPDATE.json')")
 s=s.replace("(d/'ENV_CLOSE_RETURNED.json')","(d/'control_out/ENV_CLOSE_RETURNED.json')").replace("(d/'APP_CLOSING.json')","(d/'control_out/APP_CLOSING.json')").replace("(d/'E3_N20K_FULLRESTORE_ORIGINAL_ERROR.json')","(d/'control_out/NORMAL_H1_NATIVE24_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json')")
 s=s.replace('E3_1CD_N20K_NATIVE34_NOUPDATE_FINISHED','H1_71DB_N20K_NATIVE24_NOUPDATE_FINISHED')
 supervisor=B/'supervise_h1_71db_noupdate_v1.py'
 with supervisor.open('x',encoding='utf-8') as f:f.write(s)
 compile(s,str(supervisor),'exec');worker=B/'evaluate_h1_71db_native24_noupdate_v1.py';compile(worker.read_bytes(),str(worker),'exec')
 code="""from pathlib import Path
import json,shutil,hashlib
S=Path(%r);B=Path(%r);assert not B.exists();final=json.loads((S/'FINAL.json').read_bytes());closed=json.loads((S/'PARENT_EXIT_SCOPE.json').read_bytes())
assert final['passed'] is True and closed['all_own_children_waited'] and closed['original_private_lock_released'] and closed['original_shared_lock_released'],'Actual fresh80 PASS + original release required before N20k'
old=json.loads((S/'H1_NORMAL_FRESH80_PLAN.json').read_bytes());B.mkdir();rows=[]
for r in old['files']:
 rel=Path(r['relative']);assert rel.suffix.lower() not in {'.pt','.pth','.ckpt','.onnx','.safetensors','.pyc'} and not rel.is_absolute() and '..' not in rel.parts
 if str(rel) in ('probe_h1_normal_fresh80.py','supervise_h1_normal_fresh80.py'):continue
 p=S/rel;raw=p.read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['sha256'];dst=B/rel;dst.parent.mkdir(parents=True,exist_ok=True)
 with dst.open('xb') as f:f.write(raw)
 rows.append(r)
(B/'NONPT_N20K_STAGE_INDEX.json').write_text(json.dumps({'files':rows,'source_PT_operations':0,'fresh_actual_final':final,'fresh_actual_closed':closed},indent=2))
print(json.dumps({'new_root':str(B),'originalH1_nonPT_dependencies':len(rows),'source_PT_operations':0,'fresh_actualPASS_and_release':True}))
"""%(fresh,root)
 report=dict(kind='NEW_H1_71DB_N20K_EVAL_ONLY_DISPATCH',remote_root=root,fresh_source_case=fresh,source_read_purpose=purpose,source_PT_stage_operations=0,canonical_access=False)
 client=sf=None
 try:
  client=connect72();i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=240);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();report.update(stage_rc=rc,stage_stdout=stdout,stage_stderr=stderr);assert rc==0,'N20kcase stage failed; see originalerror report'
  sf=client.open_sftp()
  with sf.open(root+'/NONPT_N20K_STAGE_INDEX.json','r') as f:rows=json.load(f)['files']
  for rel,p in [('evaluate_h1_71db_noupdate.py',worker),('supervise_h1_71db_noupdate.py',supervisor),('H1_NOUPDATE_FOR24_EXACT_AST_PROOF.json',B/'H1_NOUPDATE_FOR24_EXACT_AST_PROOF.json')]:
   raw=p.read_bytes();sf.put(str(p),root+'/'+rel);rows.append(dict(relative=rel,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
  plan=dict(kind='H1_71DB_N20K_NATIVE24_NOUPDATE_NEW_PURPOSE',execution_scope='EVAL_ONLY_NO_OPTIMIZER',source_read_purpose=purpose,model_path=MODEL,model_SHA=SHA,model_bytes=16879851,num_envs=20000,controls=24,GPU_index=1,GPU_UUID=loc['GPU_UUID'],parent_limit_s=1200,worker_limit_s=900,files=rows,no_production_GO=True,canonical_access=False)
  with sf.open(root+'/H1_NOUPDATE_PLAN.json','wx') as f:f.write(json.dumps(plan,indent=2))
  start="import pathlib,subprocess,json,psutil;B=pathlib.Path(%r);assert not(B/'PARENT_STARTED.json').exists();log=(B/'SUPERVISOR_FULL_STDOUT_STDERR.log').open('xb');p=subprocess.Popen([%r,'-u','-B',str(B/'supervise_h1_71db_noupdate.py')],cwd=B,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);log.close();print(json.dumps({'pid':p.pid,'creation':psutil.Process(p.pid).create_time(),'root':str(B),'dispatched_only':True}))"%(root,BASE+'/run-python.sh')
  i,o,e=client.exec_command(shlex.quote(BASE+'/run-python.sh')+' -B -c '+shlex.quote(start),timeout=60);i.close();stdout=o.read().decode();stderr=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,stderr);report.update(status='H1_N20K_NOUPDATE_SUPERVISOR_DISPATCHED',parent=json.loads(stdout))
  with (B/'CURRENT_N20K_CASE.json').open('x',encoding='utf-8') as f:json.dump(dict(remote_root=root,parent=report['parent'],source_read_purpose=purpose),f,indent=2)
 except BaseException:
  report.update(status='STAGE_OR_DISPATCH_ERROR',error=traceback.format_exc());raise
 finally:
  if sf:sf.close()
  if client:client.close()
  dest=T/'reports'/('H1_n20k_dispatch_'+stamp+'.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(dict(status=report.get('status'),root=root,parent=report.get('parent'),report=str(dest)),indent=2))
if __name__=='__main__':main()
