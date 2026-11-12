"""Frozen actors on local nominal flat with2.5/10/20ms timing. No original source edits."""
from pathlib import Path
import sys,json
T=Path(__file__).resolve().parent;R=T.parents[2]
sys.path.insert(0,str(R/'sources/local/MOD4V3_STEP7_DELAY_DIAG_20261110'))
import replay_delay_diagnostic as replay
original=replay.Simulation
def aligned(args):
 s=original(args);s.env.dt=.0025;s.env.decim=8;s.env.m.opt.timestep=.0025;return s
replay.Simulation=aligned
plan=json.loads((T/'CHECKPOINT_EVAL_TEMPLATE.json').read_text(encoding='utf8'))
plan['models']={'parent':str(R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/model/training_checkpoint.pt'),**{f'{m:03d}m':str(T/f'weights/model_{m:03d}m.pt') for m in (5,10,15,20) if (T/f'weights/model_{m:03d}m.pt').exists()}}
plan['timing_override']={'physics_s':.0025,'PD_s':.01,'policy_s':.02,'unchanged_delay_seconds':True,'scope':'MuJoCo nominal, not native fullDR'}
p=T/'evidence/ALIGNED_FLAT_EVAL_PLAN.json';p.write_text(json.dumps(plan,indent=2),encoding='utf8')
sys.argv=['replay_delay_diagnostic.py','--plan',str(p),'--out',str(T/'evidence/ALIGNED_FLAT_EVAL.json')];replay.main()
