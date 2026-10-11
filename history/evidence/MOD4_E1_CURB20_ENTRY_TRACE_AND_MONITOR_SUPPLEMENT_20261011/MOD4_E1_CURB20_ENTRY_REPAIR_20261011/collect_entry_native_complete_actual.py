from repair_io import *

def main():
    n,w=connect_both()
    try:
        v=linux_json(n,r'''from pathlib import Path
import json,hashlib,time,fcntl
D=Path(ROOT);B=Path(BUDGET);j=lambda p:json.loads(p.read_bytes());p=j(D/'reports/ENTRY_NATIVE_SCOPE_PASSED.json');s=j(D/'reports/ENTRY_NATIVE_STATE.json');assert p['passed'] and s['child'] is None
locs=[s['owner']]+[x['own_child_PID'] for x in p['results'].values()];exits=[]
for loc in locs:
 q=Path('/proc')/str(loc['pid']);a=None
 if q.exists():
  z=(q/'stat').read_text().split(') ',1)[1].split();a=dict(state=z[0],start_ticks=int(z[19]));assert a['state']=='Z' or a['start_ticks']!=loc['start_ticks']
 exits.append(dict(locator=loc,actual=a))
locks=[]
for q in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('r') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(str(q))
b=j(B);assert b['active_segment'] is None and b['authorized_training_seconds']==1188000 and len(b['budget_extensions'])==7
paths=set(D.glob('ENTRY*.json'))|set(D.glob('ENTRY*_trace/*'))|set((D/'reports').glob('ENTRY*.json'))
rows=[]
for q in sorted(paths):
 if not q.is_file():continue
 h=hashlib.sha256()
 with q.open('rb') as f:
  for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
 rows.append(dict(path=str(q),relative=q.relative_to(D).as_posix(),bytes=q.stat().st_size,sha256=h.hexdigest()))
for x in p['results'].values():assert next(y['sha256'] for y in rows if y['path']==x['path'])==x['sha256']
print(json.dumps(dict(epoch=time.time(),passed=p,actual_exits=exits,two_locks_free=locks,canonical_SHA=hashlib.sha256(B.read_bytes()).hexdigest(),authorized_seconds=b['authorized_training_seconds'],remaining_seconds=b['remaining_training_seconds'],active_segment=b['active_segment'],indices=rows,source_map=j(D/'reports/SOURCE_FREEZE.json'))))
'''.replace('ROOT',repr(NEW)).replace('BUDGET',repr(B)))
        dest=D/'native_complete_actual';dest.mkdir(exist_ok=True)
        with n.open_sftp() as f:
            for row in v['indices']:
                out=dest/row['relative'];out.parent.mkdir(parents=True,exist_ok=True)
                if not out.exists():f.get(row['path'],str(out))
                assert out.stat().st_size==row['bytes'] and H(out.read_bytes())==row['sha256'],row['path']
                row['local_path']=str(out.resolve())
        report=save('ENTRY_NATIVE_COMPLETE_COLLECTION_'+str(time.time_ns())+'.json',v)
        print(json.dumps(dict(report=str(report),complete=True,files=len(v['indices']),byteexact=True,bytes=sum(x['bytes'] for x in v['indices']))))
    finally:cleanup(n,w)

if __name__=='__main__':main()
