"""Prepare one isolated new scope locally; preserve all old implementations."""
from slope_io import *
import shutil,ast
N=W/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011'
PAY=D/'payload';C=PAY/'isaac/mod4'
def write(p,text):
 assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(text.encode())
 if p.suffix=='.py':compile(text,str(p),'exec')
def ren(t):return t.replace('curb20','slope5').replace('CURB','SLOPE').replace('Curb','Slope').replace('curb','slope')
def main():
 assert not PAY.exists()
 for name in ('slope5_geometry.py','slope5_profile.json'):write(C/name,(PRE/'implementation'/name).read_text(encoding='utf8'))
 write(C/'slope5_retention_runtime.py',ren((N/'implementation/curb20_retention_runtime.py').read_text()).replace('configure_slope','configure_slope'))
 state='''"""Derived5degree slope identity; old full DR schema unchanged."""
import hashlib
import e1_terrain_checkpoint as original
from slope5_geometry import PROFILE as PROFILE_PATH,profile
PROFILE='mod4_SLOPE_derived5deg_2m_mirrored_v1'
def validate(state,n):
 assert state['profile']==PROFILE and state['SLOPE_angle_deg']==5. and state['SLOPE_length_m']==2.
 assert state['SLOPE_no_vertical_riser'] and state['SLOPE_derived_not_actual_RM'] and len(state['SLOPE_profile_sha256'])==64
 assert abs(state['SLOPE_height_m']-profile()['height_m'])<1e-12
 return original.validate(dict(state,profile='mod4_intro_gentle_v1'),n)
def current_state(env):
 s=original.current_state(env);s.update(profile=PROFILE,SLOPE_angle_deg=5.,SLOPE_length_m=2.,SLOPE_height_m=profile()['height_m'],SLOPE_no_vertical_riser=True,SLOPE_derived_not_actual_RM=True,SLOPE_profile_sha256=hashlib.sha256(PROFILE_PATH.read_bytes()).hexdigest());validate(s,env.num_envs);return s
def identity(state):return original.identity(state)
'''
 write(C/'slope5_current_state.py',state)
 migration=ren((P/'environment_view_payload/isaac/mod4/curb20_command_migration_environment_view.py').read_text())
 write(C/'slope5_command_migration.py',migration)
 ck=ren((P/'environment_view_payload/isaac/mod4/curb20_full_checkpoint_environment_view.py').read_text())
 ck=ck.replace('slope5_command_migration_environment_view','slope5_command_migration').replace('verified_G3_to_independent_SLOPE20','verified_G3_to_independent_SLOPE5')
 write(C/'slope5_full_checkpoint.py',ck)
 cpu=ren((P/'reviewed_payload/isaac/mod4/curb20_fullsave_cpu.py').read_text()).replace('mod4_SLOPE_derived20mm_strip150_mirrored_v1','mod4_SLOPE_derived5deg_2m_mirrored_v1')
 write(C/'slope5_fullsave_cpu.py',cpu)
 test=ren((P/'payload/isaac/mod4/test_curb_fullstate_cpu.py').read_text())
 test=test.replace("f._env=SimpleNamespace(scene=", "f._env=SimpleNamespace(num_envs=20000,device='cpu',scene=")
 write(C/'test_slope_fullstate_cpu.py',test)
 native=ren((N/'implementation/native_e1_curbscope_probe.py').read_text())
 native=native.replace("np.ptp(heights,axis=1)-.020","np.ptp(heights,axis=1)-2.*np.tan(np.deg2rad(5.))")
 native=native.replace("-.475,.475","-1.4,1.4")
 # Inspect both flat supports bounding the new complete ramp, not just lower plane tiles.
 native=native.replace("points[:,0,0]-=1.;points[:,1,0]+=1.","points[:,0,0]-=1.4;points[:,1,0]+=1.4;")
 write(PAY/'native_e1_slopescope_probe.py',native)
 small=ren((P/'payload/isaac/mod4/train_curb20_fresh_preflight_ppo.py').read_text())
 big=ren((P/'environment_view_payload/isaac/mod4/train_curb20_environment_view_resume_ppo.py').read_text())
 big=big.replace('slope5_full_checkpoint_environment_view','slope5_full_checkpoint')
 start=big.index("    if os.environ.get('RM_SLOPE_PREFLIGHT_SELF_RESUME')=='1':")
 end=big.index('    info["log_dir"] = log_dir',start)
 big=big[:start]+big[end:]
 for name,text in (('train_slope5_fresh_preflight_ppo.py',small),('train_slope5_full_resume_ppo.py',big)):
  text=text.replace("'slope5_command_migration.py','slope5_full_checkpoint.py'","'slope5_command_migration.py','slope5_full_checkpoint.py'")
  write(C/name,text)
 probe=ren((P/'fresh_process_payload/isaac/mod4/probe_curb20_fresh_process_full_resume.py').read_text()).replace('slope5_full_checkpoint_environment_view','slope5_full_checkpoint')
 probe=probe.replace('FRESH_PROCESS_BIG_CORE_VERIFIED.json','SLOPE_BIG_CORE_VERIFIED.json')
 a=probe.index('    install_e1_save_contract(runner,env);saved=')
 b=probe.index('    v=dict(',a)
 probe=probe[:a]+"    assert int(env._sim_step_counter)==0 and hashlib.sha256(source.read_bytes()).hexdigest()==expected['checkpoint']['sha256']\n"+probe[b:]
 probe=probe.replace("own_complete_new_episode_save=dict(path=str(saved),bytes=saved.stat().st_size,sha256=hashlib.sha256(saved.read_bytes()).hexdigest()),","no_optional_logger_save_requested=True,")
 write(C/'probe_slope5_fresh_process_full_resume.py',probe)
 base=ren((P/'payload/supervise_curb20_fullstate_once.py').read_text())
 tree=ast.parse(base)
 funcs={x.name:ast.get_source_segment(base,x) for x in tree.body if isinstance(x,ast.FunctionDef)}
 train=funcs['train'].replace("'train_slope5_full_resume_ppo.py'","'train_slope5_full_resume_ppo.py'")
 train=train.replace("        if discard:assert read(run/'OWN_SAME_SLOPE_FULL_RESUME_PASSED.json')['passed']\n",'')
 train=train.replace("'bounded_E1_G3_command_retention_learning'","'bounded_E1_SLOPE5_independent_learning'")
 fullsave='''def fullsave(path,count=20000):
 import torch
 from slope5_fullsave_cpu import fullsave as validate_full
 info=validate_full(path,count=count);ck=torch.load(path,map_location='cpu',weights_only=False)
 assert ck['independent_terrain_expert']=='E1_SLOPE' and ck['E1_SLOPE_initial_source_sha256']==SOURCE_SHA
 return info
'''
 header='''"""One new isolated SLOPE5 scope, once SDK/native/PPO, fresh fullresume,300s."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,shutil,time,traceback,sys
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4';sys.path.insert(0,str(CODE))
import supervise_e1_command_retention_episode_reviewed_once as inherited
from clock_training_health import learning_health_pass
s=inherited.s;read=inherited.read;write=inherited.write;identity=inherited.identity;freeze_run=inherited.freeze_run
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_FORMAL_DISPATCH_REVIEWED_20261011')
SOURCE_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
def verify():
 inherited.verify_original_records(s.q,D)
 a=read(s.q.ER/'PLAN_APPROVAL.json');assert a['approved'] and 'S3' in a['allowed_stages'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
 rev=read(s.q.ER/'MOE_PLAN_EXECUTION_CURRENT.json')['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_SLOPE'
 f=read(R/'SOURCE_FREEZE.json')['sha256'];old=read(OLD/'reports/SOURCE_FREEZE.json')['sha256'];assert len(old)==389 and all(f[n]==h for n,h in old.items())
 for n,h in f.items():assert s.q.base.sha(D/n)==h,n
 assert read(R/'SLOPE_TARGET_FULLSTATE_CPU_PASSED.json')['passed']
 assert read(R/'SLOPE134_COMPLETE_ACTUAL_REVIEW.json')['review_complete']
def wait_existing():
 st=read(OLD/'reports/E1_STATE.json');assert st['phase']=='E1_CURB20_independent_saved_review_ready' and st['child'] is None
 p=read(OLD/'reports/e1_CURB20_independent_observation_PASSED.json');assert len(p['unique_completed_segment'])==1
 for loc in (st['owner'],read(OLD/'reports/E1_GUARDIAN_STARTED.json'),dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=81560752)):
  a=identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 assert not trainers() and s.q.base.budget_state()['active_segment'] is None and not read(s.q.ctl.STATE_PATH).get('active_training')
def runtime():
 e=inherited.runtime()
 for name in tuple(e):
  if name.endswith('INITIAL_ADMISSION'):e.pop(name)
 e['RM_SLOPE_INITIAL_ADMISSION']='verified_G3_to_independent_SLOPE5';return e
def phase(name,**kw):
 write('E1_STATE.json',dict(epoch=time.time(),phase=name,expert='E1_SLOPE',owner=identity(os.getpid()),**kw))
 s.q.base.status(stage=name,supervisor_pid=os.getpid(),active_code_root=str(D),plan_stage='Approved004 independentSLOPE5, new physical/state scope; first300s then fullfourcase review',active_expert='E1_SLOPE',architecture_variant='A0',physics_dt_s=.0025,solver_position=32,solver_velocity=4,active_log=kw.get('active_log'),normal_episode_resets_continue_learning=True)
inherited.s.verify=verify;s.q.verify=s.q.w.verify=s.q.ctl.verify=lambda:inherited.verify_original_records(s.q,D)
'''
 native_main=ren((N/'implementation/supervise_curb_native_scope_once.py').read_text())
 ta=ast.parse(native_main);native_body=ast.get_source_segment(native_main,next(x for x in ta.body if isinstance(x,ast.FunctionDef) and x.name=='main'))
 a=native_body.index('        results={};env=');b=native_body.index('    except BaseException:',a)
 loop=native_body[a:b];loop='\n'.join(x[4:] for x in loop.splitlines())
 loop=loop.replace('inherited.s.q.base.PY','s.q.base.PY').replace('inherited.s.q.P','s.q.P').replace('inherited.runtime()','runtime()').replace('write(','write(').replace("state('","phase('")
 loop=loop.replace("mod4_SLOPE_derived20mm_strip150_mirrored_v1","mod4_SLOPE_derived5deg_2m_mirrored_v1")
 loop=loop.replace("t['SLOPE_height_m']==.020 and t['SLOPE_strip_width_m']==.150","t['SLOPE_angle_deg']==5. and t['SLOPE_length_m']==2.")
 loop=loop.replace('H(cp)','s.q.base.sha(cp)').replace('H(outpath)','s.q.base.sha(outpath)').replace('B.read_bytes()','s.q.ctl.CANONICAL.read_bytes()').replace('identity=inherited.identity(child.pid)','loc=identity(child.pid)').replace('child=identity,argv','child=loc,argv').replace('child=identity,active_log','child=loc,active_log').replace('own_child_PID_receipt=identity','own_child_PID_receipt=loc')
 loop=loop.replace('source_SHA=SHA','source_SHA=SOURCE_SHA').replace('==SHA','==SOURCE_SHA')
 native_func="def native_contract(cp):\n    budget=s.q.ctl.CANONICAL.read_bytes()\n"+loop+'\n'
 trainers=funcs['trainers'].replace("'train_slope5_full_resume_ppo.py'}","'train_slope5_full_resume_ppo.py','native_e1_slopescope_probe.py','probe_slope5_fresh_process_full_resume.py'}")
 pub=funcs['publish'].replace('133-e1-slope20-independent','135-e1-slope5-independent').replace('E1_SLOPE133','E1_SLOPE135')
 guardian=funcs['guardian']
 fresh='''def fresh_resume(big):
 budget=s.q.ctl.CANONICAL.read_bytes();write('SLOPE_BIG_CORE_VERIFIED.json',big)
 e=runtime();e['RM_SLOPE_FRESH_RESUME_ONLY']='1'
 args=[s.q.base.PY,str(CODE/'probe_slope5_fresh_process_full_resume.py'),'--headless','--num_envs','20000','--max_iterations','0','--steps_per_env','24','--seed','20260928','--learning_rate','.0001','--init_checkpoint',big['checkpoint']['path'],'--log_root',str(D/'fresh_process_resume'),'--run_name','slope_fresh_full_resume_no_learning']
 log=D/'fresh_process_resume.log'
 with log.open('x') as out:p=subprocess.Popen(args,cwd=s.q.P,env=e,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 s.LIVE=p;phase('SLOPE_fresh_same_scope_full_resume_no_PPO',child=identity(p.pid),active_log=str(log),no_PPO=True)
 write('SLOPE_FRESH_RESUME_PID_RECEIPT.json',dict(child=identity(p.pid),argv=args,no_PPO=True))
 while p.poll() is None:time.sleep(2)
 s.LIVE=None;assert p.returncode==0 and 'Traceback (most recent call last)' not in log.read_text()
 proof=read(D/'fresh_process_resume/FRESH_PROCESS_SAME_SLOPE_FULL_RESUME_PASSED.json');assert proof['passed'] and proof['pid']==p.pid and proof['actual_control_steps']==proof['actual_additional_PPO_updates']==0
 assert proof['actual_same_SLOPE_terrain_command_private_CPUCUDA_disk_roundtrip_exact'] and proof['saved_source_episode_plus_one_verified']
 assert s.q.ctl.CANONICAL.read_bytes()==budget
 write('SLOPE_FRESH_PROCESS_SAME_SCOPE_PASSED.json',proof);return proof
'''
 main='''def main():
 import torch;torch.set_num_threads(1)
 assert not (R/'E1_DISPATCH_STARTED.json').exists();verify();wait_existing();init=source()
 s.q.helpers.acquire(s.q.P/'autonomy_controller.lock');s.q.helpers.acquire(s.q.ctl.CANONICAL.parent/'native_floor_supervisor.lock');wait_existing()
 write('E1_INSTALL_BOUNDARY.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_SLOPE',source=inherited.fullsave(init),old389_own_PASSED_actual_exits_two_OS_locks_held_active_empty=True,new_budget_seconds=0))
 write('E1_DISPATCH_STARTED.json',dict(epoch=time.time(),owner=identity(os.getpid()),expert='E1_SLOPE',genuinely_new_scope=True,first_formal_seconds=300,no_oldonce_replayed=True,new_budget_seconds=0))
 with (D/'guardian.log').open('x') as out:g=subprocess.Popen([s.q.base.PY,str(Path(__file__)),'--guardian',str(os.getpid()),str(identity(os.getpid())['start_ticks'])],cwd=s.q.P,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 write('E1_GUARDIAN_STARTED.json',identity(g.pid));native_contract(init)
 _,small=train(init,128,2,900,'slope_discard128',True)
 _,big=train(init,20000,4,900,'slope_discard20k',True)
 fresh=fresh_resume(big)
 write('E1_COMPLETE_PPO_PREFLIGHT_PASSED.json',dict(epoch=time.time(),small=small,big=big,fresh_same_scope=fresh,weights_discarded=True,no_fresh_only_restore_on_stepped_environment=True,SDK_native_new_scope_passed=True,old_clock_DR_exact_reused_no_replay=True))
 saved,row=train(init,20000,10000,min(300,s.left()),'e1_SLOPE5_independent_observation',False)
 assert s.q.base.sha(init)==SOURCE_SHA and saved.is_relative_to(D/'learning_logs')
 write('E1_SLOPE_OWNERSHIP_FINAL_VERIFIED.json',dict(epoch=time.time(),own_checkpoint=row['checkpoint'],output_root=str(D/'learning_logs'),source_SHA_preserved=True,E0_Wave_CURB_not_optimizer_or_save_targets=True))
 publish(saved);write('E1_REVIEW_READY.json',dict(epoch=time.time(),own_saved_source=str(saved),expert='E1_SLOPE',all_courses_finished=False,requires_actual135_fourcase_review=True,automatic_more_PPO_disallowed=True))
 phase('E1_SLOPE5_independent_saved_review_ready',child=None)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:main()
 except BaseException:write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
'''
 write(PAY/'supervise_slope5_independent_scope_once.py',header+fullsave+funcs['source']+'\n'+trainers+'\n'+train+'\n'+native_func+fresh+pub+'\n'+guardian+'\n'+main)
 # Declarative boundary and complete review, not a physics graduation claim.
 review=sorted((PRE/'reports').glob('SLOPE134_ACTUAL_REVIEW_[0-9]*.json'))[-1];rv=json.loads(review.read_bytes());assert rv['review_complete']
 write(R/'SLOPE134_COMPLETE_ACTUAL_REVIEW.json',review.read_text(encoding='utf8'))
 save('SLOPE_SCOPE_PREPARED.json',dict(epoch=time.time(),trial_id='E1-SLOPE5-INDEPENDENT-NEW-SCOPE-01',source_SHA=SHA,full_new_scope_pending=True,payload={x.relative_to(PAY).as_posix():H(x.read_bytes()) for x in PAY.rglob('*') if x.is_file()},new_geometry_only=True,old389_bytes_to_be_preserved=True,new_formal_seconds=300,no_CLOCK45min_replay=True,no_native_PPO_already_started=True))
 print(json.dumps(dict(payload_files=len([x for x in PAY.rglob('*') if x.is_file()]),new_scope_only=True)))
if __name__=='__main__':main()
