import io,os
p=r"D:/claude2/fangzhen/sim2sim/wsl/build_ws.sh"
t=io.open(p,encoding="utf-8").read()
t=t.replace('cd /root/ws/sim2sim\n','cd /root/ws/sim2sim\n[ -d wheelbipe_ros2_sim2sim-main ] && rm -rf wheelbipe_ros2_sim2sim-main && echo "removed nested duplicate copy"\n')
io.open(p,"w",encoding="utf-8",newline="\n").write(t); print("ok")
