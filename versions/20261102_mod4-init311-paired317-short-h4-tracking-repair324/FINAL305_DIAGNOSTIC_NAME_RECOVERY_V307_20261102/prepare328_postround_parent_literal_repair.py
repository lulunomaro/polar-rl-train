"""Correct the unused postround parent literal; preserve all324/325 frozenbytes."""
from pathlib import Path
import ast,hashlib,json,re,time
N=Path(__file__).resolve().parent;T=N.parent;D=T/'REFERENCE_H4_TRACKING_REPAIR_V324_20261102';S=D/'postround325';P=T/'REFERENCE324_POSTROUND_CORRECTION_V328_20261102';assert not P.exists();P.mkdir();(P/'reports').mkdir();(P/'eval_source').mkdir()
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
    with p.open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
put(P/'reports/LOCAL327_UNEXECUTED325_PARENT_LITERAL_REJECTION.json',dict(epoch=time.time(),passed=False,source=str(S/'run325_eval_once_template.py'),problem="parent generator retained .replace('246','308') while downstream target expects325",rejected_before_network=True,model_reads=0,SDK=0,physics_steps=0,original324and325INDEXunchanged=True))
def rename(text):
    keep=[]
    def h(m):keep.append(m.group());return'@SHA'+str(len(keep)-1)+'@'
    text=re.sub(r'\b[0-9a-f]{64}\b',h,text);text=re.sub(r'(?<=[A-Za-z_])325(?!\d)','328',text)
    for i,v in enumerate(keep):text=text.replace('@SHA'+str(i)+'@',v)
    return text
def write(p,text):p.parent.mkdir(parents=True,exist_ok=True);ast.parse(text);p.write_bytes(text.encode())
for path in S.rglob('*.py'):
    text=rename(path.read_text('utf8')).replace(".replace('246','308')",".replace('246','328')")
    write(P/rename(str(path.relative_to(S))),text)
script=rename((D/'postround325_finalize324_replay_eval_once.py').read_text('utf8'))
script=script.replace("N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';P=N/'postround328'", "N=Path("+repr(str(D))+");T=N.parent;R=N/'reports';P=Path(__file__).resolve().parent")
script=script.replace("(N/'INDEX328_POSTROUND_FOR324_FROZEN.json')","(P/'INDEX328_POSTROUND_FOR324_FROZEN.json')")
write(P/'postround328_finalize324_replay_eval_once.py',script)
bind=(D/'bind326_after324_first_and_launch_postround_once.py').read_text('utf8').replace('BIND326','BIND329').replace('POSTROUND325','POSTROUND328')
bind=bind.replace("N=Path(__file__).resolve().parent;R=N/'reports'", "N=Path("+repr(str(D))+");R=N/'reports'")
bind=bind.replace("path=N/'postround325_finalize324_replay_eval_once.py'","path=Path("+repr(str(P/'postround328_finalize324_replay_eval_once.py'))+")")
write(P/'bind329_after324_first_and_launch_postround_once.py',bind)
parentenv={'T':T};tree=ast.parse((P/'run328_eval_once_template.py').read_text('utf8'));main=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='main')
for stmt in main.body:
    if isinstance(stmt,ast.Assign)and any(isinstance(x,ast.Name)and x.id=='parent'for x in stmt.targets):exec(compile(ast.Module(body=[stmt],type_ignores=[]),'<fixed328parent>','exec'),parentenv)
parent=parentenv['parent'];ast.parse(parent)
assert "str(P/'source/evaluate328.py')"in parent and'from contract328 import'in parent and'RESULT328.json'in parent
files=[*sorted(P.rglob('*.py')),D/'review324_NEW_final_whole_CPU_UNUSED_once.py']
put(P/'INDEX328_POSTROUND_FOR324_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in files]))
put(P/'reports/SOURCE328_UNUSED_POSTROUND_VALIDATED.json',dict(epoch=time.time(),passed_static=True,parent328actualAST_matches=True,models=0,SDK=0,network=0,original325neverexecute=True,bind329=str(P/'bind329_after324_first_and_launch_postround_once.py'),indexSHA=H(P/'INDEX328_POSTROUND_FOR324_FROZEN.json')))
print(json.dumps(dict(passed_static=True,root=str(P),original324productionbytes_unchanged=True)))
