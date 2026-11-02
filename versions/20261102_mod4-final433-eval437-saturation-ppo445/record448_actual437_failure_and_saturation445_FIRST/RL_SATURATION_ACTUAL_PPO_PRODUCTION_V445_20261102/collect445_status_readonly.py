"""One serial metadata/stdout snapshot; no model or canonical mutations."""
from pathlib import Path
import argparse,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(N))
from launch445_actual_residual_RL_once import module,SNAPSHOT,put,read

def main():
    p=argparse.ArgumentParser();p.add_argument('--label',required=True);a=p.parse_args()
    assert a.label.replace('_','').isalnum()
    name='ROOT445_STATUS_'+a.label+'.json';assert not(R/name).exists()
    assert read(R/'ROOT445_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
    patterns='collect_actual|collect_generic|PAIR|postround|E1collect|MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|prepare_archive|single_gpu|collect_nine|RMPOLAR|watch_|run339_|run342_|run_once_after_resume|watch_w35_eval_terminal|collect_attempt2_wait_and_sdk|snapshot_w35|snapshot_adaptation|deploy_w35|launch_w35|collect300_|launch300_|run303_eval|postround303_finalize|collect445_|launch445_|run301_eval|collect297_|launch297_|run299_eval|run293_eval|collect292_|launch292_|run_ROOT|collect286_|launch286_'
    query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+patterns+"' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"
    q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
    rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
    assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()and rows[0]['ExecutablePath'].replace(chr(92),'/').lower()==sys.executable.replace(chr(92),'/').lower()and rows[0]['CreationDate']
    put('ROOT445_STATUS_'+a.label+'_EXACT_CIM.json',dict(epoch=time.time(),rows=rows,lease_before='FREE'))
    task=read(N/'TASK445_FROZEN.json')
    sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
    transport=previous=client=secret=None
    try:
        transport,previous=module('status445_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install()
        secret=module('status445_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover()
        client=d.connect72(secret);secret=None
        result=d.code(client,d.PY72,SNAPSHOT,dict(job=task['job_root'],owner=task['owner_root']),timeout=60)
        put(name,result)
        selected={Path(r['path']).name:json.loads(r['UTF8']) for r in result['full_selected_UTF8']}
        print(json.dumps(dict(report=str(R/name),files=list(selected),
          GO=selected.get('GO_PRODUCTION.json'),first=selected.get('FIRST_ACTUAL_TEACHER_DEPTH_STUDENT445_UPDATE.json'),
          progress=selected.get('LATEST_PROGRESS.json'),worker_error=selected.get('ORIGINAL_ERROR.json'),
          node_error=selected.get('NODE_ORIGINAL_ERROR.json'),owner_error=selected.get('OWNER_ORIGINAL_ERROR.json'),
          terminal=selected.get('NODE_TERMINAL_ACTUAL.json'),stdout_tail=(result.get('original_stdout')or{}).get('UTF8','')[-2200:])),flush=True)
    finally:
        secret=None
        if client is not None:client.close();client=None
        if transport is not None:transport.SESSION=previous
        put('ROOT445_STATUS_'+a.label+'_SSH_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':main()
