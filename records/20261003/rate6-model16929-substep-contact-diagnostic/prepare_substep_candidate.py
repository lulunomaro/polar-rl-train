"""One-time isolated source preparation and CPU arithmetic verification, no app."""
import ast,hashlib,json,shutil,subprocess,sys,time
from pathlib import Path
FILES=Path(__file__).resolve().parent
ROOT=Path('/home/egde/rl_candidates/MOD4_rate6_substep_diagnostic_20261003')
OLD=Path('/home/egde/rl_candidates/MOD4_rate6_contact_repair_20261003')
assert not ROOT.exists(),'Do not repeat isolated preparation'
ROOT.mkdir();shutil.copytree(OLD/'isaac',ROOT/'isaac',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
shutil.copytree(OLD/'train',ROOT/'train');(ROOT/'reports').mkdir()
code=ROOT/'isaac/mod4'
for n in ['spin_substep_probe.py','substep_contact_readback.py','test_substep_contact.py']:
 shutil.copyfile(FILES/n,code/n);ast.parse((code/n).read_text())
result=subprocess.run([sys.executable,str(code/'test_substep_contact.py')],cwd=ROOT,capture_output=True,text=True)
receipt=dict(stage='prepared_cpu_passed' if result.returncode==0 else 'isolated_CPU_error',PPO_performed=False,production_changed=False,ledger_authority=False,epoch=time.time(),cpu_stdout=result.stdout,cpu_stderr=result.stderr,source_hashes={n:hashlib.sha256((code/n).read_bytes()).hexdigest() for n in ['spin_substep_probe.py','substep_contact_readback.py','test_substep_contact.py','mod4_task.py','mod4_env.py','contact_capture.py','contact_geometry.py']})
(ROOT/'reports/SUBSTEP_DIAGNOSTIC_PREPARED.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt));assert result.returncode==0,'CPU diagnostic arithmetic must pass before simulation'
