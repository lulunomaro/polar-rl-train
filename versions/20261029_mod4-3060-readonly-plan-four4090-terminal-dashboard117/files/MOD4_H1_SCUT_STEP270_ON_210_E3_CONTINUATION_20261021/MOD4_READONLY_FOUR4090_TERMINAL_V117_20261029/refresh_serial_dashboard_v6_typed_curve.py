"""Finite serial refresh of the existing visible117 terminal, with strict log fields.
Absent reward/event fields produce an unavailable status, never invented zero success.
"""
from pathlib import Path
import argparse,json,math,runpy,time,traceback
HERE=Path(__file__).resolve().parent
ns=runpy.run_path(str(HERE/'refresh_serial_dashboard_v5.py'),run_name='definitions_only')['ns']
R=HERE/'reports/selected_v6';R.mkdir(exist_ok=True);ns['R']=R
alias=R/'REMOTE3060_VISIBLE_TERMINAL_ONEOFF_TASK_STARTED.json'
if not alias.exists():alias.write_bytes((HERE/'reports/selected_v5/REMOTE3060_VISIBLE_TERMINAL_ONEOFF_TASK_STARTED.json').read_bytes())
a="   curve.append(dict(epoch=r['epoch']"
b="""   assert ev['schema']=='completed_control_goal_events_v1' and ev['diagnostic_valid'] and ev['invalid_rows']==0 and not ev['diagnostic_write_errors'],'actual event diagnostic invalid or absent'
   assert all(k in ev['events'] for k in ('takeoff_count','landing_count','recovery_count')) and 'both_leading_edges_cross_event_count' in ev
   expected_terms={'command_world_velocity','both_wheel_height_270_with_forward_command','supported_top_landing','supported_top_quiet','original_nonrequest_recovery'}
   assert set(terms)==expected_terms and isinstance(comp['total'],(int,float)),'selected116 optimization terms absent or wrong'
   assert abs(comp['total']-sum(terms.values()))<2e-8,'display components do not sum to optimized total'
   curve.append(dict(epoch=r['epoch']"""
assert ns['LINUX'].count(a)==1;ns['LINUX']=ns['LINUX'].replace(a,b)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--samples',type=int,default=1);p.add_argument('--period',type=float,default=30);p.add_argument('--until-original116-nominal',action='store_true');a=p.parse_args()
    if a.until_original116_nominal:
        w=ns['read'](ns['T']/'MOD4_H1_FUDAN270_DIRECT_COMMAND_RESOURCE_V116_20261029/reports/CURRENT_ACTUAL116_TWO_DIRECT_COMMAND_FIRST_NEW_UPDATES_AND_NORMAL_CLOSING_WORK_ORDER.json')
        end=max(g['nominal_end_epoch'] for g in w['actual_signed_go'].values());a.samples=max(1,math.ceil((end-time.time())/a.period)+1)
        assert a.samples<=60 and (a.samples-1)*a.period<=1700
    try:ns['main'](a.samples,a.period,True)
    except BaseException:ns['put']('V6_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_task_relaunch=True));raise
