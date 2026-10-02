import io
F=r"D:\claude2\fangzhen\scripts\export_sim2sim_cc.py"
s=io.open(F,encoding="utf-8").read()
anchor = "# ------------------------------------------------------------------ 2. MJCF edits"
add = ('''# ------------------------------------------------------------------ 2. MJCF edits
# Physics rate.  Training uses timestep=0.002 with decimation=10, i.e. each policy torque is
# held across ten 2 ms substeps.  The bridge runs its control loop at 500 Hz, so a 2 ms plant
# step makes one control tick == one physics step and the new 50 Hz leg-torque ZOH reproduce
# the training regime exactly.  (1 ms here would decouple the two rates.)
xml = re.sub(r"(<option [^>]*?timestep=\\")[0-9.]+(\\")", r"\\g<1>0.002\\g<2>", xml, count=1)
print("deployment physics timestep -> 0.002 s (matches training dt x decimation)")

''')
assert s.count(anchor)==1
io.open(F,"w",encoding="utf-8").write(s.replace(anchor, add.rstrip("\n")))
print("dt patch OK")