"""V3 uses the existing memory-only compressed-session adapter before recovery.
V1/V2 both failed locally before a network connection; their reports are retained.
"""
from pathlib import Path
import argparse,runpy,time,traceback
HERE=Path(__file__).resolve().parent
v2=runpy.run_path(str(HERE/'collect_serial_and_publish_dashboard_v2.py'),run_name='dashboard117_v2_definitions_only')
ns=v2['ns'];ns['__file__']=str(Path(__file__).resolve())
R=HERE/'reports/selected_v3';R.mkdir(exist_ok=True);ns['R']=R
original_credentials=ns['credentials']
def credentials():
    adapter=ns['module']('dashboard117_v3_credential_session_adapter',ns['T']/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
    module,previous=adapter.install()
    try:return original_credentials()
    finally:module.SESSION=previous
ns['credentials']=credentials
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--samples',type=int,default=3);p.add_argument('--period',type=float,default=30);p.add_argument('--refresh',action='store_true');a=p.parse_args()
    try:ns['main'](a.samples,a.period,a.refresh)
    except BaseException:ns['put']('V3_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_automatic_remote_task_relaunch=True));raise
