"""Refresh the actual existing117 terminal; never register/start it again.
Use86's exact original known interpreter/loader prefix, not its bare system Python.
"""
from pathlib import Path
import argparse,ast,hashlib,json,runpy,time,traceback
HERE=Path(__file__).resolve().parent
ns=runpy.run_path(str(HERE/'collect_serial_and_publish_dashboard_v4.py'),run_name='definitions_only')['ns']
R=HERE/'reports/selected_v5';R.mkdir(exist_ok=True);ns['R']=R
recovery=HERE/'reports/selected_v4/REMOTE3060_ACTUAL_TERMINAL_AND_TASK_READONLY_RECOVERED.json'
bound=json.loads(recovery.read_bytes());assert bound['actual_task']['name']==ns['TASK'] and bound['started']
alias=R/'REMOTE3060_VISIBLE_TERMINAL_ONEOFF_TASK_STARTED.json'
if not alias.exists():
    alias.write_text(json.dumps(dict(original_actual_task=bound['actual_task'],original_started=bound['started'],original_report=str(recovery),original_report_SHA=hashlib.sha256(recovery.read_bytes()).hexdigest(),publication_alias_only_no_task_start=True),indent=2),encoding='utf8')
_,j86=ns['jobs']();prefix=j86[0]['worker']['argv'][:4]
assert prefix[1]=='--library-path' and prefix[0].startswith('/data/robemo/polar-rl-train/') and prefix[-1].endswith('/envs/mod4/bin/python')
source=(HERE/'collect_serial_and_publish_dashboard.py').read_text(encoding='utf8');tree=ast.parse(source)
fragment=ast.get_source_segment(source,next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='raw_code'))
old='command=shlex.quote(py)';assert fragment.count(old)==1
fragment=fragment.replace(old,"assert py=='/usr/bin/python3'\n    command=' '.join(shlex.quote(x) for x in known86_prefix)")
ns['known86_prefix']=prefix;exec(compile(fragment,str(Path(__file__).resolve()),'exec'),ns)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--samples',type=int,default=3);p.add_argument('--period',type=float,default=30);a=p.parse_args()
    try:ns['main'](a.samples,a.period,True)
    except BaseException:ns['put']('V5_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_task_relaunch=True));raise
