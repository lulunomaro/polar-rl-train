# Autonomous Stair Jump PPO Launch

The user requested setup and training of a policy that discovers how to jump onto stairs. This is a new finite7200-second window, retaining the preceding two-hour duration. No completed training window is replayed.

- Original window start: 2026-11-14T22:36:38.623455+08:00.
- Current valid segment start: 2026-11-14T22:46:58.990453+08:00.
- Absolute deadline: 2026-11-15T00:36:38.623455+08:00; no automatic extension.
- Remote root: `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_AUTONOMOUS_STAIR_JUMP_2H_20261114_R1`.
- Frozen source: `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_AUTONOMOUS_STAIR_JUMP_2H_20261114_R1/revision_r2`; archive SHA256 `b4ce0826c2df27a98c42978ff9c78837d2ec3a86666295b1152f209d7bbbc50c`.
- Training GPU0:2048 parallel environments, one PPO optimizer owner. GPU1 performs independent deterministic256-environment evaluations of completed checkpoints when free.
- Parent: stable85-minute forward-jump repair checkpoint, SHA256 `c4d0328472e8642c497f113e37fb8940d92435cd8d96f547b8f1f4aa15cc1dfe`.
- Full parent actor/critic/STD/Adam was restored before explicit adaptation: actor input columns31:35 and critic32:39 plus matching Adam moments cleared; critic output reset for the new reward; leg exploration STD floored at0.30. Other inherited state is retained. Same dimensions do not imply old input compatibility.
- Interface35/78/6; new observation schema `MOD4V3_AUTONOMOUS_STAIR_OBS_V1`. The last seven actor inputs contain base mode, latched jump request, measured airborne state, signed target-edge distance, step height, tread depth and scaled vertical velocity. Terrain targets are found from a forward ray scan and locked at request time; no phase clock or leg pose target is given.
- All six executed actions come from PPO. No teacher action, force impulse, pose sequence, or extra actuator is executed.
- Geometry: saved Isaac Lab tile r00_c00(16.5cm) and r03_c00(22cm), unscaled at their target levels. Explicit4/8/12cm warmup copies share the original XY geometry.20% target-height exposure starts immediately; the remaining curriculum expands at15/30/60minutes.
- Acceptance requires a real qualified flight before the edge, both wheels crossing in that flight, both wheel footprints on the upper tread, then at least0.5s stable recovery. Single-wheel contact, climbing, vertical height alone, and landing after a failed episode do not pass.
- Original MOD4v3 HW300N60 R3 plant, motor envelopes,2.5ms TGS32/4, leg100Hz/wheel400Hz/policy50Hz, closure10mm and mimic0.01rad per-episode resets retained. FullDR ranges retained,20% nominal mixture.
- Existing manual player and one-tile map are unchanged. A new-schema actor requires the matching new producer before player selection; WASD and one-shot Space remain the interaction contract.

## Verification

The objective check rejected all31 previously failed MuJoCo stair trajectories and checked rolling, partial contact, short holds, failure flags, scan decoding and a synthetic positive sequence. Synthetic checks do not claim physical success.

Native admission `admit_r2` passed with2048 complete episodes and zero optimizer updates, including actual terrain-height decoding, interface, motor envelope, timing, asset identity and physics-console checks. Native failures, if any, are retained beside the successful revision.

Actual first PPO update: actor=True, critic=True, STD=True, Adam=True. Latest collected valid update count:13, original window consumed:752.0s, current valid segment elapsed:131.6s.

The matching MuJoCo producer in `mujoco_player.py` was tested with the first valid new-schema checkpoint on one original16.5cm tile. Actual forward speed at request:0.636m/s. One request was accepted, a duplicate was rejected, all405 following frames retained one total request, and ray-decoded task inputs had the correct schema and height. This integration check claims task success only if the same measured outcome accepts it; actual flag:False. The existing user launcher is not switched to an unqualified early policy.

## Retained Invalid Segment

Original segment `train7200` reported a PhysX found/lost aggregate-pair capacity overflow(needs60887986), so its physics and weights are rejected. Its reports, full checkpoints and original source are retained. Only its own supervisor was stopped, and its optimizer closed after a REQUEST_STOP and complete state save.

Revision2 distributes training over8 terrain columns and9 approach lanes per tile, checks PhysX errors explicitly, and repeats native admission at the actual2048-environment training scale. Contact/footprint geometry uses each tile's coordinates. The player remains one visible tile. The valid segment returns to the original stable parent; rejected weights are not reused.

The original start/deadline remain 2026-11-14T22:36:38.623455+08:00 / 2026-11-15T00:36:38.623455+08:00. Failed runtime and repair/admission time count against that same7200-second window. No replacement two-hour window is granted.

Training is in progress. No target stair-jump success rate is claimed at launch. Checkpoints are atomically saved every300seconds; final complete PPO state is saved at the original deadline. The evaluator never extends or restarts training. Reports created after this collection remain pending the next Git append.
