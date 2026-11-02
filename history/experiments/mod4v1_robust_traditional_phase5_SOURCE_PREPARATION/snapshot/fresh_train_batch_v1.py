"""Fresh named CPU TRAIN waves. No existing output or consumed case is reused."""
from pathlib import Path
import concurrent.futures,hashlib,json,os,subprocess,sys,time

def dump(path,data):
    with Path(path).open('x',encoding='utf-8')as f:json.dump(data,f,indent=2,allow_nan=False)

def launch(root,batch_name,runner,configs,protocol,summary_keys,max_workers=2):
    root=Path(root).resolve();batch=root/'batches'/batch_name
    assert batch.resolve().is_relative_to(root)and 1<=max_workers<=4
    assert len({name for name,_ in configs})==len(configs)
    for name,_ in configs:
        assert name and Path(name).name==name and not(root/'results'/name).exists(),name
    batch.mkdir(exist_ok=False)
    items=[]
    for name,cfg in configs:
        cp=batch/(name+'.json');dump(cp,cfg);items.append((name,cp))
    src=[]
    for name in (runner,Path(__file__).name):
        p=root/name;raw=p.read_bytes();src.append(dict(path=str(p),SHA=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
    dump(batch/'PROTOCOL.json',dict(**protocol,case_names=[name for name,_ in configs],max_workers=max_workers,runner_sources_before_physics=src))
    env=dict(os.environ);env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8')
    def run(item):
        name,cp=item;out=root/'results'/name;log=batch/(name+'.log');start=time.perf_counter()
        with log.open('xb')as stream:
            done=subprocess.run([sys.executable,'-B',str(root/runner),'--config',str(cp),'--out',str(out)],cwd=root,env=env,
                                stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT)
        row=dict(case=name,returncode=done.returncode,wall_s=time.perf_counter()-start,log=str(log))
        if(out/'result.json').is_file():
            result=json.loads((out/'result.json').read_bytes())
            for key in summary_keys:
                if key in result:row[key]=result[key]
            row['result_path']=str(out/'result.json')
        elif(out/'ERROR.json').is_file():row['software_error']=json.loads((out/'ERROR.json').read_bytes())
        return row
    rows=[]
    for start in range(0,len(items),max_workers):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)as pool:wave=list(pool.map(run,items[start:start+max_workers]))
        rows+=wave;print(json.dumps(wave,indent=2,allow_nan=False),flush=True)
        if any(row['returncode']!=0 for row in wave):break
    used={row['case']for row in rows}
    result=dict(kind=protocol['kind'],scheduled=len(items),executed=len(rows),unstarted=[name for name,_ in items if name not in used],rows=rows,
                results_are_not_robot_release=True)
    dump(batch/'BATCH_RESULT.json',result)
    if any(row['returncode']!=0 for row in rows):raise SystemExit(1)
    return result
