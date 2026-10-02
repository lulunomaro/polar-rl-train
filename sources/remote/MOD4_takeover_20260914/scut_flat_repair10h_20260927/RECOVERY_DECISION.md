# Recovery at 2026-09-27 18:27 CST

The host shut down at 12:19:29 CST after 1800 seconds of the first 10-hour segment. Status was stale at reboot and no PPO process remained. Last complete model_1470.pt was preserved. The 15-second nominal 64-environment audit on model_1470 had 43/64 survivors, 0/64 strict passes, vx 0.543 m/s, tilt RMS 11.53 deg, powered-wheel contact 0.710, guide load 28.3 N, action delta/delta2 0.114/0.175, closure 0.254 mm, mimic 0.00183 rad. No sustained effort saturation.

For the remaining 34200 seconds, only flat reward coefficients change: run tilt -8 -> -12, powered-wheel contact +2 -> +3, guide load -4 -> -5. This targets the measured failure while retaining 0.30-1.20 m/s commands, 500 N reference spring, detailed USD, action mapping, solver 16/4, 12000 env x 48 steps, and the same PPO architecture. Resume exactly from model_1470; old run, status, and checkpoints remain untouched.
