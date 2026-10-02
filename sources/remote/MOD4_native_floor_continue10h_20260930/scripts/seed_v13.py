import os, shutil
R = r"D:/claude2/fangzhen"
src = os.path.join(R, "train/logs/rsl_rl/rm_cc_v12/2026-09-05_10-10-37/model_8696.pt")
dst = os.path.join(R, "train/logs/rsl_rl/rm_cc_v13/seed_from_v12")
os.makedirs(dst, exist_ok=True)
shutil.copy2(src, os.path.join(dst, "model_8696.pt"))
print("seeded v13 from v12 model_8696.pt ->", dst)