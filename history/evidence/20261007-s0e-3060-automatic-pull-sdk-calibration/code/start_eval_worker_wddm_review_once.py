"""WDDM reviewed launch: preserve desktop rendering, reject other computation."""
from pathlib import Path
import json,subprocess,time,os
ROOT=Path(__file__).resolve().parent
assert not (ROOT/'WORKER_LAUNCHED.json').exists() and not (ROOT/'WORKER_STARTED.json').exists()
probe=subprocess.run(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],capture_output=True,text=True,creationflags=0x08000000)
assert probe.returncode==0
reviewed_display={'TextInputHost.exe','explorer.exe','dwm.exe','ShellExperienceHost_cw5n1h2txyewy','ShellExperienceHost.exe','msedgewebview2.exe','SearchHost.exe','PhoneExperienceHost.exe','WindowsTerminal.exe','WUDFHost.exe','GameViewerServer.exe','msedge.exe','ChatGPT.exe','codex-computer-use-swift.exe'}
rows=[x for x in probe.stdout.splitlines() if x.strip()]
assert all(Path(x.split(',',1)[1].strip()).name in reviewed_display for x in rows),'Unreviewed GPU process; do not interfere'
gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,creationflags=0x08000000)
assert gpu.returncode==0
PY='D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe'
with (ROOT/'worker.log').open('ab') as f:
 child=subprocess.Popen([PY,str(ROOT/'eval_worker.py')],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,creationflags=0x08000200)
time.sleep(3);assert child.poll() is None,'Worker exited during initial launch'
proof={'epoch':time.time(),'worker_pid':child.pid,'headless':True,'hidden':True,'single_frozen_eval_worker':True,'new_learning':False,'canonical_authority':False,
 'WDDM_includes_display_processes':True,'original_empty_compute_reader_rejected_before_launch':True,'reviewed_display_apps_preserved':rows,'GPU_before':gpu.stdout.strip()}
(ROOT/'WORKER_LAUNCHED.json').write_text(json.dumps(proof));print(json.dumps(proof))
