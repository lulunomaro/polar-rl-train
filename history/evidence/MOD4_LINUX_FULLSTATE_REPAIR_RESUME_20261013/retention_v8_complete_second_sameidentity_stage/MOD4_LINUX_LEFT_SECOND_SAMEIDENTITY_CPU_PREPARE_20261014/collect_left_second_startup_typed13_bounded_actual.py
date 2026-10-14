"""Future readonly actual 13-marker collection, independent of first save25."""
from pathlib import Path
import json,os,time
import second_root_owned_transport_common_v1 as t
CODE=r'''
from pathlib import Path
import json,sys,time,hashlib,psutil
R=Path(CONTEXT['proposed_root']);a=R/'left_second_formal3600_v1';sys.path.insert(0,str(R))
from left_sameidentity_typed13_receipts import validate_set
def record(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
mp=R/'LEFT_SECOND_SAMEIDENTITY_ADMISSION_MANIFEST.json';m=json.loads(mp.read_bytes())
assert record(mp)['sha256']==CONTEXT['manifest_SHA'] and m['source']['sha256']==CONTEXT['source_SHA'] and m['no_initializer_repeat'] is True
folders=[p for p in (a/'learning_logs').glob('*') if p.is_dir()] if (a/'learning_logs').is_dir() else []
if not folders:print(json.dumps(dict(startup_pending=True,source_SHA=CONTEXT['source_SHA'],PPO_claimed=False)));sys.exit(0)
assert len(folders)==1;paths=list(folders[0].glob('*STARTUP*VERIFIED.json'))
if len(paths)<13:print(json.dumps(dict(startup_pending=True,startup_count=len(paths),PPO_claimed=False)));sys.exit(0)
dp=a/'DISPATCH_RECEIPT.json';d=json.loads(dp.read_bytes());assert d['source']==m['source']
typed=validate_set(paths,d['child']['pid'],CONTEXT['source_SHA'])
actual=[]
for role,row in [('parent',d['parent']),('worker',d['child'])]:
 try:
  p=psutil.Process(row['pid']);ticks=int(Path('/proc',str(p.pid),'stat').read_text().split(') ',1)[1].split()[19])
  v=dict(role=role,pid=p.pid,created=p.create_time(),start_ticks=ticks,argv=p.cmdline(),cwd=p.cwd())
  assert v['created']==row['created'] and v['argv']==row['argv'] and v['cwd']==row['cwd']==str(R)
  if role=='parent':assert v['pid']==CONTEXT['parent_pid'] and ticks==CONTEXT['parent_start_ticks']
  actual.append(v)
 except psutil.NoSuchProcess:actual.append(dict(role=role,pid=row['pid'],actual_absent=True))
print(json.dumps(dict(epoch=time.time(),passed=True,root=str(R),source=m['source'],own_dispatch=d,typed13_actual=typed,actual_processes=actual,artifacts=[record(p) for p in sorted(paths)]+[record(mp),record(dp)],sameidentity_initializer_not_repeated=True,PPO_claimed=False,no_weight_saved_or_final_claim=True,no_GPU_or_budget_mutation=True)))
'''
def main():
    dispatch=json.loads((t.REPORTS/'SECOND_ROOT_UNIQUE_FORMAL_DISPATCH_ACTUAL.json').read_bytes());assert dispatch['source']['sha256']==t.SOURCE_SHA
    c=None;sf=None
    try:
        c=t.connect();v=t.run(c,CODE,'LEFT_SECOND_TYPED13_REMOTE_ACTUAL',dict(proposed_root=t.ROOT,source_SHA=t.SOURCE_SHA,manifest_SHA=dispatch['manifest_SHA'],parent_pid=dispatch['pid'],parent_start_ticks=dispatch['start_ticks']))
        if v.get('startup_pending'):print(json.dumps(v));return
        dest=t.D/('left_second_startup_actual_'+str(time.time_ns()));dest.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(60);rows=[]
        for i,row in enumerate(v['artifacts']):
            p=dest/(str(i)+'_'+row['path'].rsplit('/',1)[1]);sf.get(row['path'],str(p),max_concurrent_prefetch_requests=16)
            assert p.stat().st_size==row['bytes'] and t.sha(p)==row['sha256']
            rows.append(dict(remote_path=row['path'],local_path=str(p),bytes=p.stat().st_size,sha256=t.sha(p)))
        path=t.REPORTS/('LEFT_SECOND_TYPED13_STARTUP_TWOHOST_COLLECTION_ACTUAL_'+str(time.time_ns())+'.json');t.write_once(path,dict(epoch=time.time(),actual_remote_review=v,two_host_byteSHA_exact=rows,no_PPO_saved_or_formal_final_claim=True,pending_Git_by_root=True))
        print(json.dumps(dict(report=str(path),startup_actual13=True,PPO_claimed=False)))
    except BaseException:t.original_error('LEFT_SECOND_TYPED13_COLLECTION_ORIGINAL_ERROR');raise
    finally:
        if sf:sf.close()
        if c:c.close()
        os.environ.pop('RM_SSH_PASSWORD',None)
if __name__=='__main__':main()
