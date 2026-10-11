from direction_io import *
import ast,traceback
def main():
 previous=json.loads((R/'DIRECTION_ACTIVE_ROOT.json').read_bytes())['root'];root='/home/egde/rl_candidates/MOD4_S3_E1_CURB20_DIRECTION_STARTUP_REVIEWED_20261011'
 P=D/'startup_reviewed_payload';P.mkdir();C=P/'isaac/mod4';C.mkdir(parents=True)
 small=(D/'payload/isaac/mod4/train_curb20_direction_fresh_preflight_ppo.py').read_text();anchor='    manifest["actual_CURB_episode_direction_scope"]=env.command_manager.get_term("twist").audit_direction()'
 assert small.count(anchor)==1;small=small.replace(anchor,'    env.command_manager.get_term("twist")._write_dynamic(torch.arange(env.num_envs,device=env.device))\n'+anchor)
 name='train_curb20_direction_startup_reviewed_fresh_preflight_ppo.py';p=C/name;ast.parse(small);p.write_bytes(small.encode())
 controller=(D/'payload/supervise_curb20_direction_once.py').read_text().replace('train_curb20_direction_fresh_preflight_ppo.py',name)
 controller=controller.replace(" direction_native(10,0,300,'ENTRY_ORIGIN_BOUND_SDK10')\n direction_native(20000,24,120,'DIRECTION_NATIVE20K')", " assert read(R/'DIRECTION_REUSED_PHYSICAL_SCOPE_VERIFIED.json')['passed']\n assert read(R/'ENTRY_ORIGIN_BOUND_SDK10_PASSED.json')['passed'] and read(R/'DIRECTION_NATIVE20K_PASSED.json')['passed']")
 assert "direction_native(10,0,300" not in controller
 p=P/'supervise_curb20_direction_startup_reviewed_once.py';ast.parse(controller);p.write_bytes(controller.encode())
 n,w=io.connect_both()
 try:
  v=run(n,r'''from pathlib import Path
import sys,json,time,torch,subprocess,shutil,hashlib,fcntl
old=Path(PREVROOT);D=Path(ROOT);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes())
assert not D.exists();state=j(old/'reports/E1_STATE.json');att=j(old/'reports/E1_ATTENTION.json');assert not att['own_child_still_alive'] and att['active_segment'] is None and j(B)['active_segment'] is None
exits=[]
for loc in (state['owner'],state['child'],j(old/'reports/E1_GUARDIAN_STARTED.json')):
 p=Path('/proc')/str(loc['pid']);a=None
 if p.exists():
  z=(p/'stat').read_text().split(') ',1)[1].split();a=dict(state=z[0],start_ticks=int(z[19]));assert a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 exits.append(dict(locator=loc,actual=a))
for q in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
segments=[x for x in j(B)['completed_segments'] if x['pid']==state['child']['pid']];assert len(segments)==1
error=old/('discard_logs/'+Path(state['active_log']).stem+'.error.txt');assert 'bound_episode' in (old/state['active_log']).read_text()
freeze=j(old/'reports/SOURCE_FREEZE.json');assert len(freeze['sha256'])==421
D.mkdir();(D/'reports').mkdir()
for name,h in freeze['sha256'].items():
 p=old/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h;q=D/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ('SOURCE_SELECTED.json','CURB_FOUR_CASE_TEMPLATES.json','CANDIDATE_JOB_UNUSED_ACTUAL.json','DIRECTION_TARGET_CPU_PASSED.json','ENTRY_ORIGIN_BOUND_SDK10_PASSED.json','DIRECTION_NATIVE20K_PASSED.json'):shutil.copy2(old/'reports'/name,D/'reports'/name)
physical=[]
for name in ('ENTRY_ORIGIN_BOUND_SDK10_PASSED.json','DIRECTION_NATIVE20K_PASSED.json'):
 row=j(old/'reports'/name);assert row['passed'] and hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256'];physical.append(row)
reuse=dict(epoch=time.time(),passed=True,source_root=str(old),physical_scope_exact_SHA_reused=physical,no_SDK_native_replay=True,old_failedsmall_learning_updates=0,old_failure_and_unique_cost_retained=True,old_unique_segment=segments,old_actual_exits=exits)
(D/'reports/DIRECTION_REUSED_PHYSICAL_SCOPE_VERIFIED.json').write_text(json.dumps(reuse,indent=2))
print(json.dumps(dict(root=str(D),source_freeze=freeze,reuse=reuse,no_GPU_or_budget_transaction=True)))
'''.replace('PREVROOT',repr(previous)).replace('ROOT',repr(root)).replace('BUDGET',repr(io.B)))
  save('DIRECTION_STARTUP_421_SOURCE_COPIED.json',v);hashes=dict(v['source_freeze']['sha256'])
  with n.open_sftp() as f:
   for p in sorted(P.rglob('*.py')):
    raw=p.read_bytes();name=p.relative_to(P).as_posix();assert name not in hashes;io.put(f,root+'/'+name,raw);hashes[name]=H(raw)
   freeze=dict(candidate_root=root,sha256=hashes,old421_allbytes_exact=True,only_small_prelearn_initial_episode_binding_repair=True)
   io.put(f,root+'/reports/SOURCE_FREEZE.json',json.dumps(freeze,indent=2).encode());save('DIRECTION_STARTUP_SOURCE_FREEZE.json',freeze)
  row=run(n,r'''from pathlib import Path
import sys,json,time,torch,subprocess,ast,hashlib
D=Path(ROOT);C=D/'isaac/mod4';sys.path.insert(0,str(D));sys.path.insert(0,str(C));torch.set_num_threads(1)
import supervise_curb20_direction_startup_reviewed_once as own
own.verify();own.wait_existing();assert own.D==D and own.R==D/'reports' and own.CODE==C and own.inherited.D==D
for name in ('train_curb20_direction_startup_reviewed_fresh_preflight_ppo.py',):
 t=(C/name).read_text();ast.parse(t);assert t.index('._write_dynamic(torch.arange(env.num_envs')<t.index('manifest["actual_CURB_episode_direction_scope"]')<t.index('bounded_learn(runner')
assert not torch.cuda.is_initialized()
v=dict(epoch=time.time(),passed=True,CPU_only=True,old_direction_math_runtime_checkpoint_unchanged=True,initialization_binding_before_manifest_and_learning=True,old_failedsmall_before_any_control_or_PPO=True,source_count=len(own.read(D/'reports/SOURCE_FREEZE.json')['sha256']),actual_previous_exits_and_idle_verified=True,physical_reuse=own.read(D/'reports/DIRECTION_REUSED_PHYSICAL_SCOPE_VERIFIED.json'))
(D/'reports/DIRECTION_STARTUP_REVIEWED_CPU_PASSED.json').write_text(json.dumps(v,indent=2))
args=[own.s.q.base.PY,str(D/'supervise_curb20_direction_startup_reviewed_once.py')]
with (D/'controller.log').open('x') as f:p=subprocess.Popen(args,cwd=own.s.q.P,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
row=dict(epoch=time.time(),root=str(D),owner=own.identity(p.pid),argv=args,source_count=v['source_count'],CPU=v,formal_requires_new_small_big_fresh_PASSED=True,no_budget_extension=True)
(D/'reports/DIRECTION_STARTUP_DISPATCH_ACTUAL_RECEIPT.json').write_text(json.dumps(row,indent=2));print(json.dumps(row))
'''.replace('ROOT',repr(root)))
  save('DIRECTION_STARTUP_DISPATCH_ACTUAL_RECEIPT.json',row);save('DIRECTION_STARTUP_ACTIVE_ROOT.json',dict(root=root,source_count=len(hashes),old421_failedsmall_retained=True));print(json.dumps(dict(root=root,source_count=len(hashes),owner=row['owner'],SDK_native_reused=True,newsmall_active_formal_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('DIRECTION_STARTUP_STAGE_DISPATCH_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_old_once_replay=True));raise
