"""Record negative and partial results without relabeling them as successes."""
import json
from pathlib import Path
import time

T=Path(__file__).resolve().parent
cases=[]
for name in ('sweep_r2','timing22_r3','lowest_stair_r4'):
    result=json.loads((T/'evidence'/name/'RESULT.json').read_bytes())
    cases.extend(dict(**row,run=name) for row in result['cases'])
steps=[row for row in cases if not row['flat'] and not row['no_jump']]
grouped=[]
for height in sorted({round(row['step_height_m'],4) for row in steps}):
    rows=[row for row in steps if abs(row['step_height_m']-height)<1e-5]
    grouped.append(dict(height_m=height,attempts=len(rows),passed=sum(row['accepted'] for row in rows),
                        any_top_contact=sum(row['first_top_contact_s'] is not None for row in rows),
                        both_wheels_top_contact=sum(row['first_both_wheels_top_contact_s'] is not None for row in rows),
                        resets=sum(row['resets'] for row in rows),
                        max_stable_seconds=max(row['max_stable_on_step_s'] for row in rows)))
flat=[row for row in cases if row['flat']]
summary=dict(epoch=time.time(),actual_MuJoCo_physics=True,optimizer_created=False,
             step_attempts=len(steps),step_successes=sum(row['accepted'] for row in steps),heights=grouped,
             flat_controls=[{k:row[k] for k in ('id','accepted','airborne_lower_rim_peak_above_approach_m')} for row in flat],
             cases=cases,live_player_changed=False,training_process_changed=False,
             startup_failure='sweep_r1: manifest path mapping TypeError before physics; source and log retained',
             source_scope='Same saved Isaac Lab-generated tile reconstruction as existing MuJoCo player, one tile per model',
             limitations='Selected deterministic nominal cases and trigger distances only; no universal capability limit or statistical probability claim')
(T/'evidence/SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
lines=['# MuJoCo Jump Onto Official Stair: Results','',
       'The user requested a MuJoCo test of jumping onto a stair. Existing plant, motor limits, timing, drive actor and one-shot learned jump control were reused. Each model contains exactly one saved original terrain tile. No optimizer, jump force, teleport during an attempt, live-player model replacement or training change was used.','',
       '## Measured Results','',
       '| First riser | Jump attempts | Successful stable top landings | Any wheel top touch | Both wheels top support |',
       '|---|---:|---:|---:|---:|']
for row in grouped:
    lines.append(f"| {row['height_m']*100:.1f} cm | {row['attempts']} | {row['passed']} | {row['any_top_contact']} | {row['both_wheels_top_contact']} |")
lines+=['','Success required measured flight, both wheels on the first tread, orientation and vertical-velocity recovery, at least0.5s stable hold and no automatic reset. None of the tested jump attempts reached both-wheel top support, so the negative result does not depend only on the stable-hold threshold.','',
        '## Checkpoints And Controls','',
        'The previous selected85-minute parent and new height-training40/55-minute checkpoints were compared. All use the original five-minute cruise actor before and after the jump. The initial22cm sweep used20/30/40/50/60cm leading-wheel trigger gaps for all three checkpoints. A22cm timing follow-up used54/56/58cm for the40/55-minute checkpoints. The16.5cm lowest official stair used20/30/40/50/60cm for the40/55-minute checkpoints. The forward command was0.6m/s. These are attempts at different trigger distances, not repeated random-seed trials.','',
        '| Flat control | Lower-rim peak above flat ground | Accepted complete jump |','|---|---:|---:|']
for row in flat:
    lines.append(f"| {row['id']} | {row['airborne_lower_rim_peak_above_approach_m']*100:.2f} cm | {row['accepted']} |")
lines+=['','The closest22cm attempt was height055 at58cm trigger distance: a single wheel briefly touched the top, but both-wheel landing and stable hold were not achieved. The16.5cm lowest stair also had one single-wheel top-touch attempt without both-wheel support. Higher measured flat-jump clearance did not translate into reliable stair landing in these tests.','',
        '## Evidence And Limits','',
        'Every physical case has a result and compressed state trajectory. Videos replay those actual MuJoCo states without another integration. R2 replay uses clearer collision-surface colors, a light sky and a camera angle showing the riser; only rendering changes. R1 rendering and source are retained. The first lowest-stair video label rounded16.5cm to17cm; R2 displays16.5cm explicitly.','',
        'The initial sweep_r1 stopped before physics because the report builder passed a duplicate path key. Its source and console error remain preserved, and the corrected physical run has a new sweep_r2 ID.','',
        'This result covers the selected checkpoints, nominal MuJoCo physics, original terrain and trigger distances. It is not a proof of the mechanical maximum or impossibility at all possible commands. No new training was launched by this test.']
(T/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(json.dumps(dict(step_attempts=summary['step_attempts'],step_successes=summary['step_successes'],heights=grouped),indent=2))
