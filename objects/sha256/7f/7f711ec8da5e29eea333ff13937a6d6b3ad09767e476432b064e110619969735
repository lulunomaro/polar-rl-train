import os, shutil, time, sys
T = r"C:/Users/lulunomaro/AppData/Local/Temp"
assert os.path.isdir(T)
targets = ["gltf_export", "wsl-crashes"]
def dsize(p):
    tot = 0
    for r, ds, fs in os.walk(p):
        for f in fs:
            try: tot += os.path.getsize(os.path.join(r, f))
            except OSError: pass
    return tot
for name in targets:
    p = os.path.join(T, name)
    real = os.path.realpath(p)
    if not real.startswith(os.path.realpath(T) + os.sep):
        print("SKIP (outside temp):", real); continue
    if not os.path.isdir(p):
        print("absent:", name); continue
    print("removing %s  (%.2f GB)" % (real, dsize(p) / 1e9), flush=True)
    shutil.rmtree(p, ignore_errors=True)
    print("  still exists:", os.path.exists(p))
free = shutil.disk_usage("C:/")[2] / 1e9
print("C: free now %.2f GB" % free)
