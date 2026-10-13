from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;p=D/'deploy_selected_production_once.py';tree=ast.parse(p.read_text(encoding='utf8'))
main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main');assign=next(x for x in main.body if isinstance(x,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='code' for k in x.targets))
R='C:/Users/Win10/Documents/MOD4_WAVE50_WINDOWS_4090_20261013';old=R+'/capacity512_own128_expanded_benchmark_v2_20261013';new=R+'/CPU_compile_fixture_only';n=512;source=dict(path='C:/CPU_PREPARED_ONLY.pt',sha256='0'*64)
code=eval(compile(ast.Expression(assign.value),'<generate_cpu_compile_only>','eval'),dict(R=R,old=old,new=new,n=n,source=source,case="CPU_compile_fixture"));parsed=ast.parse(code)
start=next(i for i,x in enumerate(parsed.body) if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='p' for y in x.targets) and 'temporary_parent' in ast.unparse(x));end=next(i for i,x in enumerate(parsed.body) if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='mf' for y in x.targets))
fixture=D/'PRODUCTION_PARENT_CPU_COMPILE_FIXTURE';assert not fixture.exists();(fixture/'payload').mkdir(parents=True)
src=D/'CAPACITY512_COMPLETED_INPUTS_1791896907514283900/payload/temporary_parent.py';dest=fixture/'payload/temporary_parent.py';dest.write_bytes(src.read_bytes())
exec(compile(ast.Module(parsed.body[start:end],type_ignores=[]),'<parent_transformation_only>','exec'),dict(new=fixture))
actual=dest.read_text(encoding='utf8');assert "for phase in ('train',):" in actual and 'capacity_error_seen' in actual and 'request_own_save_stop_no_kill=True' in actual
compile(actual,str(dest),'exec')
q=D/'reports/PRODUCTION_BUILDER_CPU_PREPARED_ACTUAL.json';assert not q.exists();q.write_text(json.dumps(dict(epoch=time.time(),passed_CPU_compile_only=True,builder_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),generated_CPU_fixture_parent_SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),train_only_no_old_native_fullrestore_replay=True,own_PhysX_error_save_stop_not_kill=True,actual_GPU_production_not_yet_launched=True),indent=2),encoding='utf8');print(str(q))
