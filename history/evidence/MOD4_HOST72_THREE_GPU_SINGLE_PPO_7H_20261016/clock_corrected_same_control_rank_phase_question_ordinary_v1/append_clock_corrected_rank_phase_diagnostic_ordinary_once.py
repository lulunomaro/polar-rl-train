"""One ordinary supplement for the human slow-rank question; live runtime untouched."""
from pathlib import Path
import importlib.util,json,time,traceback
D=Path(__file__).resolve().parent;R=D/'reports';BASE='90c5795bc19d28cd57a51a4af115e5fe9a31cc4a'
def main():
 s=importlib.util.spec_from_file_location('existing_throughput_append_pure',D/'append_current_throughput_snapshot_ordinary_once.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 assert m.git('rev-parse','HEAD')==BASE and not m.git('status','--porcelain')
 p=R/'CLOCK_CORRECTED_SAME_CONTROL_SLOW_RANK_QUESTION_INTERPRETATION_ACTUAL.json';assert not p.exists()
 x=json.loads((R/'RANK_SAME_CONTROL_CLOCK_OFFSET_PHASE_READONLY_ACTUAL.json').read_bytes());assert x['same_control_steps'];rows={r['rank']:r for n in x['nodes'] for r in n['rows']}
 gaps={str(i):rows[i]['health_local_epoch_estimate']-rows[0]['health_local_epoch_estimate'] for i in (1,2)}
 assert all(v>0 for v in gaps.values())
 v=dict(epoch=time.time(),question='Is original host210 RTX4090 the slowest rank?',observed_control_steps=rows[0]['controls'],callbacks_per_rank=rows[0]['callbacks'],rank_map={'0':'original host210 RTX4090','1':'host72 GPU0','2':'host72 GPU1'},
  corrected_host72_arrival_later_than_rank0_seconds=gaps,
  clock_estimate_combined_halfwidth_s={str(i):rows[i]['offset_halfwidth_s']+rows[0]['offset_halfwidth_s'] for i in (1,2)},
  interpretation='At this same physical-control boundary rank0 arrived first; ranks1/2 on host72 arrived roughly 10.7/11.2 seconds later. Evidence contradicts original210 being the slowest sampler in this observed window.',
  limits=['One periodically recorded rollout boundary, not a rank-wise averaged CUDA/NCCL profile.','Current SSH date-offset bounds assume no intervening wall-clock step since the saved health epoch.','Does not isolate GPU hardware versus shared host CPU/NUMA, other workloads or software/communication effects.','Ranks1/2 existing logs do not publish per-iteration collection/learning metrics; absence is logger behavior, not a runtime failure.','Rank0 learning timer includes GAE, PPO compute, collective synchronization and waiting; it does not demonstrate rank0 is the slowest GPU.'],
  own_health_at_boundary={str(i):{k:rows[i][k] for k in ('ordinary','integrity','unknown','nonfinite','STOP')} for i in rows},
  same_seven_hour_training_continues_no_restart_hotpatch_signals_resource_config_or_other_job_actions=True)
 p.write_text(json.dumps(v,indent=2),encoding='utf8')
 src=(D/'append_current_throughput_snapshot_ordinary_once.py').read_text(encoding='utf8')
 src=src.replace("BASE='5e9c0ca47bf4a34ffbd5e2912e6b3385deecafe5'",'BASE='+repr(BASE))
 src=src.replace("/'shared_PPO_throughput_live_question_actual_ordinary_v1'","/'clock_corrected_same_control_rank_phase_question_ordinary_v1'")
 src=src.replace("/'real_shared_update1_three_full_models_CPU_and_active_7h_ordinary_v1/REPORT_CAPTURE_INDEX.json'","/'three_GPU_scaling_efficiency_phase_and_link_readonly_actual_ordinary_v1/REPORT_CAPTURE_INDEX.json'")
 src=src.replace('Append current shared-PPO throughput snapshot, installed logger units and wall-rate distinction','Append clock-corrected same-control rank arrival diagnosis and attribution limits')
 src=src.replace("if __name__=='__main__':","if __name__=='__unused__':")
 scope={'__file__':str(D/'append_current_throughput_snapshot_ordinary_once.py'),'__name__':'rank_phase_append_once_implementation'}
 exec(compile(src,str(Path(__file__)),'exec'),scope);scope['main']()
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('RANK_PHASE_ORDINARY_APPEND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),resume_existing_objects_no_duplicate_commit_record_tag_or_runtime=True),f,indent=2)
  raise
