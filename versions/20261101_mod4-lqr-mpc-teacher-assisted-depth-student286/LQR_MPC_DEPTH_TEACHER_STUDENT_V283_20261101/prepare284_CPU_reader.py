"""Independent CPU-reader purpose; CUDA RNG is not a CPU generator state."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent
p=N/'review283_actual_carrier_CPU_once.py'
text=p.read_text('utf8').replace('CPU283','CPU284')
text=text.replace("wm.generator.set_state(carrier['world_model']['dedicated_sampling_rng'].cpu())",
    "wm.generator.manual_seed(284)  # dedicated CPU admission RNG; production retains exact CUDA state")
out=N/'review284_actual_carrier_CPU_once.py'
with out.open('x',encoding='utf8')as f:f.write(text)
ast.parse(text)
(N/'reports/CPU284_READER_RNG_REPAIR_BEFORE_USE.json').write_text(json.dumps(dict(
 epoch=time.time(),trial_id='teacher284-cpu-reader-rng-repair',predecessor_CPU283_false_preserved=True,
 original_reader_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),new_reader_SHA=hashlib.sha256(out.read_bytes()).hexdigest(),
 repair='CUDA Philox16B cannot initialize CPU MT19937; fresh declared284 CPU test seed. No production RNG change.',
 reason_for_new_carrier_read='new corrected CPU integration purpose after original pre-migration failure',
 source_model_or_physics_changed=False),indent=2),encoding='utf8')
