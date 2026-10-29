"""V4 binds E2 identity from its actual top-level worker_state publication.
V3 schema refusal occurred before network; no prior remote deployment is replayed.
"""
from pathlib import Path
import argparse,runpy,time,traceback
HERE=Path(__file__).resolve().parent
v3=runpy.run_path(str(HERE/'collect_serial_and_publish_dashboard_v3.py'),run_name='dashboard117_v3_definitions_only');ns=v3['ns']
R=HERE/'reports/selected_v4';R.mkdir(exist_ok=True);ns['R']=R
source=(HERE/'collect_serial_and_publish_dashboard.py').read_text(encoding='utf8')
import ast
tree=ast.parse(source);node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='jobs')
fragment=ast.get_source_segment(source,node)
old="e=first['admission_readonly_evidence'];worker=e['worker_state']['expected']"
assert fragment.count(old)==1
fragment=fragment.replace(old,"worker=first['worker_state']['expected']")
exec(compile(fragment,str(Path(__file__).resolve()),'exec'),ns)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--samples',type=int,default=3);p.add_argument('--period',type=float,default=30);p.add_argument('--refresh',action='store_true');a=p.parse_args()
    try:ns['main'](a.samples,a.period,a.refresh)
    except BaseException:ns['put']('V4_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_automatic_remote_task_relaunch=True));raise
