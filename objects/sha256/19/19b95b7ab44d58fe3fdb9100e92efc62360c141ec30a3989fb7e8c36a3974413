import io,ast
p=r"D:/claude2/fangzhen/sim_mujoco/sim_baseline.py"
t=io.open(p,encoding="utf-8").read()
t=t.replace("rend = mujoco.Renderer(m, 460, 820)","rend = mujoco.Renderer(m, 480, 832)")
t=t.replace("""    imageio.mimsave(vid, frames, fps=int(round(1.0 / (m.opt.timestep * 12))),
                    codec="libx264", quality=8)""",
"""    fps = int(round(1.0 / (m.opt.timestep * 12)))
    w = imageio.get_writer(vid, fps=fps, codec="libx264", pixelformat="yuv420p",
                           macro_block_size=1, ffmpeg_params=["-movflags", "+faststart"])
    for f in frames:
        w.append_data(f)
    w.close()
    for fr, tag in ((0.06, "a"), (0.30, "b"), (0.55, "c"), (0.85, "d")):
        imageio.imwrite(vid.replace(".mp4", "_%s.png" % tag), frames[int(fr * len(frames))])""")
io.open(p,"w",encoding="utf-8").write(t); ast.parse(t); print("ok")
