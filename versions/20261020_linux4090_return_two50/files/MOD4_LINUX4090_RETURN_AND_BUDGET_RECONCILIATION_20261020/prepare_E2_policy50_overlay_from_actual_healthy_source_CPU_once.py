from pathlib import Path
import ast,hashlib,json,shutil,time,traceback
import torch
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;F=W/'MOD4_POLICY_50HZ_CONTINUATION_20261020';OLD=W/'MOD4_SCUT_FUDAN_EIGHTEENTH_HOUR_20261019/payload/e2';OUT=B/'E2_policy50_overlay'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert not OUT.exists();OUT.mkdir();changes=[];baseline=json.loads((F/'reports/POLICY50_ISOLATED_OVERLAY_AND_CLOCK_COMPONENTS_CPU_ACTUAL.json').read_bytes())
 for row in baseline['changes']:
  rel=row['relative']
  if rel.endswith(('e3_public_recovery_phase_v1.py','train_E3_fullstate_v1.py','recovery_worker.py')):continue
  p=OLD/rel;assert H(p)==row['baseline_SHA'];new=F/'controller50V5/overlay'/rel;dest=OUT/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(new,dest);changes.append(dict(relative=rel,old_SHA=H(p),new_SHA=H(dest),same_before_bytes_as_actual_E3_50Hz_migration=True))
 inner='job0/runtime/isaac/mod4/physics_clock.py';p=OLD/inner;assert H(p)==H(OLD/'job0/runtime/physics_clock.py');shutil.copy2(OUT/'job0/runtime/physics_clock.py',OUT/inner);changes.append(dict(relative=inner,old_SHA=H(p),new_SHA=H(OUT/inner)))
 rel='job0/runtime/isaac/mod4/train_E2_full_resume_v1.py';p=OLD/rel;s=p.read_text('utf8');assert 'gamma=0.99' in s and 'lam=0.95' in s;s=s.replace('gamma=0.99','gamma=0.9801').replace('lam=0.95','lam=0.9025');(OUT/rel).write_text(s,encoding='utf8');changes.append(dict(relative=rel,old_SHA=H(p),new_SHA=H(OUT/rel)))
 p=OLD/'native_admission_worker.py';s=p.read_text('utf8');s=s.replace("phase=args.phase;out=j/phase;out.mkdir();assert args.job==0 or phase=='native'","phase=args.phase;assert args.job==0 and phase in ('native','production');out=j/('clock_native50' if phase=='native' else phase);out.mkdir()")
 s=s.replace("assert H(source)==task['source_SHA'];N=", "assert H(source)==task['source_SHA'];assert task['policy_clock_migration_authorized'] and task['source_policy_hz'] in (50,100);N=")
 s=s.replace(" m=json.loads((j/'original_run_manifest.json').read_bytes());", " os.environ['MOD4_RESUME_QUEUE_CONTROL_US']=str(1000000//task['source_policy_hz'])\n m=json.loads((j/'original_run_manifest.json').read_bytes());")
 needle=" sys.path[:0]=[str(B/'lib'),str(j/'runtime/isaac/mod4')];";assert needle in s;s=s.replace(needle," assert int(m['env'].get('RM_SPAWN_GRACE_STEPS','10'))==10\n os.environ['RM_SPAWN_GRACE_STEPS']='5'\n"+needle)
 s=s.replace("v['owned_phase_complete_updates']=updates;torch.save(v,tmp)","v['owned_phase_complete_updates']=updates;v['policy_clock']=dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_sampling_hz=100,source_policy_hz=task['source_policy_hz']);torch.save(v,tmp)")
 assert "{772320+updates*20}" in s;s=s.replace('{772320+updates*20}',"{task['source_Adamstep']+updates*20}")
 z="  zero=save(out/'own_startup0.pt',0);";assert z in s
 s=s.replace(z,"  assert env.physics_dt==.0025 and env.step_dt==.02 and env.cfg.decimation==8\n  env._physics_action_delay.queue.control_us=20000\n  put(out/'POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json',dict(policy_hz=50,control_period_s=.02,physics_dt_s=.0025,decimation=8,feedback_sampling_hz=100,contact_bin_s=.005,action_transition_delay_us=[0,2500,5000],source_policy_hz=task['source_policy_hz'],source_SHA=task['source_SHA'],gamma=.9801,lam=.9025,rollout_decisions=24,rollout_simulated_seconds=.48))\n"+z)
 actual=(F/'controller50V5/overlay/recovery_worker.py').read_text('utf8');start=actual.index('  if native:\n');end=actual.index('  go=json.loads',start);block=actual[start:end].replace('if native:','if phase==\'native\':').replace('OUT','out').replace('s[k]','src[k]')
 start=s.index("  if phase=='native':\n");end=s.index('  completed=0;',start);s=s[:start]+block+s[end:]
 assert "OWN_E2_H1_KIND=task['kind']" in s and "source=j/'source/E2_closed_hour241.pt'" in s;ast.parse(s);(OUT/'native_admission_worker.py').write_text(s,encoding='utf8');changes.append(dict(relative='native_admission_worker.py',old_SHA=H(p),new_SHA=H(OUT/'native_admission_worker.py')))
 assert all(ast.parse(p.read_text('utf8')) for p in OUT.rglob('*.py'))
 source=W/'MOD4_SCUT_FUDAN_SEVENTEENTH_HOUR_20261019/actual_closed_three_finals/e2/model_update241.pt';assert source.stat().st_size==14615528 and H(source)=='48150f0dc8f279a421cb84462fcefce7a0632c3ba5eaf721f37bb74d4c26bbb8';torch.set_num_threads(2);rng=torch.get_rng_state().clone();state=torch.load(source,map_location='cpu',weights_only=False);counts=[0,0]
 def finite(v):
  if torch.is_tensor(v):counts[0]+=1;counts[1]+=int(v.is_floating_point());assert not v.is_floating_point() or torch.isfinite(v).all()
  elif isinstance(v,dict):
   for x in v.values():finite(x)
  elif isinstance(v,(tuple,list)):
   for x in v:finite(x)
 finite(state);assert counts==[175,98] and len(state['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in state['optimizer_state_dict']['state'].values()}=={772320}
 phase=(OLD/'job0/runtime/isaac/mod4/e2_directional_spin_runtime_v1.py').read_text('utf8');tree=ast.parse(phase);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='transition_yaw');scope={'torch':torch};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual E2 seconds command profile>','exec'),scope);f=scope['transition_yaw'];ts=torch.tensor([0.,1.,4.,5.,6.,7.,10.,11.,12.]);assert torch.equal(f(ts,4.),torch.tensor([0.,4.,4.,0.,0.,-4.,-4.,0.,0.]));assert 'self._dt = float(env.step_dt)' in phase and 'self.phase_elapsed += self._dt' in phase
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized();put('E2_POLICY50_ISOLATED_OVERLAY_SOURCE_AND_SECONDS_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed_CPU=True,source=dict(path=str(source),SHA=H(source),bytes=source.stat().st_size,Adam=772320,tensor_counts=counts),changes=changes,original_E2_seconds_command_profile_retained=True,gamma=.9801,lam=.9025,physics_dt=.0025,policy_dt=.02,feedback100Hz=True,spawn_grace100ms=True,native_protocol='future 24 policy /192 physics callbacks /0optimizer; original native144 not replayed',source_full175_98finite_17Adam_CPU=True,target_SDK_and_actual_GPU_admission=False,original_canonical_not_written=True,no_training_or_new_GO=True))
 print(json.dumps(dict(E2_policy50_CPU_overlay_prepared=True,changes=len(changes),target_admission=False)))
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_POLICY50_OVERLAY_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_remote_write=True));raise
