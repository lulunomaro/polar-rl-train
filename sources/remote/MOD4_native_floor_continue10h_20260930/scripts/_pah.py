import io,ast
p=r"D:/claude2/fangzhen/train/rmvehicle/src/rmvehicle/mdp/rewards.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("  return ((asset.data.joint_vel[:, ids[0]] - asset.data.joint_vel[:, ids[1]]) ** 2).mean()","  return (asset.data.joint_vel[:, ids[0]] - asset.data.joint_vel[:, ids[1]]) ** 2")
t=t.replace("  return ((q[:, 0] - q[:, 2]) ** 2 + (q[:, 1] - q[:, 3]) ** 2).mean()","  return (q[:, 0] - q[:, 2]) ** 2 + (q[:, 1] - q[:, 3]) ** 2")
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("per-env reward shapes fixed")
