"""Visible, bounded363 recorded-pose replay with platform and truthful labels."""
from pathlib import Path
import ast
P=Path(__file__).resolve().parent;N=P.parent/'MPC_PLANNED_INITIAL_QUEUE_HOLD_V363_20261102'
source=(N/'view363_actual_MPC_target_replay.py').read_text('utf8')
source=source.replace("N=Path(__file__).resolve().parent;R=N/'reports';O=N/'VISIBLE_REPLAY363'", "N=Path("+repr(str(N))+");R=N/'reports';O=N/'VISIBLE_REPLAY364'")
source=source.replace("[edge+1.5*c,lat+1.5*s,.135]if r['result']['kind']in('state_target','processed_MPC_target')else[0,0,-10]", "[edge+1.5*c,lat+1.5*s,.135]")
source=source.replace('time.monotonic()-started<1800','time.monotonic()-started<90')
source=source.replace("if not state['paused']:state['clock']=(state['clock']+delta*state['speed'])%(r['seconds']+.05)", "state['case']=min(3,int((now-started)//20));r=rows[state['case']];p=packets[state['case']]\n        if not state['paused']:state['clock']=(state['clock']+delta*state['speed'])%(r['seconds']+.05)")
source=source.replace("state=dict(case=0,clock=0.,speed=.1,paused=False", "state=dict(case=0,clock=0.,speed=.5,paused=False")
source=source.replace("if not shot and i>=min(max(0,r['controls']-2),15):", "if not shot:")
source=source.replace("actual_source='PhysX363 final324 first episodes',policy_updates=4379", "actual_source='PhysX363 model-free currentstate MPC firstepisodes',policy_updates=0")
source=source.replace('FINAL324 / NO NN / source target trace / actual PhysX363 RECORDED REPLAY','NO NN / actual PhysX363 MPC reset hold comparison RECORDED REPLAY')
source=source.replace('planned motor targets / actor terminal0 / WM H32','current-state MPC / initial queue hold comparison')
source=source.replace('REFERENCE TRACKER: planned goals; use saved independent evaluation facts','DIAGNOSTIC PRIVILEGED MPC: not a learned depth actor; use saved independent facts')
ast.parse(source)
exec(compile(source,str(P/'generated364_visible_pose_replay.py'),'exec'),dict(__name__='__main__',__file__=str(P/'generated364_visible_pose_replay.py')))
