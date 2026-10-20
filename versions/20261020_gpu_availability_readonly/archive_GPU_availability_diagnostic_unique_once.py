from pathlib import Path
import hashlib,json,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';G=B.parent/'polar-rl-train';D=G/'versions/20261020_gpu_availability_readonly'
ID='gpu-availability-readonly-after-policy50'
def git(*args):return subprocess.check_output(['git','-C',str(G),*args],text=True).strip()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def main():
 v=json.loads((R/'CURRENT_GPU_AVAILABILITY_READONLY_RETURNED_ACTUAL.json').read_bytes());assert v['actual_finite_transport_returned'] and not D.exists() and not git('diff','--cached','--name-only')
 tags=git('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines();assert len(tags)==1414
 from datetime import datetime,timezone,timedelta
 stamp=datetime.fromtimestamp(v['host72']['epoch'],timezone(timedelta(hours=8))).isoformat()
 note=f'''# Current GPU availability read-only diagnostic

Human asked whether other GPUs are now free. One new finite reader authenticated the original strict host72 pin through hidden stdin and queried NVIDIA GPU/free-memory/compute snapshots, RAM/disk and existing project locks. Only this project's own serial process identities were examined; no peer identity query, process termination, lock deletion, training deployment, system switch, model access or accounting write occurred. It then closed72 transport and sequentially used the existing strict Windows210 transport; the Linux pin was unchanged. Local NVIDIA query was read-only. Host249 was not queried.

Snapshot {stamp}: host72 H1 UUID16828 had9683MiB free and94% utilization, with an unrelated-identity compute PID104121 using14514MiB. The owner/workload is unknown. This does not meet the future H1 minimum15669MiB headroom, so free project lock alone is not sufficient. E3 UUIDc27 had9653MiB free/78% utilization; current worker160582/create1792490561.02/exact argv matched the owned50Hz series and compute PID. These values are instantaneous, not permanent occupancy or performance claims.

Host10.24.4.210 returned Windows11 Pro10.0.22631, RTX4090 UUID937b with23576MiB free,567MiB used and0% utilization. WDDM compute rows report[N/A] memory, so this is low-load available VRAM rather than a proven empty/exclusive GPU. Original Linux training/canonical workflow remains unavailable on this boot; no migration or reboot was performed. Local RTX5070Ti Laptop had8912MiB free/19% utilization; laptop training remains paused and this query authorizes no dispatch. All resource values may change.

Two local source-lookup errors used a nonexistent controller50_V5 path; original failed path/error and actual correction are preserved. These were local lookup errors, not SSH/GPU failures. No consumed reader, deployment or old cleanup was replayed. Current E3 policy50 training and its existing monitor continue unchanged. All saved source/error/full receipts are included in this unique diagnostic stage.
'''
 (B/'STAGE_NOTE.md').write_text(note,encoding='utf8');D.mkdir(parents=True)
 index=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  raw=p.read_bytes();raw.decode('utf8');assert len(raw)<50000000;dest=D/p.relative_to(B);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);index.append(dict(source=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),archive=dest.relative_to(G).as_posix()))
 put(D/'COMPLETE_TEXT_SOURCE_ERROR_INDEX.json',dict(epoch=time.time(),entries=index))
 sys.path.insert(0,str(G/'archive_tools'));import record_experiment as record
 original=record.git
 def stdin_git(*args):
  if args[0]=='add':
   assert args[1]=='--';p=subprocess.run(['git','-C',str(G),'add','--pathspec-from-file=-','--pathspec-file-nul'],input=b'\0'.join(x.encode('utf8') for x in args[2:])+b'\0',capture_output=True,check=True);return p.stdout.decode().strip()
  return original(*args)
 record.git=stdin_git;selected=[p.relative_to(G).as_posix() for p in sorted(D.rglob('*')) if p.is_file()]
 sys.argv=['record_experiment.py','--id',ID,'--title','Read-only current GPU availability: Windows210 low load, Linux72 H1 memory constrained','--kind','diagnostic','--note-file',str(D/'STAGE_NOTE.md'),'--validation','One finite strict-pinned72/210 sequential reader; actual NVIDIA snapshots; no dispatch, peer identity query or budget change','--files',*selected,'--push'];record.main()
 head=git('rev-parse','HEAD');tag='trial-20261020-'+ID;remote=dict(line.split()[::-1] for line in git('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines());assert remote['refs/heads/main']==head and remote['refs/tags/'+tag]==git('rev-parse',tag) and remote['refs/tags/'+tag+'^{}']==head
 for line in tags:
  row=line.split();assert remote[row[0]]==row[1]
  if len(row)==3:assert remote[row[0]+'^{}']==row[2]
 assert not git('status','--porcelain')
 print(json.dumps(dict(remote_main=head,tag=tag,tag_object=remote['refs/tags/'+tag],total_tags=1415,all1414_old_tag_objects_and_peels_preserved=True,workspace_clean=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/('ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_record_or_once=True));raise
