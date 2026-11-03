"""Prepare two NEW CPU-only purposes; no remote/model/SDK/canonical operations.
V2 is a deliberate unchanged-loader alias control (expected remote RC1 after all
14 negatives); V3 alone selects the whole-ingress-copy loader.
"""
from pathlib import Path
import ast,copy,hashlib,json
R=Path(__file__).resolve().parent;S=R/'source_quality_microtrain_resume_alias_v2';report=R/'reports/RESUME_ALIAS_CPU_V2_V3_CALLERS_SOURCE_V1.json';assert not report.exists()
pins={
 'test_quality_microtrain_torch_cpu_v2.py':(37148,'44bbf55bbf8631fbc748be010c96610b2fb3fe91efdfad0906c85818ec6c05dd'),
 'test_quality_microtrain_torch_cpu_v3.py':(37133,'98329d9f224b368535904b1788fc9f27158cdb42553f420c0bdc9f0ef9f07e02'),
 'ctx_reward_full_resume_candidate_v3.py':(36941,'20fd4945a0f2345c17505316560ae6d358fcce147c6988f62a08d867e084e749')}
for name,pin in pins.items():
 raw=(S/name).read_bytes();assert (len(raw),hashlib.sha256(raw).hexdigest())==pin;ast.parse(raw)
oldcore=ast.parse((R/'source_resume_runtime_v2/ctx_reward_full_resume_candidate_v2.py').read_bytes());newcore=ast.parse((S/'ctx_reward_full_resume_candidate_v3.py').read_bytes());trim=copy.deepcopy(newcore);imports=[n for n in trim.body if isinstance(n,ast.Import)and any(a.name=='copy'for a in n.names)];assert len(imports)==1;trim.body.remove(imports[0]);cls=next(n for n in trim.body if isinstance(n,ast.ClassDef)and n.name=='ContextRewardLearner');load=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='load_full_checkpoint');assert ast.dump(load.body[0])==ast.dump(ast.parse('payload=copy.deepcopy(payload)').body[0]);load.body.pop(0);assert ast.dump(trim)==ast.dump(oldcore)
template=(R/'run_quality_microtrain_torch_cpu_v1_once.py').read_text(encoding='utf-8');rows=[]
for version in (2,3):
 name=f'run_quality_microtrain_torch_cpu_v{version}_once.py';dest=R/name;assert not dest.exists()
 text=template.replace('test_quality_microtrain_torch_cpu_v1.py',f'test_quality_microtrain_torch_cpu_v{version}.py').replace('source_quality_microtrain_torch_validation_v1/', 'source_quality_microtrain_resume_alias_v2/').replace('753cf898edbf9015349509cd7e67d4086dbedb80828bb146d88bbc58c2ab74be',pins[f'test_quality_microtrain_torch_cpu_v{version}.py'][1]).replace('QUALITY_MICROTRAIN_TORCH_CPU_V1',f'QUALITY_MICROTRAIN_TORCH_CPU_V{version}').replace('QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V1.json',f'QUALITY_MICROTRAIN_TORCH_CPU_RECEIPT_V{version}.json').replace('ACTUAL_CPU_SOFTWARE_A1_LEGACY_MICROTRAIN_FULL_RESUME_V1',f'ACTUAL_CPU_SOFTWARE_A1_LEGACY_MICROTRAIN_FULL_RESUME_V{version}')
 if version==3:
  text=text.replace('ctx_reward_full_resume_candidate_v2.py','ctx_reward_full_resume_candidate_v3.py').replace('source_resume_runtime_v2/ctx_reward_full_resume_candidate_v3.py','source_quality_microtrain_resume_alias_v2/ctx_reward_full_resume_candidate_v3.py').replace('8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac',pins['ctx_reward_full_resume_candidate_v3.py'][1]).replace('whole_loader_core_811_unchanged=True','whole_loader_core_811_unchanged=False,whole_ingress_copy_core_v3=True')
  gate="control=json.loads((R/'reports/QUALITY_MICROTRAIN_TORCH_CPU_V2.json').read_bytes());cr=control.get('receipt')or{};assert control['returncode']==1 and cr.get('counter_3_to_5_actual_path_passed')is True and cr.get('negative_case_count')==14 and cr.get('whole_CPU_source_strict_check_passed')is False and not cr.get('unhandled_error'),'Original-loader alias control must finish all 14 negatives before V3'\n"
  text=text.replace('paths={',gate+'paths={',1)
 ast.parse(text);dest.write_text(text,encoding='utf-8',newline='\n');raw=dest.read_bytes();rows.append(dict(path=str(dest),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),new_purpose_version=version,expected_remote_returncode=1 if version==2 else 0))
value=dict(kind='NEW_CPU_ONLY_ALIAS_CONTROL_AND_WHOLE_COPY_CALLER_SOURCES',files=rows,source_pins=pins,protected_core_AST_equal_after_only_two_additions=True,remote_SDK_PT_C_GO_or_native_operations=0)
report.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2))
