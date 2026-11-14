"""Open the verified map player with the project's existing Python runtime."""
from pathlib import Path
import subprocess
import time

task = Path(r"D:\claude2\fangzhen\_mod4v2_src_20261106\sources\local\MOD4V3_FORWARD_JUMP_MANUAL_20261114")
runtime = task / "runtime" / time.strftime("manual_%Y%m%d_%H%M%S")
runtime.mkdir(parents=True, exist_ok=True)
with (runtime/"stdout.log").open("w") as stdout, (runtime/"stderr.log").open("w") as stderr:
    subprocess.Popen([r"D:\claude2\fangzhen\.venv\Scripts\pythonw.exe", "-X", "utf8", "-B", "-u",
                      str(task/"manual_jump.py"), "--output", str(runtime)],
                     cwd=task, stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
