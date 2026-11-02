"""Read-only artifact checks and final metadata; no solver/test/compiler invocation."""
from pathlib import Path
import hashlib,json,re,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
FINAL='SEALED_NEW_NATIVE_POWER_MATH_HOST_CPP_AND_SEPARATE_ARM_OBJECT_FACTS'
PRIMARY=['pa1_allocator.c','pa1_allocator.h','MODEL_CONTRACT.json','NUMERICAL_BUDGET.json','COMPARISON_02.json','HOST_BUILD_02.json','ARM_BUILD_01.json','OBJECT_SUMMARY.json','CORE_RECEIPT.json','HOST_QUALIFICATION.json','ANALYSIS_RECEIPT.json','README.md','ERROR_REPORT.md','pa1_source_bundle.zip','SOURCE_FREEZE.json']
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(n):return json.loads((HERE/n).read_bytes())
def put(n,v,exclusive=False):
    with(HERE/n).open('x'if exclusive else'w',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
def rec(p):return dict(path=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def main():
    assert not(HERE/'INDEX.json').exists()and not(HERE/'MANIFEST.json').exists()and not(HERE/'VALIDATION.json').exists()
    freeze=load('SOURCE_FREEZE.json');prereg=load('PREREGISTRATION_RECEIPT.json')
    assert len(freeze['old_files'])==1151 and len(freeze['source_references'])==26 and len(freeze['model_assets'])==279
    for key in ('old_files','source_references','model_assets','preregistered'):
        for r in freeze[key]:
            p=Path(r['path']);assert p.is_file()and p.stat().st_size==r['bytes']and sha(p)==r['sha256'],str(p)
    assert sha(HERE/'NUMERICAL_BUDGET.json')==prereg['budget_SHA']and sha(HERE/'MODEL_CONTRACT.json')==prereg['contract_SHA']
    comparison=load('COMPARISON_02.json');failed=load('COMPARISON_01.json');analysis=load('ANALYSIS_RECEIPT.json');host=load('HOST_BUILD_02.json');arm=load('ARM_BUILD_01.json');obj=load('OBJECT_SUMMARY.json');hq=load('HOST_QUALIFICATION.json')
    assert comparison['numerical_failures']==comparison['native_failures']==0 and comparison['CPP_pass']and comparison['cases']==219
    assert comparison['numerical_checks']==38508 and comparison['native_checks']==2290 and comparison['clock_insertion_rows']==36
    assert failed['numerical_failures']==3 and failed['native_failures']==1 and not failed['CPP_executed']
    assert analysis['only_changed_build_input']==['pa1_allocator.c']and len(analysis['raw_numeric_bit_changes'])==3 and analysis['exact_source_reversal_restores_first']
    assert sha(HERE/'analyze_pa1.py')==analysis['analyzer_SHA']
    for i in (1,2):
        build=load(f'HOST_BUILD_{i:02d}.json');folder=HERE/f'host_attempt_{i:02d}'
        for n,h in build['sources'].items():assert sha(folder/n)==h
        if i==2:
            for n,h in build['sources'].items():assert sha(HERE/n)==h
            assert all(c['exit_code']==0 for c in build['commands'])
        for c in build['commands']:
            if 'artifact'in c:assert Path(c['artifact']).stat().st_size==c['bytes']and sha(c['artifact'])==c['sha256']
            if 'raw_sha256'in c:assert sha(c['raw_output'])==c['raw_sha256']
        comp=load(f'COMPARISON_{i:02d}.json');assert sha(HERE/f'C_RUNS_{i:02d}.jsonl')==comp['raw_SHA']
    assert host['success']and arm['success']and all(c['exit_code']==0 for c in arm['commands'])and len(obj['objects'])==2
    for n,h in arm['sources'].items():assert sha(HERE/n)==h and sha(HERE/'arm_attempt_01'/n)==h
    for r in obj['objects']:
        assert sha(r['object'])==r['sha256']and r['source_SHA']==sha(HERE/'pa1_allocator.c')and not r['writable_allocated_sections']and r['target_execution']==0 and not r['helper_libm_binding']
    assert 'actual_extern_C=PASS'in(HERE/'cpp_run_02.log').read_text()and 'checks=2290 failures=0'in(HERE/'native_run_02.log').read_text()
    assert 'checks=2290 failures=1'in(HERE/'native_run_01.log').read_text()and not(HERE/'cpp_run_01.log').exists()
    assert hq['actual_CPP_extern_C_pass']and hq['physics_steps']==0 and hq['ARM_execution']==0
    with zipfile.ZipFile(HERE/'pa1_source_bundle.zip')as z:
        assert z.namelist()==['pa1_allocator.c','pa1_allocator.h','BUILD.txt','MODEL_CONTRACT.json','NUMERICAL_BUDGET.json']
        assert all(hashlib.sha256(z.read(n)).hexdigest()==sha(HERE/n)for n in z.namelist())
    discovered=set()
    for line in(HERE/'DISCOVERED_FILES.txt').read_text(encoding='utf-8-sig').splitlines():
        if not line.strip():continue
        p=Path(line.strip());p=p if p.is_absolute()else ROOT/p;p=p.resolve();assert p.is_relative_to(HERE)and p.is_file();discovered.add(p)
    discovered.update((HERE/n).resolve()for n in ('DISCOVERED_FILES.txt','MANIFEST.json','INDEX.json','VALIDATION.json'))
    assert all((HERE/n).resolve()in discovered for n in PRIMARY)
    put('MANIFEST.json',dict(scope=FINAL,primaries=[rec(HERE/n)for n in PRIMARY],primary_count=len(PRIMARY)),True)
    put('INDEX.json',dict(status='PENDING_INDEX_COMPLETION'),True);put('VALIDATION.json',dict(status='PENDING_INDEX_COMPLETION'),True)
    links=[]
    for p in sorted(discovered):
        if p.parent!=HERE or p.suffix.lower()!='.md':continue
        text=p.read_text(encoding='utf-8')
        for target in re.findall(r'\[[^\]]*\]\(<([^>]+)>\)',text):
            path=target.split('#',1)[0]
            if not path:continue
            resolved=(p.parent/path).resolve();assert resolved.is_file(),(str(p),target)
            links.append(dict(source=p.name,target=target))
    validation=dict(status=FINAL,valid=True,old_files_unchanged=1151,source_references_unchanged=26,model_assets_unchanged=279,preregistration_unchanged=True,first_failed_attempt_preserved=True,fixture_case_count=219,canonical_numerical_checks=38508,canonical_native_checks=2290,canonical_failures=0,actual_CPP_extern_C=True,logical_clock_insertions=36,ARM_objects=2,ARM_execution=0,default_real_calibration='UNBOUND_INVALID',electrical_thermal_battery_HIL_stability_qualified=False,target_libm_BSP_FPSCR_stack_WCET_qualified=False,C3_final_enqueue_or_robot_MPC_qualified=False,physics_steps=0,GPU=False,Git=False,new_agents=False,parent_goal_changed=False,blocked_IO_changed_or_run=False,PH4_cutoff_excludes_component=True,PH5_and_later_pending=True,indexed_files=len(discovered),live_markdown_links=len(links))
    put('VALIDATION.json',validation)
    files=[]
    for p in sorted(discovered,key=lambda p:p.relative_to(HERE).as_posix()):
        assert p.is_file()
        if p.name in ('INDEX.json','seal_01.log')and p.parent==HERE:files.append(dict(path=p.relative_to(HERE).as_posix(),bytes=None,sha256=None,reason='self index or final streaming seal log'))
        else:files.append(rec(p))
    put('INDEX.json',dict(status=FINAL,files=files,links=links,inventory_source='host glob complete spilled list; explicit metadata additions only',scope='new component only; old files remain read-only'))
    for r in load('INDEX.json')['files']:
        if r['sha256']is not None:assert sha(HERE/r['path'])==r['sha256']and(HERE/r['path']).stat().st_size==r['bytes']
    for r in load('MANIFEST.json')['primaries']:assert sha(HERE/r['path'])==r['sha256']
    print(json.dumps(dict(status=FINAL,files=len(files),links=len(links),old_files_unchanged=1151,source_references_unchanged=26,model_assets_unchanged=279,README_SHA=sha(HERE/'README.md'),INDEX_SHA=sha(HERE/'INDEX.json'),source_bundle_SHA=sha(HERE/'pa1_source_bundle.zip'),core_SHA=sha(HERE/'pa1_allocator.c'),no_test_or_compile_rerun=True,physics_steps=0),indent=2))
if __name__=='__main__':main()
