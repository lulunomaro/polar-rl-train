# Probe64 r1: startup name mismatch

Isaac body names use the existing FullDR base_id contract; literal MuJoCo chassis lookup was invalid. Failed before physical stepping or PPO. Exact failed source and prepared input hashes preserved in ../probe64_r1_source/. Corrected only lookup to env.full_dr.base_id; no asset change. Probe rerun is new job probe64_rearward_r2.
