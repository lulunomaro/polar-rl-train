import io
p = r"D:/claude2/fangzhen/sim2real/mock_h7.py"
t = io.open(p, encoding="utf-8").read()
a = """        if args.verbose and int((now - t_start) * 2) != int((now - period - t_start) * 2):"""
b = """        if (now - last_report) > 2.0:
            last_report = now
            print("[h7] t=%5.1f z=%+.4f pitch=%+.2fdeg wheel vel=%+.2f/%+.2f "
                  "rx=%d bad=%d tx=%d"
                  % (now - t_start, d.qpos[2],
                     math.degrees(math.asin(np.clip(grav[0], -1, 1))),
                     d.qvel[VADR[4]], d.qvel[VADR[5]],
                     stats["rx"], stats["rx_bad"], stats["tx"]), flush=True)
        if args.verbose and int((now - t_start) * 2) != int((now - period - t_start) * 2):"""
assert a in t
t = t.replace(a, b)
t = t.replace("last_rx_t = time.monotonic()", "last_rx_t = time.monotonic()\nlast_report = 0.0")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
import ast; ast.parse(t); print("mock now reports every 2 s")

p2 = r"D:/claude2/fangzhen/sim2real/run_sim2real.sh"
t2 = io.open(p2, encoding="utf-8").read()
t2 = t2.replace("""timeout $((DUR + 25)) ros2 launch template_middleware template_bring_up.launch.py \\
  backend:=real prefix:=rm_vehicle real_serial_port:=/dev/wheelbipe_h7 \\
  use_dt7:=true auto_enter_rl:=false controller_params:=$PARAMS \\
  > "$LOG" 2>&1
echo "LAUNCH_EXIT=$?"
kill $MOCK 2>/dev/null""",
"""timeout $((DUR + 25)) ros2 launch template_middleware template_bring_up.launch.py \\
  backend:=real prefix:=rm_vehicle real_serial_port:=/dev/wheelbipe_h7 \\
  use_dt7:=true auto_enter_rl:=false controller_params:=$PARAMS \\
  > "$LOG" 2>&1 &
LJ=$!
sleep 9
python3 -u /mnt/d/claude2/fangzhen/sim2real/telem.py 2>&1 | tail -32
wait $LJ
echo "LAUNCH_EXIT=$?"
kill $MOCK 2>/dev/null""")
io.open(p2, "w", encoding="utf-8", newline="\n").write(t2)
print("run script now samples telemetry")
