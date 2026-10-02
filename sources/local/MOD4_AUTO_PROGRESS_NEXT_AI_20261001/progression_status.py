from pathlib import Path
import json
import subprocess

ROOT=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930')
HERE=Path(__file__).resolve().parent
s=json.loads((ROOT/'status.json').read_text())
print(json.dumps({k:s.get(k) for k in ['stage','training_pid','supervisor_pid','latest_checkpoint','iteration',
    'remaining_training_seconds','deadline_epoch','evaluation_pid','evaluation_path','active_log']}))
processes=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
    try:
        argv=p.read_bytes().split(b'\0')
        if any(a.endswith((b'/train_mod4_ppo.py',b'/validate_speed.py',b'/mild_parameter_probe.py')) for a in argv):
            processes.append({'pid':int(p.parent.name),'argv':[a.decode(errors='replace') for a in argv if a],
                              'cwd':str((p.parent/'cwd').resolve())})
    except OSError:pass
print(json.dumps({'actual_processes':processes}))
receipt=json.loads((HERE/'confirmation_launch.json').read_text())
out=Path(receipt['output'])
if out.exists():
    from admission_gate import assess
    r=json.loads(out.read_text())
    print(json.dumps({'confirmation':assess(r),'global_closure_m':r['max_closure_after_grace_m'],
                      'global_mimic_rad':r['max_mimic_after_grace_rad']}))
else:
    lines=out.with_suffix('.log').read_text(errors='replace').splitlines()
    print(json.dumps({'confirmation_pending':True,'log_tail':lines[-4:]}))
gpu=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,temperature.gpu',
                    '--format=csv,noheader'],capture_output=True,text=True)
print(json.dumps({'gpu':gpu.stdout.strip()}))
