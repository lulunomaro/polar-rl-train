from pathlib import Path
import hashlib,json,subprocess,time,tomllib,traceback
B=Path(__file__).resolve().parent;R=B/'reports';G=B.parent/'polar-rl-train';D=G/'versions/20261020_two_linux_policy50_series/cohort33_closed_cohort34_learning_V67/POST_GIT_MONITOR_ORDINARY'
def git(*args):return subprocess.check_output(['git','-C',str(G),*args],text=True).strip()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert git('rev-parse','HEAD')=='d0a151fd3e468548c87479bf8af2c5179b09c8b1' and not git('status','--porcelain') and not D.exists();tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines();assert len(tags)==1416;a=json.loads((R/'V67_GIT_ACTUAL_MONITOR_UPDATE_ARGS.json').read_bytes());saved=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'));checks=dict(prompt=saved['prompt']==a['prompt'],status=saved['status']==a['status']=='ACTIVE',rrule=saved['rrule']==a['rrule'],target=saved['target_thread_id']==a['targetThreadId'],id=saved['id']=='mod4-10');assert all(checks.values()),checks;readback=R/'V67_GIT_ACTUAL_MONITOR_EXACT_READBACK_CPU_ACTUAL.json';put(readback,dict(epoch=time.time(),passed=True,checks=checks,no_second_monitor=True));D.mkdir(parents=True);sources=[Path(__file__),B/'build_V67_git_actual_monitor_args_once.py',R/'V67_GIT_ACTUAL_MONITOR_UPDATE_ARGS.json',R/'V67_GIT_ACTUAL_MONITOR_APP_RECEIPT.json',readback];index=[]
 for p in sources:
  raw=p.read_bytes();raw.decode('utf8');q=D/p.name;q.write_bytes(raw);index.append(dict(source=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),archive=q.relative_to(G).as_posix()))
 put(D/'SUPPLEMENT_INDEX.json',dict(epoch=time.time(),entries=index,ordinary_only_no_record_tag_or_training=True));paths=[p.relative_to(G).as_posix() for p in D.iterdir() if p.is_file()];subprocess.run(['git','-C',str(G),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(p.encode('utf8') for p in paths)+b'\0',capture_output=True,check=True);git('commit','-m','Record two-policy50 cohort34 existing monitor Git handoff and exact readback');git('push','origin','main');head=git('rev-parse','HEAD');remote=dict(line.split()[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines());assert remote['refs/heads/main']==head
 for line in tags:
  row=line.split();assert remote[row[0]]==row[1]
  if len(row)==3:assert remote[row[0]+'^{}']==row[2]
 assert not git('status','--porcelain');print(json.dumps(dict(remote_main=head,all1416_tag_objects_and_peels_unchanged=True,existing_monitor_exact=True,ordinary_only=True,workspace_clean=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('V67_POSTGIT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_replay_once=True));raise
