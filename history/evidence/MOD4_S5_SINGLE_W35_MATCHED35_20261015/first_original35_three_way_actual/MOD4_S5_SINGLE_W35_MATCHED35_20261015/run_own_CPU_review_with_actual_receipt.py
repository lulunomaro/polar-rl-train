"""Persist original CPU reader stdout/error without replaying any GPU case."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,time
D=Path(__file__).resolve().parent;R=D/'reports'
def main():
 p=argparse.ArgumentParser();p.add_argument('--script',required=True);p.add_argument('args',nargs='*');a=p.parse_args();source=D/a.script
 assert source.parent==D and source.name in ('review_s5_single35_own_physical_actual_CPU.py','review_s5_single35_actual_source_history_CPU.py','review_s5_single35_full1500_original_route_prefix_CPU_actual.py','review_s5_first35_matched_three_configurations_CPU.py')
 env=dict(os.environ,CUDA_VISIBLE_DEVICES='');cmd=['C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe','-X','utf8',str(source),*a.args]
 run=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',env=env)
 v=dict(epoch=time.time(),script=str(source),source_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),argv=cmd,actual_exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr,no_GPU_SSH_PPO_or_budget=True,failed_reader_not_qualified_as_physical_failure=run.returncode!=0)
 out=R/('OWN_CPU_REVIEW_'+('PASSED_' if run.returncode==0 else 'ORIGINAL_ERROR_')+str(time.time_ns())+'.json');out.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(receipt=str(out),exit_code=run.returncode,stdout=run.stdout)));raise SystemExit(run.returncode)
if __name__=='__main__':main()
