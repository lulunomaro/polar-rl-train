"""Retain the consumed native and failed coordinator; prepare only 29 unused cases."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import time
import traceback

D=Path(__file__).resolve().parent
R=D/'reports'
CASE='s5_nominal_s20261002_single_eval_flat_120_v1'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert (R/'NOMINAL_ABC_FIXED30_ORIGINAL_ERROR.json').exists()
    cmd='$p=Get-CimInstance Win32_Process -Filter "ProcessId = 34592";$p|Select-Object ProcessId,CreationDate,CommandLine|ConvertTo-Json -Compress'
    ci=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True,encoding='utf8',check=True)
    assert not ci.stdout.strip() or json.loads(ci.stdout) in (None,[])
    data=R/(CASE+'_ORIGINAL_PHYSICAL_CPU_REVIEW_V2.json');source=R/(CASE+'_S5_SINGLE_CONTROL_CPU_ADMITTED.json')
    v=json.loads(data.read_bytes())['result'];s=json.loads(source.read_bytes())
    assert v['steps']==120 and v['num_envs']==80 and v['profile']=='nominal' and v['data']['complete_data_contract']
    assert s['passed'] and s['source9_STD_initial_final_exact'] and s['callbacks']==480
    old=(D/'run_nominal_ABC_fixed30_case_batch_once.py').read_text(encoding='utf8')
    new=old.replace('NOMINAL_ABC_FIXED30','NOMINAL_ABC_REMAINDER29')
    new=new.replace('--execute-root-fixed30-new-nominal-cases','--execute-root-remainder29-unused-only')
    new=new.replace('a.execute_root_fixed30_new_nominal_cases','a.execute_root_remainder29_unused_only')
    new=new.replace('review_nominal_original_physical_and_metrics_CPU.py','review_nominal_original_physical_and_metrics_CPU_v2.py')
    new=new.replace("case+'_ORIGINAL_PHYSICAL_CPU_REVIEW.json'","case+'_ORIGINAL_PHYSICAL_CPU_REVIEW_V2.json'")
    before="   an=consume(seed,'single_eval',kind,120);completed.append(an);single=consume(seed,'single_eval',kind,1500,an);completed.append(single)"
    after="""   if seed==20261002 and kind=='flat':
    an=json.loads((R/'NOMINAL_REMAINDER29_RETAINED_NATIVE_CPU_ADMISSION_ACTUAL.json').read_bytes())['retained_native']
    assert H(an['data'])==json.loads((R/'NOMINAL_REMAINDER29_RETAINED_NATIVE_CPU_ADMISSION_ACTUAL.json').read_bytes())['physical_V2_SHA']
    assert json.loads(Path(an['data']).read_bytes())['result']['data']['complete_data_contract']
    assert json.loads(Path(an['routing']).read_bytes())['source9_STD_initial_final_exact']
   else:
    an=consume(seed,'single_eval',kind,120)
   completed.append(an);single=consume(seed,'single_eval',kind,1500,an);completed.append(single)"""
    assert before in new;new=new.replace(before,after)
    new=new.replace("plan='perkind single native120+full1500, gate native120, rulefull1500+gatefull1500, actual3way initialpairs; 30newcases total'",
        "plan='Retain first complete native120; execute only29unused cases (11native+18full) withV2reader, samekind3pair beforecredit',retained_native_case='"+CASE+"',original_failed_coordinator34592_CIM_absent_before_handoff=True")
    new=new.replace('all30_closed_and_CPU_admitted=True,','all30_closed_and_CPU_admitted=True,new_cases_this_coordinator=29,reused_complete_native_cases=1,')
    script=D/'run_nominal_ABC_unused_remainder29_after_reader_fix_once.py'
    assert not script.exists();ast.parse(new);script.write_text(new,encoding='utf8')
    current=json.loads(sorted(R.glob(CASE+'_CURRENT_ACTUAL_*.json'))[-1].read_bytes())
    attempt=Path(next(x['local_path'] for x in current['collected_files'] if x['relative'].endswith('/PARENT_EXIT_RECEIPT.json'))).parent
    retained=dict(case=CASE,seed=20261002,profile='nominal',mode='single_eval',kind='flat',steps=120,
        attempt=str(attempt),boundary=str(R/(CASE+'_INDEPENDENT_BOUNDARY.json')),data=str(data),routing=str(source))
    value=dict(epoch=time.time(),passed=True,retained_native=retained,physical_V2_SHA=H(data),source_CPU_SHA=H(source),
        old34592_actual_CIM_absent=True,actual_CIM_command=cmd,actual_CIM_stdout=ci.stdout,
        source9_STD_all_saved_CPU_means_history_reset_passed=True,original_failed_coordinator_and_V1_TypeError_preserved=True,
        fix_only_local_optional_None_reader_no_runtime_or_GPU_source_changes=True,
        no_old_GPU_case_Task_lease_or_collection_replayed=True,next_fixed_unused_cases=29,
        remainder_script_SHA=H(script),no_PPO_or_budget=True)
    with (R/'NOMINAL_REMAINDER29_RETAINED_NATIVE_CPU_ADMISSION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
    launch=(D/'launch_nominal_ABC_fixed30_hidden_once.py').read_text(encoding='utf8')
    launch=launch.replace('NOMINAL_ABC_FIXED30','NOMINAL_ABC_REMAINDER29')
    launch=launch.replace('run_nominal_ABC_fixed30_case_batch_once.py',script.name)
    launch=launch.replace('--execute-root-fixed30-new-nominal-cases','--execute-root-remainder29-unused-only')
    launch=launch.replace('fixed_native12_full18_only=True','fixed_new_native11_full18_only=True,retained_native1_not_replayed=True')
    launch=launch.replace('new_finite30_exclusive_transport_owner_started=True','new_remainder29_exclusive_transport_owner_started=True')
    launch=launch.replace('started_finite30=True','started_remainder29=True')
    lp=D/'launch_nominal_unused_remainder29_hidden_once.py'
    assert not lp.exists();ast.parse(launch);lp.write_text(launch,encoding='utf8')
    print(json.dumps(dict(prepared_remainder29_only=True,retained_native_CPU_passed=True,old_coordinator_absent=True,no_GPU_replay=True)))


if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('NOMINAL_REMAINDER29_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(),no_GPU_network_PPO_budget=True,partial_preparation_not_replayed=True),f,indent=2)
        raise
