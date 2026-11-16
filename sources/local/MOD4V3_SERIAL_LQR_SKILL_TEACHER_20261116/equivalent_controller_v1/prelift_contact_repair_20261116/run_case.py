from pathlib import Path
import sys,json,hashlib,shutil
P=Path(__file__).resolve().parent;E=P.parent
sys.path.insert(0,str(E))
from run_teacher import run
case=json.loads(sys.argv[1]);out=P/case['name'];out.mkdir(exist_ok=False)
files=['native_contact_latch.py','sim/controller.py','sim/step_climb.py','native_runtime.py','native_contacts.py','native_actuation.py','run_teacher.py','data/lqr_gain_fit.py']
for s in files:
 dst=out/'code'/s;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(E/s,dst)
(out/'SOURCE.json').write_text(json.dumps({s:hashlib.sha256((E/s).read_bytes()).hexdigest()for s in files},indent=2))
run(case,out)
