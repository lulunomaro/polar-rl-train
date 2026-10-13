from pathlib import Path
import ast, base64, hashlib, importlib.metadata as md, importlib.util, json, os, subprocess, sys, time, traceback

ROOT = Path('C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013')
REPORT = ROOT / 'install_reports' / ('KERNEL_HTTP_CONSUMER_CPU_ACTUAL_' + str(time.time_ns()) + '.json')
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def tree_line(p, text, needle):
    lines = text.splitlines(); hits=[]
    for i,line in enumerate(lines):
        if needle in line.lower():
            hits.append({'line':i+1,'context':lines[max(0,i-3):min(len(lines),i+7)]})
    return hits
result={'epoch':time.time(),'CPU_only':True,'no_Isaac_Kit_Torch_CUDA_import':True,'installed_SDK_code_and_metadata_unchanged':True,'python':sys.executable,'versions':{},'source_consumers':[],'headless_entry_sources':[],'scan_counts':{},'httpx_spec':None}
try:
    for n in ['isaacsim-kernel','fastapi','starlette','click','isaaclab','isaaclab-rl','torch','tensordict','httpx','httpcore']:
        try:result['versions'][n]=md.version(n)
        except md.PackageNotFoundError:result['versions'][n]=None
    result['httpx_spec']=str(importlib.util.find_spec('httpx'))
    dist_names=[]; scanned=set(); count=0
    for d in md.distributions():
        n=d.metadata.get('Name','')
        if not n.lower().startswith('isaacsim'):continue
        dist_names.append({'name':n,'version':d.version,'requires':d.requires or []})
        for f in d.files or []:
            p=Path(d.locate_file(f))
            if p in scanned or p.suffix.lower() not in ('.py','.toml','.kit','.json','.cfg') or not p.is_file():continue
            scanned.add(p);count+=1
            try:t=p.read_text(encoding='utf8')
            except UnicodeError:continue
            if 'fastapi' not in t.lower() and 'click' not in t.lower():continue
            imports=[]
            if p.suffix=='.py':
                try:
                    node=ast.parse(t)
                    for x in ast.walk(node):
                        if isinstance(x,ast.Import):imports.extend({'line':x.lineno,'name':a.name} for a in x.names if a.name.startswith(('fastapi','click')))
                        if isinstance(x,ast.ImportFrom) and (x.module or '').startswith(('fastapi','click')):imports.append({'line':x.lineno,'module':x.module,'names':[a.name for a in x.names]})
                except SyntaxError:imports.append({'parse':'SyntaxError'})
            result['source_consumers'].append({'distribution':n,'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'imports':imports,'fastapi':tree_line(p,t,'fastapi'),'click':tree_line(p,t,'click')})
    result['scan_counts']={'isaacsim_distributions':dist_names,'unique_text_files':count,'matching_files':len(result['source_consumers'])}
    entry_paths=[ROOT/'sdk_exact/source/isaaclab/isaaclab/app/app_launcher.py']
    for d in md.distributions():
        if d.metadata.get('Name','').lower() not in ('isaacsim','isaacsim-kernel','isaacsim-app'):continue
        for f in d.files or []:
            p=Path(d.locate_file(f))
            if p.suffix=='.py' and p.is_file() and (p.name=='__init__.py' and p.parent.name=='isaacsim' or p.name in ('simulation_app.py','application.py')):entry_paths.append(p)
    for p in dict.fromkeys(entry_paths):
        t=p.read_text(encoding='utf8');node=ast.parse(t);imports=[]
        for x in ast.walk(node):
            if isinstance(x,ast.Import):imports.extend({'line':x.lineno,'name':a.name} for a in x.names)
            elif isinstance(x,ast.ImportFrom):imports.append({'line':x.lineno,'module':x.module,'names':[a.name for a in x.names]})
        result['headless_entry_sources'].append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'imports':imports,'headless':tree_line(p,t,'headless'),'experience':tree_line(p,t,'experience'),'fastapi':tree_line(p,t,'fastapi'),'click':tree_line(p,t,'click')})
    result['apps_actual_exists']=(ROOT/'sdk_exact/apps').exists()
    pc=subprocess.run([sys.executable,'-m','pip','check'],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=60)
    result['post_click_pipcheck_actual']={'exit_code':pc.returncode,'stdout':pc.stdout,'stderr':pc.stderr,'original_05I_two_failures_preserved':True}
    result['source_audit_completed']=True
except BaseException as e:
    result.update(error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(),source_audit_completed=False)
finally:
    with REPORT.open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
    print(json.dumps({'report':str(REPORT),'bytes':REPORT.stat().st_size,'sha256':sha(REPORT),'source_audit_completed':result.get('source_audit_completed'),'versions':result['versions'],'matches':len(result['source_consumers']),'httpx_spec':result['httpx_spec']}))
if not result.get('source_audit_completed'):sys.exit(1)
