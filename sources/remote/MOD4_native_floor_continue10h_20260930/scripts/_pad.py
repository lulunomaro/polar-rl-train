import io,ast
p=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/mdp/rewards.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("  return (found > 0).float().mean(dim=1)","  return (found > 0).float().reshape(found.shape[0], -1).mean(dim=1, keepdim=True)")
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("wheel_contact_fraction -> [B,1]")
