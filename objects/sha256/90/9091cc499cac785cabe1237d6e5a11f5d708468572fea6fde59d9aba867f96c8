import io,glob
for p in glob.glob(r"D:/claude2/fangzhen/sim2sim/wsl/*.py")+glob.glob(r"D:/claude2/fangzhen/sim2sim/wsl/*.sh")+glob.glob(r"D:/claude2/fangzhen/sim2real/*.py"):
    t=io.open(p,encoding="utf-8").read(); io.open(p,"w",encoding="utf-8",newline="\n").write(t.replace("\r\n","\n"))
print("normalized")
