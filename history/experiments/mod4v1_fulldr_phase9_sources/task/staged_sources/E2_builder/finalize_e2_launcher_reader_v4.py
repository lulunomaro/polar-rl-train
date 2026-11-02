"""Bind the actual E2 Zonglin2 launcher import, preserving original boot flags."""
from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent
s=(HERE/'build_e2_mod4v1_sources_v3.py').read_text(encoding='utf-8')
a="trainer=replace(trainer0,'from isaaclab.app import AppLauncher', 'from launcher_mod4v1_e2 import IsolatedAppLauncher208 as AppLauncher')"
b="trainer=replace(trainer0,'from zonglin2_app_launcher import Zonglin2AppLauncher as AppLauncher', 'from launcher_mod4v1_e2 import IsolatedAppLauncher208 as AppLauncher')"
assert a in s;s=s.replace(a,b)
a="base_files=[r for k,r in rows.items() if k.startswith('runtime/') and Path(k).suffix.lower() not in ('.pt','.pth')]"
b="base_files=[r for k,r in rows.items() if (k.startswith('runtime/') or k.startswith('lib/')) and Path(k).suffix.lower() not in ('.pt','.pth')]"
assert a in s;s=s.replace(a,b)
a="prior,prior_ref=read(HERE/'build_e2_mod4v1_sources_v2.py');reader,reader_ref=read(HERE/'finalize_e2_manifest_reader_v3.py');refs.extend([prior_ref,reader_ref])"
b=a+"\n    launcher_row=rows['lib/zonglin2_app_launcher.py'];original_launcher,original_launcher_ref=read(Path(launcher_row['local_path']),launcher_row['SHA']);refs.append(original_launcher_ref)\n    previous,previous_ref=read(HERE/'build_e2_mod4v1_sources_v3.py');last_correction,last_correction_ref=read(HERE/'finalize_e2_launcher_reader_v4.py');refs.extend([previous_ref,last_correction_ref])"
assert a in s;s=s.replace(a,b)
ast.parse(s)
new=HERE/'build_e2_mod4v1_sources_v4.py'
with new.open('x',encoding='utf-8') as f:f.write(s)
print(json.dumps({'generator':str(new),'PT_or_SDK_or_training':False},indent=2))
