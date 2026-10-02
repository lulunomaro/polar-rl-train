import glob, os, shutil
cks = sorted(glob.glob(r"D:/claude2/fangzhen/train/logs/rsl_rl/rm_cc_v11/2026-09-05_*/model_*.pt"),
             key=os.path.getmtime)
src = cks[-1]
dst = r"D:/claude2/fangzhen/train/logs/rsl_rl/rm_cc_v12/seed_from_v11"
os.makedirs(dst, exist_ok=True)
shutil.copy2(src, os.path.join(dst, os.path.basename(src)))
print("seeded v12 from", src, "->", dst)