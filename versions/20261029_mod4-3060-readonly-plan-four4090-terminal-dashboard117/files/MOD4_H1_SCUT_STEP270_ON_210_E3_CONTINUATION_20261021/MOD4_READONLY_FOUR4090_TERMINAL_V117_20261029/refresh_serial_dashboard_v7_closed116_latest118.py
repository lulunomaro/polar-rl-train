"""Existing3060 terminal refresh with explicit closed116 and latest118 display status."""
from pathlib import Path
import argparse,json,runpy,time,traceback
HERE=Path(__file__).resolve().parent
ns=runpy.run_path(str(HERE/'refresh_serial_dashboard_v6_typed_curve.py'),run_name='definitions_only')['ns']
R=HERE/'reports/selected_v7';R.mkdir(exist_ok=True);ns['R']=R
alias=R/'REMOTE3060_VISIBLE_TERMINAL_ONEOFF_TASK_STARTED.json'
if not alias.exists():alias.write_bytes((HERE/'reports/selected_v6/REMOTE3060_VISIBLE_TERMINAL_ONEOFF_TASK_STARTED.json').read_bytes())
original_publish=ns['publish249']
def publish(secret,snapshot,first=False):
    assert not first,'Never relaunch the original visible Task'
    T=HERE.parent
    closed=ns['read'](T/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029/reports/CURRENT_CLOSED116_TWO_QUALIFIED_DIRECT_WHEEL_HEIGHT_FORMALS_ACTUAL.json')
    latest=ns['read'](T/'H1_NATIVE116_LATEST_USER_MUJOCO_MOTION_WM_V118_20261029/display/reports/USER_DISPLAY_DATA_COMPLETE.json')
    assert closed['actual_closed'] and latest['display_is_latest_qualified116']
    for host in snapshot['hosts']:
        for job in host.get('jobs',[]):
            if job['label'].startswith('H1-116') and job['known_process_state']=='original own process out':job['label']+=' [已结束；曲线/速度为最后学习窗口]'
    snapshot['current_qualified116_closed']=True;snapshot['latest_mujoco_actual118']=dict(model_SHA=latest['actual_source_SHA'],actual_seconds=latest['actual_duration_s'],terminal='closure',both_wheel_peak_control_endpoints_m=latest['actual_both_wheel_peak_m'])
    snapshot['sampler_status']='终态更新：116两路已完整保存/退出/结算，初始整态CPU通过；跨台/落台/落稳均0。\n最新MuJoCo：模型116 SHA78f5840e，灰色actual118+同模型蓝色想象；4.31s闭链保护结束，100Hz轮底峰约15.89mm。\n当前没有本方learning作业；其他GPU占用来源未识别，不归因于旧专家。单一串行本次采集，数据年龄见顶部'
    return original_publish(secret,snapshot,False)
ns['publish249']=publish
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--samples',type=int,default=1);p.add_argument('--period',type=float,default=30);a=p.parse_args()
    try:ns['main'](a.samples,a.period,True)
    except BaseException:ns['put']('V7_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_task_relaunch=True));raise
