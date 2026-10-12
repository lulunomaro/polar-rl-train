from route_second_io import *

def main():
    n,w=io.connect_both()
    try:
        v=run(n,r'''import os,json,time,subprocess
from pathlib import Path
def read(p):
 try:return Path(p).read_text()
 except Exception as e:return dict(error=type(e).__name__,message=str(e))
pids=(3340858,3340979)
ps=[]
for pid in pids:
 p=Path('/proc')/str(pid)
 if not p.exists():ps.append(dict(pid=pid,exited=True));continue
 item=dict(pid=pid,stat=read(p/'stat'),status=read(p/'status'),limits=read(p/'limits'),wchan=read(p/'wchan'),stack=read(p/'stack'),cgroup=read(p/'cgroup'),io=read(p/'io'),argv=(p/'cmdline').read_bytes().replace(bytes([0]),b' ').decode())
 item['threads_wchan']={t.name:read(t/'wchan') for t in (p/'task').iterdir()}
 ps.append(item)
cg={name:read('/sys/fs/cgroup/'+name) for name in ('memory.max','memory.current','memory.high','memory.events','memory.swap.max')}
policies={name:read('/proc/sys/vm/'+name) for name in ('overcommit_memory','overcommit_ratio','max_map_count','nr_hugepages')}
cmds=[]
for c in (['df','-B1','/home/egde/rl_candidates','/dev/shm'],['ps','-eo','pid,ppid,rss,etimes,comm','--sort=-rss'],['journalctl','-k','--since','2026-10-12 07:20:00','--until','2026-10-12 07:30:00','--no-pager','-n','100']):
 r=subprocess.run(c,capture_output=True,text=True);cmds.append(dict(command=c,returncode=r.returncode,stdout=r.stdout[:18000],stderr=r.stderr[:2000]))
print(json.dumps(dict(epoch=time.time(),processes=ps,cgroup_root_memory=cg,vm_policies=policies,commands=cmds,observer_only_no_signal_no_budget_write_no_OS_setting_change=True)))
''')
        p=save('FAILED_HOST_ALLOCATION_CONTRACT_ACTUAL_'+str(time.time_ns())+'.json',v)
        print(json.dumps(dict(report=str(p),epoch=v['epoch'],vm_policies=v['vm_policies'],cgroup=v['cgroup_root_memory'],processes=[dict(pid=x['pid'],exited=x.get('exited',False),wchan=x.get('wchan')) for x in v['processes']],commands=v['commands'])))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('HOST_ALLOCATION_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),observer_only=True));raise
