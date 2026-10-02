"""Report which optional sim2sim dependencies are importable in the current python."""
for name in ("mujoco", "numpy", "onnxruntime", "torch", "tensorboard"):
    try:
        mod = __import__(name)
        print("%-14s OK   %s" % (name, getattr(mod, "__version__", "?")))
    except Exception as exc:  # noqa: BLE001
        print("%-14s MISS %s" % (name, type(exc).__name__))
