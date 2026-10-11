"""Use previously admitted external task-asset snapshot schema, retain broad-reader failure."""
from pathlib import Path
D=Path(__file__).resolve().parent
s=(D/'complete_cpu_fixture_explicit_assignment_view_once.py').read_text()
anchor="s=s.replace(anchor,\"code=code.replace('import test_wave50_entry_target_cpu as test',prefix+\"+repr(sub)+\")\")"
assert s.count(anchor)==1
extra='''\ns=s.replace("code=blocks[0].replace('ROOT_TOKEN',repr(ROOT))", "code=blocks[0].replace('ROOT_TOKEN',repr(ROOT));code=code.replace(\\\"and not (own.CODE/a.value).is_file():missing.append(a.value)\\\",\\\"and a.value not in ('import_contract.json','robot_cfg.py') and not (own.CODE/a.value).is_file():missing.append(a.value)\\\")")'''
s=s.replace(anchor,anchor+extra)
exec(compile(s,'<actual-external-asset-missing-CPU-reader>','exec'),{'__file__':str(D/'complete_cpu_fixture_explicit_assignment_view_once.py'),'__name__':'__main__'})
