# Requested original driver, real RM7v7 full terrain, latest MoE and jump references

The prior local-player delivery used the wrong window/arena. User explicitly corrected
it to MOD4_LOCAL_MUJOCO_DRIVE_20261008, then clarified that the supplied real RM7v7
map was required. That earlier delivery remains a preserved wrong-target attempt;
its successful interface tests are not this requested map's results.

The requested directory now keeps the original Tk driver layout, hold-WASD/release-stop,
nominal PD60/2/crank0.5, original closed robot/reset poses, and no yaw/upright assist.
New drive_rm7v7_moe.py runs the complete supplied RMUC2026_V2.0.0.stp ground assembly,
29x16m, both original1.5degree floor halves, island, ramps, waves, tunnels and trenches.
The existing source conversion omits separate base/outpost/rune/dart machinery; this
is clearly stated, not claimed to be a complete mechanical assembly or shooting sim.

START_WASD.bat and START_RM7V7_MOE.bat open this driver. P starts/pauses, hold WASD
drives, J requests0.8s jump after initial100normal controls, K selects recovery,
Z/B selects+/-4spin, N/X returns normal, R resets, F/dropdown chooses15CAD starts,
M switches complete map overview and robot-follow. Initial state is paused. The actual
player was launched and wrote its own STARTED/CURRENT with fourth-hour ONNX name.
Original model30900 and driver are kept via START_OLD_30900.bat; original reports and
BUILD_RECEIPT remain unchanged. The intermediate original-road-only new driver was
prepared/tested but not launched; it is superseded by the user clarified full-map entry.

Latest complete sources were updated again after the fourth training hour naturally
closed: H1 a7711e6d / Adam655360 /74updates, E2 d42e497b /Adam686020 /240updates,
E3 d4c8067d /Adam665300 /94updates. Whole final model CPU/out/cost once is in F.
Original learned gate148 E0/W35 is retained; jump/recovery/spin are explicit manual
whole-action dispatch. This is not a new learned five-way gate or weight/action blend.
The newly exported graph uses35input,6output, clipped-output parity6.6757202e-6,
source weights/pathsizeSHA in adjacent JSON. No remote model or physics changed.

Geometry was converted as original convex solids or convex planar patches / individual
20um-halfthickness contact prisms, not a giant hull or heightfield filling underpasses.
The original robot's complete XML body/actuator/constraints remain unchanged. Actual
MuJoCo compile:47600geoms/47566meshes/37q/36v/6actuator/10equalities. Initial tiny-mesh
volume rejection was retained; using shell inertia for static world skins fixes only
the compiler's static mesh mass convention, with contact geometry unchanged. Initial
relative path mismatch was fixed before compile and original XML preserved. Full source
CAD3770rays initially all returned-1 because mj_ray skips fully transparent collider
geoms; that false and trace remain. V2 temporarily changes only ray-query visibility
alpha, restores it, and passes all3770 at original source tolerances, max0.000764699m.
No production query/geometry threshold was changed. Local flat/jump/wave/tunnel smoke
remained finite with actual closure/mimic values saved. Jumping still has substantial
pitch/translation and is not a qualified takeoff/landing/recovery skill.

Additional inspection errors: incorrect preparer filename lookup (no action), one
PowerShell embedded Python quoting SyntaxError (before Python work), and searches of
nonexistent refs/environment aliases or denied unrelated unpack folder. These are
local lookups, not GPU faults. All source, error reports and unexecuted helpers remain.

The user then reported jumping was poor and requested checking Fudan released jump
models and SCUT jump rewards, clarifying repositories are already downloaded. The
existing local Fudan deployment ONNX was found under audits/20260925/fudan_rl_deploy/
pseudocode/example/onnx/jump/jump_pos0.2_0.4_p6.0_d0.5_0.2.onnx,157656B,
SHA54c9972506a38e94a6b5de30e79ad689a7b9fd92e72640874eee1bdb4c36dc78.
ONNX checker passes:obs[batch,25] +obs_history[batch,125] ->actions[batch,6]. It was
not inferred on MOD4 or installed as our policy. Fudan jump reward code/config and
deployment PD/midpositions were inspected; SCUT jump_takeoff.py/airborne.py/V14cfg
contain actual push/release/height/tuck/airtime/landing/wheel-speed/impact terms. Definitions
and active weights are distinguished: multiple candidates are disabled/commented, and
the jump state machine also contains assist-force/terrain filters that are not authorized
MOD4 features. Local source snapshots and exact paths/SHAs are indexed. Upstream GitHub
README/code pages were checked but no all-repositoryHEAD or upstream binary byteexact
claim is made. Web API tree opens failed; local source was used, not absence inferred.

Three real remote PPO jobs continue independently on their fifth hourly block from
the just-closed fourth-hour sources (G owner185836; metadata all3GO/positiveupdates/
matchingGPU true). No actorSTD/LR/reward/CAD/guard/budget was changed for the research
or local player. Factual new cost10939.876977205276seconds was settled once by original
writer174112; snapshot449529.1767463684 is not another debit or refund. G hourly saving,
original accounting and future helpers bound185836 are unchanged, no native replay.
Existingmod4-10 remainsACTIVE/hourly/same target, V21 app update and saved TOML verified.
Do not automatically reopen or interrupt the human's local player on heartbeats.

Preserve G unique stage1aeaf945/tag34c44a48(total1384tags) and all prior consumed
helpers/stages. This correction/research is a new unique stage. Capture all saved
current texts; large meshes, models, compiledMJB andPNG use actual externalpathsizeSHA
with originals retained. Running player's liveCURRENT is a snapshot, not a new formal
behavior result on every repaint. No future report is claimed already archived.
