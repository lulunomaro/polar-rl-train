from pathlib import Path
import hashlib,json,subprocess,time,tomllib,traceback
B=Path(__file__).resolve().parent;R=B/'reports';G=B.parent/'polar-rl-train';D=G/'versions/20261020_e3_policy50_actual_continuation/POST_GIT_MONITOR_ORDINARY'
def git(*args):return subprocess.check_output(['git','-C',str(G),*args],text=True).strip()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 assert git('rev-parse','HEAD')=='f88a2eb9f501eb0fb178f407e51203dcb1cf0599' and not git('diff','--cached','--name-only') and not D.exists()
 tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines();assert len(tags)==1414
 args=json.loads((R/'V64_GIT_ACTUAL_EXISTING_AUTOMATION_UPDATE_ARGS.json').read_bytes());a=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text('utf8'))
 checks={'prompt_exact':a['prompt']==args['prompt'],'status':a['status']==args['status']=='ACTIVE','rrule_exact':a['rrule']==args['rrule'],'target_exact':a['target_thread_id']==args['targetThreadId'],'id':a['id']=='mod4-10'}
 put(R/'V64_GIT_ACTUAL_EXISTING_AUTOMATION_EXACT_READBACK_CPU_ACTUAL.json',dict(epoch=time.time(),checks=checks,passed=all(checks.values()),no_second_monitor=True,unique_stage_commit='f88a2eb9f501eb0fb178f407e51203dcb1cf0599'))
 assert all(checks.values()),checks
 sources=[Path(__file__),R/'V64_GIT_ACTUAL_EXISTING_AUTOMATION_UPDATE_ARGS.json',R/'V64_GIT_ACTUAL_EXISTING_AUTOMATION_APP_RECEIPT.json',R/'V64_GIT_ACTUAL_EXISTING_AUTOMATION_EXACT_READBACK_CPU_ACTUAL.json']
 D.mkdir(parents=True);index=[]
 for p in sources:
  raw=p.read_bytes();raw.decode('utf8');dest=D/p.name;dest.write_bytes(raw);index.append(dict(source=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),archive=dest.relative_to(G).as_posix()))
 put(D/'SUPPLEMENT_INDEX.json',dict(epoch=time.time(),entries=index,ordinary_only_no_record_or_tag_or_training=True))
 selected=[p.relative_to(G).as_posix() for p in D.iterdir() if p.is_file()]
 subprocess.run(['git','-C',str(G),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(p.encode('utf8') for p in selected)+b'\0',capture_output=True,check=True)
 git('commit','-m','Record actual 50 Hz continuation monitor and confirmed Git handoff');git('push','origin','main')
 head=git('rev-parse','HEAD');remote=dict(line.split()[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines());assert remote['refs/heads/main']==head
 for line in tags:
  row=line.split();assert remote[row[0]]==row[1]
  if len(row)==3:assert remote[row[0]+'^{}']==row[2]
 assert not git('status','--porcelain')
 print(json.dumps(dict(remote_main=head,all1414_tag_objects_and_peels_unchanged=True,existing_monitor_exact=True,ordinary_only=True,workspace_clean=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  put(R/('POSTGIT_ORDINARY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_once=True));raise
