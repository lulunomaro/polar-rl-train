# MuJoCo Jump Onto Official Stair: Results

The user requested a MuJoCo test of jumping onto a stair. Existing plant, motor limits, timing, drive actor and one-shot learned jump control were reused. Each model contains exactly one saved original terrain tile. No optimizer, jump force, teleport during an attempt, live-player model replacement or training change was used.

## Measured Results

| First riser | Jump attempts | Successful stable top landings | Any wheel top touch | Both wheels top support |
|---|---:|---:|---:|---:|
| 16.5 cm | 10 | 0 | 1 | 0 |
| 22.0 cm | 21 | 0 | 1 | 0 |

Success required measured flight, both wheels on the first tread, orientation and vertical-velocity recovery, at least0.5s stable hold and no automatic reset. None of the tested jump attempts reached both-wheel top support, so the negative result does not depend only on the stable-hold threshold.

## Checkpoints And Controls

The previous selected85-minute parent and new height-training40/55-minute checkpoints were compared. All use the original five-minute cruise actor before and after the jump. The initial22cm sweep used20/30/40/50/60cm leading-wheel trigger gaps for all three checkpoints. A22cm timing follow-up used54/56/58cm for the40/55-minute checkpoints. The16.5cm lowest official stair used20/30/40/50/60cm for the40/55-minute checkpoints. The forward command was0.6m/s. These are attempts at different trigger distances, not repeated random-seed trials.

| Flat control | Lower-rim peak above flat ground | Accepted complete jump |
|---|---:|---:|
| parent085_flat | 22.66 cm | True |
| height040_flat | 25.28 cm | True |
| height055_flat | 27.44 cm | True |

The closest22cm attempt was height055 at58cm trigger distance: a single wheel briefly touched the top, but both-wheel landing and stable hold were not achieved. The16.5cm lowest stair also had one single-wheel top-touch attempt without both-wheel support. Higher measured flat-jump clearance did not translate into reliable stair landing in these tests.

## Evidence And Limits

Every physical case has a result and compressed state trajectory. Videos replay those actual MuJoCo states without another integration. R2 replay uses clearer collision-surface colors, a light sky and a camera angle showing the riser; only rendering changes. R1 rendering and source are retained. The first lowest-stair video label rounded16.5cm to17cm; R2 displays16.5cm explicitly.

The initial sweep_r1 stopped before physics because the report builder passed a duplicate path key. Its source and console error remain preserved, and the corrected physical run has a new sweep_r2 ID.

This result covers the selected checkpoints, nominal MuJoCo physics, original terrain and trigger distances. It is not a proof of the mechanical maximum or impossibility at all possible commands. No new training was launched by this test.
