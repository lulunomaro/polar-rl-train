# V6 actual independent standing200 evaluation and route diagnosis

The completed V6 RL+BPTT final checkpoint is239074513B/SHA `d12e17e7f47fbbaf27ce22d5c15105a005fb312a5f60841e3e7dc7b04a0056e9`,1019 verified BPTT policy steps,4476 WM/aux steps,4076 critic steps,2861 physical controls and1464832 environment transitions. Original fullsave,child waits,cost settlement and lease release remain unchanged.

The original owner immediately ran frozen evaluation after training close. Actual evaluation completed on November3,2026 at02:10:58 +08,waited at02:10:59,and released by02:10:59.965. Earlier local heartbeat reports accurately marked results not yet retrieved while another controller occupied the serial channel; they did not claim the evaluation had not run. The single finite evidence transfer finally executed at04:27 +08 after fresh local release,obtaining24 evidence/replay files and verifying all four NPZs against published source SHA. It opened no policy/PT and ran no SDK or physics. The consumed transfer must not be repeated.

## Measured outcome

Independent80 first episodes,500 controls/10s,seed9137,fresh original full DR,fixed edge.8m and height.2m: **0/80 strict successes**. All80 reached10s timeout,none physically terminated. Across the500 recorded control endpoints,both-wheel top support case count and stable support ticks are identically zero. Every episode's final top forces are zero. This is a valid execution that failed the skill test,not a startup rejection.

Four saved real pose sequences are env0,1,40,41. Their final chassis x is.512–.541m; authored wheel front bounds never reach.8m in those four samples. Each wheel's maximum bottom height is.00118–.02322m; the lower of both wheel bottoms peaks only.00010–.00048m. Chassis height stays.233–.280m,with roll/pitch up to24.3/19.3deg and yaw drifting as far as−54.65deg. Selected3608 wheel manifold rows are ground-level; highest saved point z is.00000418m. These selected observations are not asserted to represent individual geometry of all80.

Initial current-depth output correctly detects.2000002–.2000004m in allfour. Height-assist detection begins around1.98–2.12s; depth later becomes invalid in substantial portions of three cases. This is not evidence of initial blindness. The actual policies approach the riser,remain on the lower ground,and progressively turn; they do not coordinate lift and wheel ascent.

All2000 selected control actions have left-crank channel exactly−6. The other channels vary. This is a strong concrete diagnostic lead,but the recorded actor output does not separate frozen base,residual latent,sum before clip or actual processed motor target. Its origin and sole causal role are not yet established. Current reward curves penalize increasing yaw; no claim that reward explicitly pays for a wrong route. Surviving10s is not skill success.

## Native replay and curves

`render_standing_recorded_v1.py` rejected guide_roller_00 before images because guide rollers are actual authored USD Cylinder shapes,not visual Mesh objects. Original source and failed output are preserved. V2 only adds tessellation from each actual cylinder's radius,height,axis and original relative transform. It retains exact new MOD4v1 USD visuals and uses actual saved body positions/quaternions through a display-only MuJoCo model with0DOF. No neural read,inference or simulation step. The finite renderer generated eight side/top contact sheets and one500-frame four-case half-speed MP4. Current model used native `view_image` on all eight sheets and both plotted curve images. The visible pattern matches measured lower-ground motion and increasing yaw.

`analyze_saved_standing_v6.py` produced CSV and route/yaw/chassis/wheel-bottom/action/depth curves plus all80 reward/top-support curves from actual packets. Full analysis and precise values are indexed. Rendering and diagrams never determine contact acceptance; actual filtered PhysX solver data does.

## Decision and next action

Do **not** run unchanged V6 training again or replay completed evaluation/transfer. A targeted read-only CPU action decomposition is prepared as `diagnose_final_action_cpu_v7.py`,currently **unused**. It will decode the final once onCPU,retain the complete source tensor root,construct frozen actor copies from the embedded final teacher/residual,and analyze exact saved real replay inputs. It will compare base,residual,preclip sum,action gradients,action-range reachability and normal-mode input counterfactual. This is necessary diagnosis of a measured constant saturation,not an archival model read. No source mother PT,optimizer,GPU,SDK,new rollout or budget write.

At this record,other H1 wheel-height postround PID60788/create2026-11-03T04:27:49.079354+08 remains a known local controller. Its process/task is not changed; no second SSH or watcher is started. After actual local release,do the finite CPU diagnosis and use its evidence to repair policy integration or select reasonable continuation. Do not guess which component caused saturation. No standing200 training is currently live.

All sources,reports,raw failed render,consumed transfer receipts,replay metadata,actual80 results and next decision are mapped in `INDEX.json`. SameSHA text references existing Git paths; new text uses content-addressed objects. PT/NPZ/USD/video/images/intermediate frames are path/bytes and available published-SHA indices only. Actual new physics/model source was not read for archive. Parent270mm work and automation unchanged. The original V6 trial object/peel `f7065b545f200083a09163401261243e1d8f3b5f`/`90dd98299a278f221e14785185eb114e5c8415b1` remain protected; this is a new evaluation/diagnosis phase.
