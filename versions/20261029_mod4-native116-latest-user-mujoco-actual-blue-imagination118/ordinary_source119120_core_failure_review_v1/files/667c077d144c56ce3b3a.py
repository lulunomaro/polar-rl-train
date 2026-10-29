"""One finite refresh of the user's existing terminal with fresh known PID identity.
No terminal restart if it has closed; no unknown process identity query.
"""
from pathlib import Path
import argparse,base64,json,runpy,time,traceback
HERE=Path(__file__).resolve().parent
ns=runpy.run_path(str(HERE/'refresh_serial_dashboard_v7_closed116_latest118.py'),run_name='definitions_only')['ns']
R=HERE/'reports/selected_v8';R.mkdir(exist_ok=True);ns['R']=R
alias=R/'REMOTE3060_VISIBLE_TERMINAL_ONEOFF_TASK_STARTED.json'
if not alias.exists():alias.write_bytes((HERE/'reports/selected_v7/REMOTE3060_VISIBLE_TERMINAL_ONEOFF_TASK_STARTED.json').read_bytes())
expected=json.loads((HERE/'reports/selected_v4/REMOTE3060_ACTUAL_TERMINAL_AND_TASK_READONLY_RECOVERED.json').read_bytes())['started']
class ViewerClosed(Exception):pass
old_credentials=ns['credentials']
def credentials():
    pw72,pw249,req86=old_credentials();c=ns['connect249'](pw249)
    try:
        code="""import json,time,psutil
expected=EXPECTED
try:
 p=psutil.Process(expected['pid'])
 if p.create_time()!=expected['creation']:out=dict(known_original_viewer_alive=False,PID_recycled_foreign_identity_not_read=True)
 else:
  row=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),cwd=p.cwd())
  assert row=={k:expected[k] for k in row},'original viewer identity differs'
  out=dict(known_original_viewer_alive=p.is_running(),exact_identity=row)
except psutil.NoSuchProcess:out=dict(known_original_viewer_alive=False,original_out=True)
out.update(epoch=time.time(),no_Task_restart=True,no_GPU_model_or_account_query=True,not_a_new_session0_visibility_assertion=True)
print(json.dumps(out))
""".replace('EXPECTED',repr(expected))
        enc=base64.b64encode(code.encode()).decode();_,o,e=c.exec_command('"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe" -B -X utf8 -c "import base64;exec(base64.b64decode(\''+enc+'\'))"',timeout=30)
        raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,err.decode('utf8','replace')[-1600:]
        state=json.loads(raw);ns['put']('KNOWN3060_VIEWER_FRESH_IDENTITY_'+str(time.time_ns())+'.json',state)
        if not state['known_original_viewer_alive']:raise ViewerClosed('Original viewer closed; no task replay or other-host query')
        return pw72,pw249,req86
    finally:c.close()
ns['credentials']=credentials
outer_publish=ns['publish249'];base_publish=outer_publish.__globals__['original_publish']
def append_source119(secret,snapshot,first=False):
    snapshot['sampler_status']+='\n源码119（未部署/未训练）：前2秒原目标x=0带约5.6cm后退位置信号；neutral-X候选CPU通过。跳跃过程/闭链问题仍待解决。'
    snapshot['source119_is_not_runtime']=True
    return base_publish(secret,snapshot,first)
outer_publish.__globals__['original_publish']=append_source119
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--samples',type=int,default=1);p.add_argument('--period',type=float,default=30);a=p.parse_args()
    try:ns['main'](a.samples,a.period,True)
    except ViewerClosed as e:ns['put']('FINITE_MONITOR119_VIEWER_CLOSED_NO_RELAUNCH_'+str(time.time_ns())+'.json',dict(epoch=time.time(),reason=str(e),normal_user_window_exit_not_training_failure=True));print(json.dumps(dict(viewer_closed=True,no_restart=True)))
    except BaseException:ns['put']('V8_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_task_relaunch=True));raise
