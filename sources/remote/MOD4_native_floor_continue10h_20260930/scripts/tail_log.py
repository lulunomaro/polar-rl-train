import io, re, sys
path = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 2200
pat = r"V1\d_START|V1\d_EXIT|Number of environments|Learning iteration|Steps per second|Mean reward|Iteration time|ETA|Error|Trace|out of memory|jump_progress|track_lin_vel|track_ang_vel|terrain_levels"
d = io.open(path, "rb").read()[-n:].decode("utf-8", "replace")
for l in d.splitlines():
    if re.search(pat, l):
        print(l.rstrip()[:104])