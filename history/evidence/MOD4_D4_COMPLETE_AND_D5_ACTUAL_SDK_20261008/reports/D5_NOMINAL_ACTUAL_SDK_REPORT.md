# D5 nominal spring SDK readback completed; pressure training is not deployed

The existing3060 worker completed10 environments/300 control steps/3s from the full behavior-reviewed D4 model28633.1200 physical writes and1200 contact callbacks matched. Installed PhysX stiffness/damping/effort limit/armature and buffered properties read3500N/m,3Ns/m,2000N,.002 and remained exact initially/finally. Existing float32 preload target is.220639437m; neutral initial/reset writes are recorded separately.

The independent q/qd/target formula agrees with the installed SDK approximate computed/clipped effort within8.62791203e-05N (SDK's own float32 formula error0). Actual active-preload sampled elastic estimate range is723.300842–857.885986N. These are software estimates at observed joint states, not separate PhysX drive force, constraint reaction, physical gas stroke or measured hardware force. No nominal parameter was changed to meet300–700N.

Task resets0/nonfinitefalse, maximum closure0.546933mm and mimic0.001691456rad. D1–D4 actor/clean critic/command/last action/readback and both1200 action group callbacks passed; selected sensor reset and other rows/global clock were preserved. Original skill flags remain;10env3s is an interface check. Processwall86.280s;2s sampled memory2854MiB is not a continuous peak. Two returned JSON files were byte-SHA verified.

The first ±10% independent spring-stiffness pressure component passed10 target Torch2.10 CPU contracts without CUDA initialization, physical writes or PPO. Actual pressure setter/CUDA lifecycle/full learning resume/native20k/newscope PPO and the next unique controller are still required. Hardware force-stroke calibration is absent. Current243-source4090 D4 training and the worker are unchanged.
