"""Read own actual scope and save all new receipts, never relaunch or mutate budget."""
from slope_io import *
import traceback
def main():
 n,w=connect_both()
 try:
  actual=linux_json(n,r'''from pathlib import Path
import json,hashlib,time
D=Path(ROOT);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def identity(v):
 if not v:return None
 p=Path('/proc')/str(v['pid'])
 if not p.exists():return None
 a=(p/'stat').read_text().split(') ',1)[1].split();return dict(pid=v['pid'],state=a[0],start_ticks=int(a[19]),argv=[s.decode(errors='replace') for s in (p/'cmdline').read_bytes().split(b'\0') if s],same_start=int(a[19])==v['start_ticks'])
reports={};indices=[]
for p in sorted((D/'reports').glob('*')):
 if not p.is_file():continue
 if p.stat().st_size<1800000 and p.suffix=='.json':reports[p.name]=j(p)
 indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p)))
st=reports.get('E1_STATE.json');owner=identity(st.get('owner')) if st else None;child=identity(st.get('child')) if st else None;guardian=identity(reports.get('E1_GUARDIAN_STARTED.json'))
l=j(B);active=l['active_segment'];remaining=l['authorized_training_seconds']-l['charged_training_seconds'];f=j(D/'reports/SOURCE_FREEZE.json');assert len(f['sha256'])==402 and all(h(D/n)==sha for n,sha in f['sha256'].items())
logs=[]
for p in sorted(D.glob('*.log')):logs.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),tail=p.read_text(errors='replace')[-6000:]))
runs=[]
for p in sorted(list((D/'learning_logs').glob('*'))+list((D/'discard_logs').glob('*'))):
 if not p.is_dir():continue
 run=dict(path=str(p),reports={},indices=[])
 for q in sorted(p.glob('*.json')):
  run['indices'].append(dict(path=str(q),bytes=q.stat().st_size,sha256=h(q)))
  if q.stat().st_size<1800000:run['reports'][q.name]=j(q)
 runs.append(run)
print(json.dumps(dict(epoch=time.time(),root=str(D),source_count=402,phase=st['phase'] if st else 'startup_pending',actual_owner=owner,actual_child=child,actual_guardian=guardian,own_reports=reports,report_indices=indices,runs=runs,logs=logs,canonical=dict(sha256=h(B),active=active,authorized_seconds=l['authorized_training_seconds'],remaining_seconds_before_unaccounted_tail=remaining),read_only=True)))
'''.replace('ROOT',repr(NEW)).replace('BUDGET',repr(B)))
  p=save('SLOPE_ACTUAL_'+str(time.time_ns())+'.json',actual)
  with n.open_sftp() as f:
   for row in actual['report_indices']+[x for run in actual['runs'] for x in run['indices']]:
    if row['bytes']>=1800000:continue
    target=D/'actual_remote'/Path(row['path']).relative_to(NEW)
    raw=f.open(row['path']).read();assert H(raw)==row['sha256'];target.parent.mkdir(parents=True,exist_ok=True)
    # Dynamic files are retained in their independently timestamped actual snapshot.
    if target.exists():
     if target.read_bytes()==raw:continue
     target=target.with_name(target.stem+'_'+str(actual['epoch']).replace('.','_')+target.suffix)
    assert not target.exists();target.write_bytes(raw)
  print(json.dumps(dict(report=str(p),phase=actual['phase'],owner=actual['actual_owner'],child=actual['actual_child'],attention=actual['own_reports'].get('E1_ATTENTION.json'),passed=[k for k in actual['own_reports'] if 'PASSED' in k],remaining_seconds=actual['canonical']['remaining_seconds_before_unaccounted_tail'],active=actual['canonical']['active'])))
 finally:cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('ACTUAL_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),read_only_no_signal_or_relaunch=True));raise
