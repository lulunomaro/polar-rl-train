import io
F=r"D:\claude2\fangzhen\scripts\x_stand_probe2.py"
s=io.open(F,encoding="utf-8").read()
s=s.replace("    UP=np.array([0.,0.,-1.]); last=np.zeros(6,np.float32); tgt={n:0.0 for n in ACT_J}",
            "    UP=np.array([0.,0.,-1.]); last=np.zeros(6,np.float32)\n    tgt={n:0.0 for n in ACT_J}\n    def _noop():\n        pass")
s=s.replace("        global last\n","        nonlocal last\n")
io.open(F,"w",encoding="utf-8").write(s)
print("fixed")