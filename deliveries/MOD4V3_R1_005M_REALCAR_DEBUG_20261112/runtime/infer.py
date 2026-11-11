"""Offline JSON-lines bridge. It prints commands; it never sends to a motor bus."""
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parent));from control import Controller
p=argparse.ArgumentParser();p.add_argument('--state');a=p.parse_args();c=Controller()
if a.state:
 state=json.loads(Path(a.state).read_text(encoding='utf-8'));print(json.dumps(c.policy_tick(state),allow_nan=False));raise SystemExit
for line in sys.stdin:
 try:
  state=json.loads(line)
  if state.get('reset'):c.reset();reply={'reset':True}
  elif state.get('tick')=='PD':reply={'torque_Nm':c.PD_tick(state['joint_position_rad'],state['joint_velocity_rad_s']).tolist()}
  else:reply=c.policy_tick(state)
  print(json.dumps(reply,allow_nan=False),flush=True)
 except (ValueError,KeyError,RuntimeError) as e:c.reset();print(json.dumps({'error':str(e),'disable_output':True}),flush=True)
