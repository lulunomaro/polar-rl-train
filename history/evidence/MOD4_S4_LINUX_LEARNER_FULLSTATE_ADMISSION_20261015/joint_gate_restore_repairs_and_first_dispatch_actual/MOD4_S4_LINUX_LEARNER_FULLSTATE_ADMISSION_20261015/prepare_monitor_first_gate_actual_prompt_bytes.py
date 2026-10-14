from pathlib import Path
import os,tomllib,json,hashlib,time
D=Path(__file__).resolve().parent
def main():
    p=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'automations/mod4-10/automation.toml'
    v=tomllib.loads(p.read_text(encoding='utf8'))
    old=D/'MONITOR_PREVIOUS_RULE35_BEFORE_REAL_LINUX_S4_FULLSTATE_AND_FIRST_GATE_20261015.txt'
    if not old.exists():old.write_bytes(v['prompt'].encode('utf8'))
    current=D/'MONITOR_S4_FIRST_SUPPORTED_GATE45M_DISPATCHED_ACTUAL_20261015.txt'
    raw=current.read_text(encoding='utf8').rstrip('\r\n');current.write_bytes(raw.encode('utf8'))
    print(json.dumps(dict(prompt=raw,prompt_SHA=hashlib.sha256(raw.encode()).hexdigest(),name=v['name'],rrule=v['rrule'],status=v['status'],targetThreadId=v['target_thread_id'],old_prompt_SHA=hashlib.sha256(old.read_bytes()).hexdigest())))
if __name__=='__main__':main()
