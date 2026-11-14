"""Describe completed preparation and measured first update, with no completion claim."""
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
T=Path(__file__).resolve().parent
p=json.loads((T/'PLAN.json').read_bytes())
first=json.loads((T/'evidence/train7200/FIRST_UPDATE.json').read_bytes())
start=json.loads((T/'evidence/train7200/TRAINING_STARTED.json').read_bytes())
guide=json.loads((T/'evidence/GUIDANCE_NO_UPDATE.json').read_bytes())
clock=lambda t:datetime.fromtimestamp(t,timezone(timedelta(hours=8))).isoformat()
text=f'''# Moving Jump Repair: New Two-Hour PPO Run

The user authorized repair followed by another two hours of moving-jump learning on Host72. This is a new task with a fresh7200-second continuous owner window; repair and admission are outside that window. Host210 and the existing viewer were not touched.

## Evidence And Repair

Previous R3best nominal fixed cases:51takeoffs,51air-balance passes,0measured retractions,0complete successes. Minimum nominal airborne leg difference median1.055rad, range1.018-1.133rad; required<0.9rad. Flight teacher-fit MSE was substantially above other phases. Native PPO already clips actor and critic separately, so critic gradient magnitude is not a demonstrated direct actor-clipping cause.

The old airborne reward switched to extension as soon as vz<0, and the teacher/cue switched at vz<-0.10, irrespective of measured retraction. The repair requires measured tuck before landing preparation in reward, observed command and training labels. Thresholds and success rules are unchanged. Online guidance now averages each present phase and weights flight4; equal-phase demonstrations also weight flight4. Only learned actor actions drive the training plant.

The40ms teacher probe achieved nominal51/51retractions but only37/51complete passes because14cases exceeded10degree air pitch. Its raw failures and source are retained. The final teacher restores the original80ms ramp. Final native teacher complete nominal: {guide['nominal_teacher_complete']}. Successful dataset metadata: {json.dumps(guide['metadata'])}. These are teacher collection results, not learned-policy successes.

Native runtime admission passed original assets, motor limits and physical timing. No-update guidance loss={guide['loss']:.6f}, finite gradient norm={guide['gradient_norm']:.6f}; no optimizer was created or stepped for that check. Physical runtime admission restored PPO state but took zero updates.

## Frozen Parents And Runtime

- Root five-minute parent SHA: `{p['root_parent_sha256']}`.
- Best prior learned child used for full PPO continuation: `{p['parent_sha256']}`, iteration{p['parent_iteration']}.
- Remote workspace: `{p['root']}`.
- Physical GPU0: one2048-environment optimizer owner; GPU1: fixed independent evaluation without an optimizer.
- Actor35, critic78, actions6; full actor/critic/STD/17Adam states and RNG restored, fresh physical episodes.
-2.5ms/TGS32/4; leg100Hz/wheel400Hz/policy50Hz;10mm closure and0.01rad mimic single-episode resets; motor envelopes and assets unchanged.
- Phase-command input semantics are versioned and require a matching deployment input producer. This is a simulation trial, not production promotion.

## Actual Learning Start

Start: {clock(start['epoch'])}. Target end: {clock(start['absolute_deadline_epoch'])}. First measured PPO update iteration: {first['iteration']}. Changes verified: `{first['changes']}`. Full first-update checkpoint: `{first['checkpoint']['sha256']}`.

Training and evaluation are in progress. No success or completion claim is made by this launch record. Final selection will use standalone deterministic actor evaluation on51nominal/205fullDR fixed cases, retain later terminations as failures, and preserve every intermediate checkpoint and failed attempt.
'''
(T/'LAUNCH_REPORT.md').write_text(text,encoding='utf8')
print(text)
