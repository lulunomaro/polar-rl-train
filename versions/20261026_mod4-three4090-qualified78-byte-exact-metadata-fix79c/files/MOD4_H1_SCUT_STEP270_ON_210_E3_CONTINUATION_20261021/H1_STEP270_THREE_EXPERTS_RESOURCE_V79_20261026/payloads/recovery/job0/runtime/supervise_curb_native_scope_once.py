"""Unique CURB SDK/native parent; no optimizer learning, budget transaction or resume."""
from pathlib import Path
import fcntl,hashlib,json,os,subprocess,sys,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';CODE=D/'isaac/mod4'
sys.path.insert(0,str(D));sys.path.insert(0,str(CODE))
import supervise_e1_command_retention_episode_reviewed_once as inherited
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
def write(name,v):
    p=R/name;assert not p.exists(),name;p.write_bytes(json.dumps(v,indent=2).encode())
def state(phase,**kw):
    p=R/'CURB_NATIVE_SCOPE_STATE.json';raw=json.dumps(dict(epoch=time.time(),phase=phase,owner=inherited.identity(os.getpid()),**kw),indent=2).encode()
    tmp=p.with_name(p.name+'.'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,p)
def verify():
    f=json.loads((R/'SOURCE_FREEZE.json').read_bytes())['sha256']
    assert all(H(D/n)==h for n,h in f.items())
    old=json.loads((Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010')/'reports/SOURCE_FREEZE.json').read_bytes())['sha256']
    assert len(old)==366 and all(f[n]==h for n,h in old.items())
    approved=json.loads((Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports/MOE_PLAN_EXECUTION_CURRENT.json')).read_bytes())
    assert approved['terrain_subexpert_revision004']['approved']
    assert not inherited.trainers(), 'A trainer is actually active; do not overlap'
    assert json.loads(B.read_bytes())['active_segment'] is None
def main():
    assert not (R/'CURB_NATIVE_SCOPE_STARTED.json').exists()
    budget=B.read_bytes();l=json.loads(budget);assert l['authorized_training_seconds']==828000 and l['active_segment'] is None
    locks=[]
    try:
        for p in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
            f=p.open('r');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
        verify();selection=json.loads((R/'SOURCE_SELECTED.json').read_bytes());cp=Path(selection['path']);assert H(cp)==SHA
        write('CURB_NATIVE_SCOPE_STARTED.json',dict(epoch=time.time(),owner=inherited.identity(os.getpid()),source_SHA=SHA,source_count=len(json.loads((R/'SOURCE_FREEZE.json').read_bytes())['sha256']),
            no_PPO_or_budget_authority=True,two_original_OS_locks_held_for_single_GPU_native_scope=True))
        results={};env=inherited.runtime()
        for name in tuple(env):
            if name.endswith('INITIAL_ADMISSION'):env.pop(name)
        for count,steps,label in ((10,300,'CURB_SDK10'),(20000,120,'CURB_NATIVE20K')):
            verify();outpath=D/(label+'.json');log=D/(label+'.log');assert not outpath.exists() and not log.exists()
            args=[inherited.s.q.base.PY,str(D/'native_e1_curbscope_probe.py'),'--headless','--dt','.0025','--checkpoint',str(cp),'--output',str(outpath),
                '--num_envs',str(count),'--warmup','0' if count==10 else '24','--steps',str(steps),'--profile_steps','0']
            with log.open('x') as out:child=subprocess.Popen(args,cwd=inherited.s.q.P,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
            identity=inherited.identity(child.pid)
            write(label+'_PID_RECEIPT.json',dict(epoch=time.time(),child=identity,argv=args,no_PPO=True,source_SHA=SHA))
            state('CURB_new_SDK_native_no_PPO',child=identity,active_log=str(log),scope=label)
            while child.poll() is None:time.sleep(5)
            assert child.returncode==0 and 'Traceback (most recent call last)' not in log.read_text(errors='replace'),label
            v=json.loads(outpath.read_bytes())
            assert v['PPO_update_count']==0 and not v['nonfinite'] and v['actual_task_failed_environments']==0
            assert v['physical_callback_count']==steps*4 and v['health']['actual_physics_callbacks']==(steps+(24 if count==20000 else 0))*4
            assert v['E1_actual_ground_error_m']<=1e-6 and v['E1_height_reward_formula_error']<=1e-6
            t=v['E1_terrain_identity'];assert t['profile']=='mod4_CURB_derived20mm_strip150_mirrored_v1' and t['CURB_height_m']==.020 and t['CURB_strip_width_m']==.150
            assert v['actual_solver_readback']['all_position32_velocity4'] and v['physical_action_delay_audit']['application_formula_max_error']==0
            hist=v['command_retention']['sample_histogram'];assert v['command_retention']['projection_error']<=1e-6
            assert all(sum(row[2:6])==0 for row in hist[:1]+hist[2:]) and not v['command_retention']['pure_high_spin']
            if count==10:
                assert v['sensor_sdk_audit']['selected_reset']['other_bias_episode_exact'] and v['SDK_CURB_actual_assignment_placement']['lower_upper_front_support_both_mirrors']
                assert v['command_retention']['eligible']==0 and sum(hist[1][2:6])==0
            else:assert all(hist[1][i]>0 for i in (2,3,4,5))
            assert B.read_bytes()==budget and H(cp)==SHA
            results[label]=dict(path=str(outpath),sha256=H(outpath),own_child_PID_receipt=identity,callbacks=steps*4,
                closure_m=v['max_closure_error_m'],ground_error_m=v['E1_actual_ground_error_m'],reward_formula_error=v['E1_height_reward_formula_error'],
                passed=True,no_PPO=True,canonical_bytes_preserved=True)
            write(label+'_PASSED.json',results[label])
        write('CURB_NATIVE_SCOPE_PASSED.json',dict(epoch=time.time(),results=results,no_PPO_or_optimizer_update=True,canonical_bytes_preserved=True,full_CURB_CPUCUDA_resume_and_PPO_pending=True))
        state('CURB_new_native_contract_complete_review_ready',child=None,results=results,no_PPO=True)
    except BaseException:
        write('CURB_NATIVE_SCOPE_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),no_PPO_or_budget_transaction=True,original_error_retained=True,no_blind_resume=True))
        state('CURB_native_contract_attention',child=None,no_PPO=True);raise
    finally:
        for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
if __name__=='__main__':main()
