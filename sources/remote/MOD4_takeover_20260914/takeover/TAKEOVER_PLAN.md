# MOD4 8-hour takeover plan

The run uses one GPU process at a time and an OS lock.  It warm-starts the last mature
mixed policy, adds a 5-frame actor history, and retains ordinary locomotion in every stage.
All stages use the same 35-D current-frame semantics, six-action order, USD, joint limits,
action scales and Isaac control gains.

Stages are fixed before launch: foundation; step/rough/spin; fly/jump; full nominal mix;
mild domain randomization; then full domain randomization until the protected deadline.
Every stage writes an exact source/asset/environment manifest and saves every 50 iterations.
If the wall-clock deadline interrupts a stage, the newest complete checkpoint is selected.

Final acceptance is independent of training counters.  Three seeds are run for nominal and
DR physics.  Each report contains completed episodes, failure reasons, closure/mimic maxima,
fly launch/air/landing flags and tunnel entry.  Target bars: run >= 0.80; ramp/step/rough/spin
>= 0.60; fly complete >= 0.50 and air-after-launch >= 0.60; no closure or mimic termination;
DR completion loss no more than 0.20 absolute on core locomotion.  MuJoCo evaluation uses the
exported action/observation contract and the verified 320/10/90 leg PI loop.
