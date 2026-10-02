import io
p = r"D:/claude2/fangzhen/sim2sim/wsl/jump_channel_test.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("                     b[2] if len(b) > 2 else float(\"nan\"),",
              "                     b[0] if len(b) > 0 else float(\"nan\"),")
s = s.replace("""    if int(t * 20) != (int((t - 0.05) * 20) if t > 0.05 else -1):""",
              """    if t >= next_sample:
        next_sample += 0.05""")
s = s.replace("rows = []\nt0 = time.time()", "rows = []\nt0 = time.time()\nnext_sample = 0.0")
s = s.replace("""armed = [r for r in rows if r[2] > 0.5]
base_z = min(r[3] for r in rows if r[1] == 0.0 and r[2] == 0.0)""",
"""rows = [r for r in rows if r[1] == r[1] and r[3] == r[3]]   # drop NaN samples
armed = [r for r in rows if r[2] > 0.5]
base_z = min(r[3] for r in rows if r[2] == 0.0)""")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("jump_channel_test.py: z slot, sampling and NaN handling fixed")