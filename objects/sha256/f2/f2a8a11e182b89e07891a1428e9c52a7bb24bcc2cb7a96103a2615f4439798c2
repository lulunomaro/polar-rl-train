"""Two isolated frozen ablations. Never pauses, launches or accounts a trainer."""
from pathlib import Path
import fcntl, json, os, signal, subprocess, time, traceback
import supervise_native_floor as base
from admission_gate import assess

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reports/sensor_ablation_model15150_20261003'
OLD=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
CK=OLD/'logs/2026-10-02_22-43-49_scut_spin_rate_continued/model_15150.pt'
SHA='0756a196ba918a725afd44bd2bdf60acd3ee3f9d083e7b0fc1fad49838d299a0'
PROBES={'validate_speed.py','spin_probe.py','spin_rate_probe.py','spin_fullscale_probe.py','spin_rate_fullscale_probe.py','sensor_readback_probe.py'}
CHILD=None

def read(p): return json.loads(p.read_text())
def live_probes(exclude=None):
    found=[]
    for proc in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            pid=int(proc.parent.name)
            if pid==exclude: continue
            argv=[v.decode(errors='replace') for v in proc.read_bytes().split(b'\0') if v]
            if any(Path(v).name in PROBES for v in argv): found.append(pid)
        except OSError: pass
    return found

def state(**kw):
    current=read(OUT/'status.json') if (OUT/'status.json').exists() else {}
    current.update(kw,updated_epoch=time.time(),worker_pid=os.getpid(),frozen_only=True,ppo_performed=False,
                   production_root=str(OLD),budget_added=False)
    base.atomic_json(OUT/'status.json',current)

def stop_own():
    if CHILD and CHILD.poll() is None:
        CHILD.send_signal(signal.SIGINT)
        try: CHILD.wait(timeout=60)
        except subprocess.TimeoutExpired: CHILD.kill();CHILD.wait()

def main():
    global CHILD
    OUT.mkdir(exist_ok=True)
    lock=(OUT/'worker.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert base.checkpoint(CK)['sha256']==SHA
    original_off=read(ROOT/'reports/latest4rad_before_handover_flat_off_20261002.json')
    combined=read(ROOT/'reports/latest4rad_before_handover_flat_sensor_20261002.json')
    assert original_off['checkpoint']==combined['checkpoint']==str(CK)
    assert original_off['seed']==combined['seed']==20261002
    results=[]
    for profile in ('sensor_noise_v1','sensor_delay_v1'):
        complete=None
        for attempt in range(1,4):
            path=OUT/f'flat_{profile}_attempt{attempt}.json'
            if path.exists(): complete=path;break
            log=path.with_suffix('.log')
            if log.exists(): continue
            state(stage='waiting_existing_evaluator',profile=profile,evaluation_pid=None)
            while live_probes():time.sleep(5)
            args=['isaac/mod4/validate_speed.py','--headless','--checkpoint',str(CK),
                  '--seed','20261002','--dr-profile','white_v1','--sensor-profile',profile,
                  '--num_envs','80','--steps','1500','--speed_limit','1.5','--ramp_suite','--output',str(path)]
            CHILD=base.spawn(args,log)
            state(stage='running_frozen_ablation',profile=profile,evaluation_pid=CHILD.pid,active_log=str(log))
            until=time.time()+1800; yielded=False
            while CHILD.poll() is None:
                if live_probes(CHILD.pid):
                    stop_own();yielded=True
                    state(stage='yielded_to_production_evaluation',evaluation_pid=None,aborted_log=str(log))
                    break
                if time.time()>until:stop_own();raise TimeoutError(str(log))
                time.sleep(2)
            rc=CHILD.returncode;CHILD=None
            if yielded:continue
            assert rc==0 and path.exists(),(profile,rc,str(log))
            complete=path;break
        assert complete, 'Three attempts used; keep logs and resume explicitly with new paths'
        r=read(complete);a=r['sensor_audit']
        assert a['profile']==profile
        assert r['checkpoint']==str(CK) and r['seed']==20261002 and r['seconds']>=15
        exact=all(r[k]==original_off[k] for k in ('reset_root_before_physics','reset_joint_pos_before_physics'))
        assert exact, 'Initial state mismatch: ablation invalid'
        if profile=='sensor_noise_v1':assert a['lag_steps_max']==0
        else:
            assert all(v==0 for v in a['observed_packet_error_max'].values())
            assert all(v==0 for v in a['bias_abs_max'].values())
            assert a['actual_lag_steps']==combined['sensor_audit']['actual_lag_steps']
        results.append(dict(profile=profile,report=str(complete),same_initial_root_q=exact,admission=assess(r),sensor_audit=a))
        state(stage='ablation_completed',evaluation_pid=None,results=results)
    base.atomic_json(OUT/'comparison.json',dict(checkpoint=base.checkpoint(CK),seed=20261002,
        original_off_admission=assess(original_off),combined_admission=assess(combined),ablations=results,
        source_reports_preserved=True,production_deployed=False,production_changed=False,
        causal_scope='Controlled single-seed frozen input-component evidence, not a universal cause or trained DR acceptance'))
    state(stage='finished',evaluation_pid=None,comparison=str(OUT/'comparison.json'))

if __name__=='__main__':
    try:main()
    except Exception:
        stop_own();state(stage='attention_required',evaluation_pid=None,error=traceback.format_exc());raise
