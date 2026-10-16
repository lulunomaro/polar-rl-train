"""Keep original evaluator guard; classify one actually signed desktop GPU child."""
from pathlib import Path
import sys,json
E=Path(__file__).resolve().parent;D=E.parent;W=D.parent;sys.path.insert(0,str(W/'MOD4_3060_BODYFRAME_FIRST_FULL80_20261014'));import transport_249_bodyframe_current_terminal_role_v3 as base
PY=base.PY;ROOT='D:/MOD4_async_eval/'+D.name+'/curb140_cont147_frozen35_3060_v1';connect=base.connect;close=base.close;py=base.py;ps=base.ps
def known_identity():
 v=json.loads((D/'reports/ACTUAL_3060_DEEPSEEK_ELECTRON_GPU_ROLE_IDENTITY_READONLY.json').read_bytes());assert v['authenticode']['Status']=='Valid' and v['actual_Electron_GPU_child_of_same_desktop_main'] and v['no_Python_Kit_or_training_child'];return dict(process=v['GPU_process'],parent=v['parent'],binary_SHA=v['binary_SHA'])
def exact_desktop(actual,expected):
 return actual==expected and '--type=gpu-process' in actual['process']['argv'] and not any(x.startswith('--type=') for x in actual['parent']['argv'])
def guard_code():
 base.ROOT=ROOT;s=base.guard_code();marker="  elif name not in allowed_names:unknown.append(dict(pid=pid,exe=exe))";assert s.count(marker)==1;known=known_identity();extra="""  elif name=='deepseek harness.exe':
   import hashlib
   parent=process.parent();assert parent is not None
   actual=dict(process=dict(pid=process.pid,creation=process.create_time(),argv=process.cmdline(),exe=process.exe(),parent=process.ppid()),parent=dict(pid=parent.pid,creation=parent.create_time(),argv=parent.cmdline(),exe=parent.exe(),parent=parent.ppid()),binary_SHA=hashlib.sha256(Path(exe).read_bytes()).hexdigest())
   expected=EXPECTED_DESKTOP
   assert actual==expected and '--type=gpu-process' in actual['process']['argv'] and not any(x.startswith('--type=') for x in actual['parent']['argv']), 'Desktop identity changed: unknown, no wildcard permission'
   desktop.append(dict(pid=pid,creation=process.create_time(),exe=exe,role='Exact Authenticode-valid DeepSeek desktop Electron GPU child, parent and binary SHA verified; no evaluation ownership; retained untouched'))
""".replace('EXPECTED_DESKTOP',repr(known))+marker;s=s.replace(marker,extra,1);compile(s,'<exact current desktop role original evaluator guard>','exec');return s
