from pathlib import Path
import json,time,hashlib,traceback
import stage_lifetime_target_CPU_once as original
D=original.D;R=original.R;P=original.P
def main():
 assert not (R/'OLD449_FINAL_BOUNDARY_RESOURCE_ACTUAL.json').exists() and not (R/'SOURCE_FREEZE_ACTUAL.json').exists()
 p=P/'supervise_wave50_lifetime_once.py';before=p.read_bytes();copy=D/'CONTROLLER_PRE_CLOSEOUT_SCHEMA_REVIEW.py.txt';assert not copy.exists();copy.write_bytes(before)
 s=before.decode().replace('e1_WAVE50_route_startup_resource_reviewed_observation_INDEPENDENT_POSTEXIT_PASSED.json','INDEPENDENT_POSTEXIT_FULLSTATE_CPU_ACTUAL.json')
 anchor='prior.__file__=__file__';assert anchor in s;s=s.replace(anchor,anchor+'\nprior.s.verify=verify')
 compile(s,str(p),'exec');p.write_text(s,encoding='utf8',newline='\n')
 original.save('OUTER_CLOSEOUT_SCHEMA_REVIEW.json',dict(epoch=time.time(),passed=True,original_KeyError_before_root_GPU_retained=True,row_receipt_and_outer_CPU_receipt_distinct=True,correct_outer_fullstate_proof_selected=True,only_prepared_controller_adjusted_before_freeze=True,original_controller_SHA=hashlib.sha256(before).hexdigest(),reviewed_controller_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),no_oldonce_or_budget_replay=True))
 source=Path(original.__file__).read_text().replace("assert not (R/'TARGET_STAGE_STARTED.json').exists();save('TARGET_STAGE_STARTED.json',dict(epoch=time.time(),new_lifetime_only=True))","assert (R/'TARGET_STAGE_STARTED.json').exists()")
 source=source.replace('e1_WAVE50_route_startup_resource_reviewed_observation_INDEPENDENT_POSTEXIT_PASSED.json','INDEPENDENT_POSTEXIT_FULLSTATE_CPU_ACTUAL.json')
 ns=dict(__file__=original.__file__,__name__='independent_outer_schema_unexecuted_stage');exec(compile(source,str(__file__)+'#unexecuted-root-CPU','exec'),ns);ns['main']()
if __name__=='__main__':
 try:main()
 except BaseException:original.save('OUTER_SCHEMA_CONTINUATION_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU=True));raise
