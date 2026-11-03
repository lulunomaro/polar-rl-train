"""New CPU waves: software failure is artifact-aware, not just return-code-aware.
V1 and all recorded outcomes remain immutable. No actuation/control math here.
"""
from pathlib import Path
import concurrent.futures,hashlib,json,os,subprocess,sys,time,traceback

def dump(path,data):
    with Path(path).open('x',encoding='utf-8')as f:json.dump(data,f,indent=2,allow_nan=False)

def launch(root,batch_name,runner,configs,protocol,summary_keys,max_workers=2):
    root=Path(root).resolve();batch=root/'batches'/batch_name
    assert batch.resolve().is_relative_to(root)and type(max_workers)is int and 1<=max_workers<=4
    assert len({name for name,_ in configs})==len(configs)
    for name,cfg in configs:
        assert name and Path(name).name==name and name not in('.','..')and not(root/'results'/name).exists(),name
        assert cfg['case_id']==name
    batch.mkdir(exist_ok=False)
    items=[]
    for name,cfg in configs:
        cp=batch/(name+'.json');dump(cp,cfg);items.append((name,cp))
    src=[]
    for name in(runner,Path(__file__).name):
        p=root/name;raw=p.read_bytes();src.append(dict(path=str(p),SHA=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
    dump(batch/'PROTOCOL.json',dict(**protocol,case_names=[name for name,_ in configs],max_workers=max_workers,runner_sources_before_physics=src))
    env=dict(os.environ);env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONIOENCODING='utf-8')
    def run(item):
        name,cp=item;out=root/'results'/name;log=batch/(name+'.log');start=time.perf_counter();issues=[]
        row=dict(case=name,returncode=None,log=str(log))
        try:
            with log.open('xb')as stream:
                done=subprocess.run([sys.executable,'-B',str(root/runner),'--config',str(cp),'--out',str(out)],cwd=root,env=env,
                                    stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT)
            row['returncode']=done.returncode
            if done.returncode!=0:issues.append('nonzero_child_returncode')
        except Exception:
            issues.append('child_launch_exception');row['launch_exception']=traceback.format_exc()
        rp=out/'result.json';ep=out/'ERROR.json'
        row['result_present']=rp.is_file();row['ERROR_present']=ep.is_file()
        if ep.is_file():
            issues.append('ERROR_artifact_present')
            try:row['software_error']=json.loads(ep.read_bytes())
            except Exception:issues.append('ERROR_artifact_parse_failed')
        if not rp.is_file():issues.append('result_artifact_missing')
        else:
            try:
                result=json.loads(rp.read_bytes())
                valid=(isinstance(result,dict)and type(result.get('complete'))is bool and isinstance(result.get('stop'),str)
                       and type(result.get('controls'))is int and result['controls']>=0
                       and type(result.get('physics_steps'))is int and result['physics_steps']==20*result['controls']
                       and isinstance(result.get('config'),dict)and result['config'].get('case_id')==name)
                if not valid:issues.append('result_basic_schema_or_case_invalid')
                else:
                    for key in summary_keys:
                        if key in result:row[key]=result[key]
                    row['result_path']=str(rp)
            except Exception:
                issues.append('result_artifact_parse_failed');row['result_reader_exception']=traceback.format_exc()
        row['software_failure']=bool(issues);row['software_failure_reasons']=issues
        row['wall_s']=time.perf_counter()-start
        # Never infer unrecorded controls/steps from the requested duration.
        return row
    rows=[]
    for start in range(0,len(items),max_workers):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)as pool:wave=list(pool.map(run,items[start:start+max_workers]))
        rows+=wave;print(json.dumps(wave,indent=2,allow_nan=False),flush=True)
        if any(row['software_failure']for row in wave):break
    used={row['case']for row in rows}
    result=dict(kind=protocol['kind'],scheduled=len(items),executed=len(rows),unstarted=[name for name,_ in items if name not in used],rows=rows,
                software_failure=any(row['software_failure']for row in rows),results_are_not_robot_release=True)
    dump(batch/'BATCH_RESULT.json',result)
    if result['software_failure']:raise SystemExit(1)
    return result
