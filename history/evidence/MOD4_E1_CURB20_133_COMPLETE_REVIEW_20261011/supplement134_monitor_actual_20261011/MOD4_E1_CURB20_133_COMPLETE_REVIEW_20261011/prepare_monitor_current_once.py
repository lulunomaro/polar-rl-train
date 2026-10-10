"""Save exact previous monitor and new actual work order; app tool performs schedule update."""
from review133_io import *
import os,tomllib

def main():
 assert not (R/'MONITOR_CURRENT_PREPARED.json').exists()
 toml=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml';v=tomllib.loads(toml.read_text(encoding='utf8'))
 assert v['status']=='ACTIVE' and v['rrule']=='FREQ=HOURLY;INTERVAL=2' and v['target_thread_id']=='01a07a2d-9036-7531-a012-692df9f56353'
 raw=v['prompt'].encode();assert len(raw)==12048 and H(raw)=='df4887fb85920e36ea299151f91f1daad383360032eeef5d3569182ee5407cd5'
 p=D/'MONITOR_PREVIOUS_FORMAL389_SCHEMA_PROMPT.md';assert not p.exists();p.write_bytes(raw)
 prompt=(D/'MONITOR_CURRENT_ACTUAL_PROMPT.md').read_text(encoding='utf8').strip();assert '\ufffd' not in prompt
 save('MONITOR_CURRENT_PREPARED.json',dict(epoch=time.time(),old_prompt=dict(path=str(p),bytes=len(raw),sha256=H(raw)),new_prompt=dict(path=str(D/'MONITOR_CURRENT_ACTUAL_PROMPT.md'),bytes=len(prompt.encode()),sha256=H(prompt.encode())),status='ACTIVE',rrule=v['rrule'],old_prompt_historical_only=True))
 print(json.dumps(dict(id='mod4-10',mode='update',kind='heartbeat',name=v['name'],status='ACTIVE',rrule=v['rrule'],targetThreadId=v['target_thread_id'],destination='thread',prompt=prompt),ensure_ascii=True))

if __name__=='__main__':main()
