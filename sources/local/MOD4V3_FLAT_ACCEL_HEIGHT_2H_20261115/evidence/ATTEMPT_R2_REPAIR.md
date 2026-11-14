# R2 objective repair within the original window

IDs: flat-accel-height-native-admit-r2, flat-accel-height-baseline-r2,
flat-accel-height-train-r2, flat-accel-height-stop-request-r2-01,
flat-accel-height-stop-request-r2-02, flat-accel-height-reward-r3.

The full2048 native admission and independent256-case baseline passed runtime
checks. The baseline had51/51 nominal takeoffs and landings, but only1 nominal
settled reward. Inspecting the stored episodes showed long stable holds and low
flight angles in many cases. The blocking condition was mostly takeoff vx exceeding
command+.35m/s, rather than poor physical landing. Example: command.6m/s,
takeoff1.41m/s, rim28.89cm, pitch4.85deg, roll.82deg, stable hold2.56s.

That command-relative upper reward gate overrode the user's height/level priority.
R3 permits forward launches in[.3,2.]m/s to earn height, retains the soft command
overspeed penalty, and retains the original absolute2m/s task reset limit.
No change to the plant, springs, controller, force limits or level/landing gates.

The first stop-request helper failed before executing any remote action because
a generated Python string contained an unescaped newline. The helper was repaired;
the second request wrote only this task's REQUEST_STOP marker. The owner saves full
PPO state at an update boundary and closes itself. No kill or shared-process change.
R3 starts from the original strong H40 parent; the short R2 child and all evidence
are retained, and the original start/deadline cover the repair and new admission.
