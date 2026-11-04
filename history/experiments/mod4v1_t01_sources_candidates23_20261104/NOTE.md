# T01: source reuse, C2 functional improvements and C3 negative result

This records two completed new 12s cases, 1200 controls/24000 physics each, with a fresh model/DR per case. Original gates, robot, KF and actuator PD/D4/DC are unchanged. No holdout or consumed case was rerun.

C2 retained C1 leg leveling and reused the existing FPS heading outer loop (3/s, +/-1.5rad/s). Its pitch/roll peaks are .0187347/.0280186rad, progress1.623630m, lateral.0468113m, steady-speed RMSE.0412814m/s and stop RMS.00554225m/s: every non-contact gate passed. Left/right support.89855/.95515 and 165 below-threshold whole-body force samples still failed. Guide/hard0. Parent collected pwsh-2ce069f872794049 exit0.

C3 directly used the supplied SPR/7z axial length D-on-measurement/J-transpose structure, retaining C2 and own nominal geometry/gains. Added128.1673466Ns/m was derived from own design mass/stiffness; no foreign gains/dimensions copied, no added length P/I. It completed but support.89385/.95210 and177 whole-low-force samples did not improve. Stop RMS.0105791; other non-contact gates passed. C3 is preserved but NOT adopted; C2 remains the best functional candidate. Parent collected pwsh-d441096df6a245f8 exit0. T01 remains incomplete; no fourth parameter grid, no DR expansion, no UI graduation.

Completed C1 stop and C2 contact reductions are included. Each new C2 raw source was streamed once (1200/20000/1200); a nested diagnostic-clock parser gap prevented its optional correspondence analysis, which was explicitly stopped without reread. 0.5-1ms low-force samples are not proof of geometric flight; 2k actual-velocity/DC clip duty remains unknown. The source-reuse inventory is in the canonical 36-task file, not a parallel plan. Source function snapshots used for that inventory are included.

Large control/contact/diagnostic logs are path/size indexed only, SHA unknown, never re-read or hashed for this archive. Old PH12 pending remains pending. Existing recorder is unchanged and called once; known sparse-add adaptation is in memory only. No other worktree/main ref, physics, native build or hardware is touched by archival.
