import io, ast
p = r"D:/claude2/fangzhen/sim2real/mock_h7.py"
t = io.open(p, encoding="utf-8").read()
t = t.replace('ap.add_argument("--verbose", action="store_true")',
              'ap.add_argument("--verbose", action="store_true")\n'
              'ap.add_argument("--video", default="", help="write an mp4 of the plant")\n'
              'ap.add_argument("--vwidth", type=int, default=640)\n'
              'ap.add_argument("--vheight", type=int, default=360)')
t = t.replace("""os.set_blocking(master, False)""",
"""renderer = None
frames = []
if args.video:
    try:
        renderer = mujoco.Renderer(m, args.vheight, args.vwidth)
        vopt = mujoco.MjvOption()
        vopt.geomgroup[:] = (1, 1, 1, 1, 1, 1)
        vcam = mujoco.MjvCamera()
        vcam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
        vcam.trackbodyid = BASE
        vcam.distance, vcam.azimuth, vcam.elevation = 1.9, 95.0, -9.0
        print("[h7] plant video enabled", flush=True)
    except Exception as exc:
        print("[h7] video unavailable:", exc, flush=True)
        renderer = None

os.set_blocking(master, False)""")
t = t.replace("""        next_t += period
        sleep = next_t - time.monotonic()""",
"""        if renderer is not None and k % 20 == 0:
            vcam.lookat = [d.qpos[0], 0.0, 0.22]
            renderer.update_scene(d, camera=vcam, scene_option=vopt)
            frames.append(renderer.render().copy())
        k += 1
        next_t += period
        sleep = next_t - time.monotonic()""")
t = t.replace("period = 1.0 / args.period if False else 1.0 / args.rate", "")
t = t.replace("period = 1.0 / args.rate", "period = 1.0 / args.rate\nk = 0")
t = t.replace("""finally:
    print("[h7] stats:", stats)""",
"""finally:
    print("[h7] stats:", stats, flush=True)
    if renderer is not None and frames:
        try:
            import imageio.v2 as imageio
            w = imageio.get_writer(args.video, fps=50, codec="libx264",
                                   pixelformat="yuv420p", macro_block_size=1,
                                   ffmpeg_params=["-movflags", "+faststart"])
            for fr in frames:
                w.append_data(fr)
            w.close()
            print("[h7] wrote", args.video, len(frames), "frames", flush=True)
        except Exception as exc:
            print("[h7] video write failed:", exc, flush=True)""")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
ast.parse(t); print("video support added to the firmware simulator")
