"""Render the nominal MuJoCo trajectory with NVIDIA EGL using system ABI."""
import os
os.environ['MUJOCO_GL']='egl';os.environ['PYOPENGL_PLATFORM']='egl'
from pathlib import Path
import importlib.machinery,importlib.util,sys
ROOT=Path('/home/lc01/Zonglin Li/zonglin2')
# driver libraries use the system C ABI; render only after model dynamics is saved.
print({'libGLVND':list(Path('/usr/share/glvnd/egl_vendor.d').glob('*.json'))},flush=True)
