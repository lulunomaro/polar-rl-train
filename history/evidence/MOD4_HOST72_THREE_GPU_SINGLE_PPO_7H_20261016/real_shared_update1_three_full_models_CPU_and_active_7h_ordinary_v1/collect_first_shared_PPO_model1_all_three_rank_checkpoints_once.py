from pathlib import Path
import getpass,hashlib,json,sys,time,paramiko
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent;sys.path.insert(0,str(W/'MOD4_LINUX_WAVE50_BODYFRAME_RESET_INTEGRATION_20261014'));import transport_bodyframe_root_owned as t
def main():
 assert not (R/'FIRST_SHARED_PPO_UPDATE1_THREE_FULL_INPUTS_ACTUAL.json').exists()
 proof=json.loads((R/'THREE_RANK_SOURCE_FIRST_UPDATE_BOUND_WAIT_ACTUAL.json').read_bytes());state=next(x['data'] for x in proof['files'] if Path(x['path']).name=='CURRENT_THREE_RANK_ACTUAL.json');assert state['phase']=='learn';refs={int(k):z['latest_complete.json'] for k,z in state['ranks'].items()};assert all(x['updates']==1 for x in refs.values())
 out=D/'first_update1_full_checkpoints';out.mkdir();rows=[]
 def fetch(c,rank):
  sf=c.open_sftp();sf.get_channel().settimeout(60)
  try:
   x=refs[rank];p=out/('rank'+str(rank)+'_model_update1.pt');h=hashlib.sha256();size=0
   with sf.open(x['checkpoint'],'rb') as f,p.open('xb') as local:
    while b:=f.read(4*1024*1024):local.write(b);h.update(b);size+=len(b)
   assert size==x['bytes'] and h.hexdigest()==x['SHA'];rows.append(dict(rank=rank,path=str(p.resolve()),remote_path=x['checkpoint'],bytes=size,SHA=h.hexdigest()))
  finally:sf.close()
 c=None
 try:c=t.connect();fetch(c,0)
 finally:t.close(c)
 c=paramiko.SSHClient();c.load_system_host_keys();c.set_missing_host_key_policy(paramiko.AutoAddPolicy());pw=getpass.getpass('Host72 SSH password (hidden, never saved): ')
 try:
  c.connect('10.24.0.72',username='lc01',password=pw,timeout=15,auth_timeout=20,banner_timeout=20,allow_agent=False,look_for_keys=False);pw=None
  assert hashlib.sha256(c.get_transport().get_remote_server_key().asbytes()).hexdigest()=='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795'
  fetch(c,1);fetch(c,2)
 finally:pw=None;c.close()
 (R/'FIRST_SHARED_PPO_UPDATE1_THREE_FULL_INPUTS_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),rows=rows,all_three_remote_size_SHA_local_exact=True,immutable_update1_not_later_rolling_latest=True),indent=2));print(json.dumps(dict(three_complete_checkpoints_received=True,bytes=sum(x['bytes'] for x in rows))),flush=True)
if __name__=='__main__':main()
