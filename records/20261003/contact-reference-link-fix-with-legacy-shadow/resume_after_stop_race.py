import json,shlex,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
code='''import json,os,signal,time
from pathlib import Path
root=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002');pid=2490960
def identity():
 p=Path('/proc')/str(pid);s=(p/'stat').read_text().split(') ',1)[1].split()
 return dict(pid=pid,state=s[0],start_ticks=s[19],cwd=str((p/'cwd').resolve()),argv=(p/'cmdline').read_bytes().decode().split('\\0'))
before=identity();assert before['start_ticks']=='17250655' and before['cwd']==str(root) and any(a.endswith('/supervise_autonomy.py') for a in before['argv'])
os.kill(pid,signal.SIGCONT);time.sleep(.2);after=identity();assert after['state']!='T'
receipt=dict(reason='Restore verified parent after asynchronous SIGSTOP status assertion; candidate script failed before own evaluation/deployment',before=before,after=after,epoch=time.time(),ledger_written=False,production_sources_modified=False)
p=root/'reports/CONTACT_REFERENCE_STOP_RACE_RECOVERY_20261003.json';assert not p.exists();p.write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
'''
c=connect()
try:
 _,o,e=c.exec_command('python3 -c '+shlex.quote(code),timeout=20)
 raw=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err
 (Path(__file__).parent/'CONTACT_REFERENCE_STOP_RACE_RECOVERY_20261003.json').write_text(raw);print(raw)
finally:c.close()
