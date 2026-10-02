"""Read-only bounded snapshot of the authorized RL project; no simulator imports."""
import datetime, hashlib, json, os, pathlib, subprocess
ROOT = pathlib.Path('/home/egde/fangzhen_linux')
def cmd(args):
    p = subprocess.run(args, capture_output=True, text=True, timeout=15)
    return {'rc':p.returncode, 'stdout':p.stdout.strip(), 'stderr':p.stderr.strip()}
def stamp(p):
    s=p.stat()
    return {'path':str(p.relative_to(ROOT)), 'bytes':s.st_size, 'mtime_ns':s.st_mtime_ns}
processes=[]
for p in pathlib.Path('/proc').iterdir():
    if not p.name.isdigit(): continue
    try:
        argv=(p/'cmdline').read_bytes().split(b'\0')
        args=[a.decode(errors='replace') for a in argv if a]
        if not args or not any(x.endswith(('train_mod4_ppo.py','eval_terrain_mod4.py','eval_mod4_skills.py')) for x in args): continue
        env={}
        for item in (p/'environ').read_bytes().split(b'\0'):
            k,sep,v=item.partition(b'=')
            name=k.decode(errors='replace')
            if (name.startswith('RM_') or name=='CUDA_VISIBLE_DEVICES') and not any(x in name for x in ['TOKEN','PASSWORD','SECRET','KEY']):
                env[name]=v.decode(errors='replace')
        processes.append({'pid':int(p.name),'argv':args,'cwd':os.readlink(p/'cwd'),'stdout':os.readlink(p/'fd/1'),'env':env})
    except (OSError,PermissionError): pass
sources=[]
for folder in [ROOT/'isaac/mod4', ROOT/'scripts']:
    for p in folder.iterdir():
        if p.is_file() and p.suffix in {'.py','.sh'} and (folder.name=='mod4' or any(k in p.name for k in ['mod4','phase','chain'])):
            item=stamp(p); item['sha256']=hashlib.sha256(p.read_bytes()).hexdigest(); sources.append(item)
logs=ROOT/'logs/isaac_mod4'
recent=[]
for p in sorted(logs.iterdir(), key=lambda p:p.stat().st_mtime_ns, reverse=True)[:20]:
    item=stamp(p)
    if p.is_dir():
        item['files']=[stamp(x) for x in p.rglob('*') if x.is_file() and x.suffix in {'.json','.yaml','.yml','.txt'}][:60]
    recent.append(item)
report={'time':datetime.datetime.now().astimezone().isoformat(),'host':cmd(['hostname']), 'gpu':cmd(['nvidia-smi','--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu','--format=csv,noheader']), 'processes':processes,'source_files':sources,'recent_logs':recent,'disk':cmd(['df','-h',str(ROOT)]),'git':cmd(['git','-C',str(ROOT),'status','--short'])}
print(json.dumps(report,indent=2,ensure_ascii=False))
