from pathlib import Path
import time,json,ast
N=Path(__file__).resolve().parent
def main():
 from stdin_only_finite_launch_v1 import launch
 dummy='non-runtime-capability-fixture-only';calls=[]
 def fake(c,py,source,*args):calls.append(dict(py=py,source=source,args=args));ast.parse(source);return dict(fixture_only=True)
 result=launch(fake,None,'python','/owned/case','finite_entry.py',dict(role='owner',token=dummy));assert result['fixture_only'] and len(calls)==1 and not calls[0]['args'] and dummy in calls[0]['source'];assert "subprocess.run(['python','-u','-B'" in calls[0]['source'] and 'input=cfg+chr(10)' in calls[0]['source']
 out=dict(epoch=time.time(),passed_future_launch_CPU_fixture_only=True,original_actual_temporary_launcher_had_CFG_in_remote_argument=True,actual_current_owner_and_node_CFG_then_read_via_stdin=True,original_claim_never_argv_for_this_N_stage_rejected=True,old_sources_and_original_errors_preserved=True,no_actual_capability_value_in_this_report_or_fixture_or_Git=True,no_claim_OS_process_creation_audits_absent=True,current_finite_jobs_not_restarted_or_rotated_for_archive=True,current_capability_only_valid_for_current_finite_run_and_endpoint=True,future_new_launcher_entire_configuration_in_SSH_stdin_and_child_stdin_no_CFG_argument=True,requires_future_dispatcher_use_new_launch_helper=True,no_GPU_optimizer_budget_or_current_worker_mutation=True)
 p=N/'reports/TEMPORARY_LAUNCHER_ARGV_CAPABILITY_EXPOSURE_DISCLOSURE_AND_FUTURE_STDIN_FIX_CPU_ACTUAL.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out),flush=True)
if __name__=='__main__':main()
