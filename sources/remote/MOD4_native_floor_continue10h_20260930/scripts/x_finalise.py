import io
# 1) harness: do not use the training solver regime by default (it explodes on CPU MuJoCo)
F=r"D:\claude2\fangzhen\scripts\hop_control_law.py"
s=io.open(F,encoding="utf-8").read()
a='if os.environ.get("RM_HARNESS_TRAIN_SOLVER", "1") == "1":'
b='if os.environ.get("RM_HARNESS_TRAIN_SOLVER", "0") == "1":   # explodes on CPU MuJoCo'
assert s.count(a)==1
io.open(F,"w",encoding="utf-8").write(s.replace(a,b))
print("harness solver default -> off")