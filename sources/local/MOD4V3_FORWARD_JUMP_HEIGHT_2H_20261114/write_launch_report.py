"""Record the actual start and first update of the new finite owner."""
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path

T=Path(__file__).resolve().parent
p=json.loads((T/'PLAN.json').read_bytes())
first=json.loads((T/'evidence/train7200/FIRST_UPDATE.json').read_bytes())
start=json.loads((T/'evidence/train7200/TRAINING_STARTED.json').read_bytes())
check=json.loads((T/'evidence/OBJECTIVE_CHECK.json').read_bytes())
admit=json.loads((T/'evidence/admit_height_r2/ADMISSION.json').read_bytes())
clock=lambda value:datetime.fromtimestamp(value,timezone(timedelta(hours=8))).isoformat()
text=f'''# Forward Jump Height Repair: Two-Hour Training Launch

The user requested repair and launch of jump training. The previous two-hour duration is retained as one new7200-second owner window. Preparation, no-update admission and independent evaluations are outside that window. No old training owner or previous task is restarted.

## Repair

The prior jump rewarded upward speed only through1.5m/s and required only12cm wheel-rim clearance. The new objective derives required upward speed from remaining body height and rewards predicted ballistic apex during push. Measured airborne body-root rise and wheel-rim peak increments provide separate height rewards, weighted by orientation. Success requires both measured height targets, the existing measured tuck and the existing stable landing.

Height curriculum: wheel lower-rim clearance25cm to35cm and body-root rise25cm to32cm, interpolated over the first3600training seconds. Body rise is relative to the measured body-root height immediately before crouch; it is not center-of-mass height. Every independent checkpoint evaluation uses the final35cm/32cm targets, seed10066,51nominal and205fullDR cases. The old complete-sequence metric is retained separately. The observed jump-request flag clears at sequence completion, independently of the stricter height score.

Takeoff requires measured extension followed by unsupported upward flight. Crouch duration, measured-tuck-before-landing-extension logic,10degree pitch/5degree roll flight limits and0.5s landing recovery are retained. Old small-jump demonstrations are disabled. Training-only guidance uses only approach and landed states, decaying0.10to0.02; crouch/push/flight guidance gradients are zero. Only the sampled learned actor drives the plant, with no jump force or velocity assist.

## Inputs And Verification

- Local workspace: `{T}`.
- Remote workspace: `{p['root']}`.
- Parent: prior selected85-minute full PPO checkpoint, iteration{p['parent_iteration']}, SHA`{p['parent_sha256']}`.
- Actor35/critic78/actions6,2.5ms physics, leg100Hz/wheel400Hz/policy50Hz; original MOD4v3 HW300N60R3 assets and motor envelopes; closure10mm and mimic0.01rad episode resets.
- One2048-environment optimizer owner on physical GPU0; optimizer-free fixed evaluation on physical GPU1. Full actor/critic/STD/Adam and RNG restored; fresh physical episodes.
- Reward/guidance regression checks passed: `{check['passed']}`. Native no-update admission passed: `{admit['passed']}`. Source hashes and parent hash were verified after transfer.
- R1 admission and parent evaluation passed before the request-exit correction. R2 uses a separate frozen source directory and plan, a new admission ID and a new fixed parent evaluation ID. Both R1 and R2 reports and the R1 source are retained; neither admission took an optimizer update.
- Existing MuJoCo WASD/one-shot Space player remains available; this trial does not replace its selected model.

## Measured Start

Start: {clock(start['epoch'])}. Deadline: {clock(start['absolute_deadline_epoch'])}. Checkpoints every300seconds. First native PPO update: iteration{first['iteration']}; verified changes: `{first['changes']}`. First complete checkpoint SHA: `{first['checkpoint']['sha256']}`.

Training is running. The35cm goal is an objective, not an achieved-height claim. Actual checkpoint results, failures and final selection are preserved separately.
'''
(T/'LAUNCH_REPORT.md').write_text(text,encoding='utf8')
print(text)
