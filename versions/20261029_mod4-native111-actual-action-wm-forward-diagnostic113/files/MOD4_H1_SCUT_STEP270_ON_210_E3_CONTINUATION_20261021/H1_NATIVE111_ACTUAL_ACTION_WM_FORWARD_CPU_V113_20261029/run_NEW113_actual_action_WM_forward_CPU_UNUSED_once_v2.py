"""ONE new admitted CPU purpose, qualified111 checkpoint1 + NEW112 controls1.
No actor/critic forward, optimizer, GPU, SDK, physics, SSH, account or Goal.
"""
from pathlib import Path
import hashlib,json,os,sys,time,traceback
S=Path(__file__).resolve().parent;R=S/"reports"
raw_reads=0;checkpoint_decodes=0;model_hash_passes=0
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def require(v,m):
 if not bool(v):raise ValueError(m)
def put(n,v):
 with (R/n).open("x",encoding="utf8") as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 global raw_reads,checkpoint_decodes,model_hash_passes
 start=time.monotonic()
 require(os.environ.get("CUDA_VISIBLE_DEVICES")=="","explicit CPU-only environment")
 index=read(S/"FROZEN_UNUSED_SOURCE113_CPU_PURPOSE_INDEX_V2.json")
 for x in index["source_files"]:require(H(x["path"])==x["SHA"],"sealed source changed "+x["path"])
 q=read(S/"PURPOSE113_TYPED_BINDING_SOURCE_ONLY.json")
 require(H(S/"PURPOSE113_TYPED_BINDING_SOURCE_ONLY.json")==index["binding_SHA"],"binding SHA")
 require(q["formal_SHA"]=="24f94861f17b05fa4abb959946822912f07e9b2b07a49461f79aa55739d5fa12" and q["declared_horizons"]==[1,8,32],"explicit purpose model/horizons")
 B=Path(q["source_payload"]);require(H(q["manifest"])==q["manifest_SHA"],"original actual111 runtime manifest")
 for x in q["source_PY_rows"]:require(H(B/x["relative"])==x["SHA"],"original source PY")
 require(H(q["qualified111_CPU"])==q["qualified111_CPU_SHA"],"qualified formal CPU proof")
 qual=read(q["qualified111_CPU"]);require(qual["passed"] and qual["model"]["SHA"]==q["formal_SHA"] and qual["original_normal_duration_account_settled_and_allout"],"qualified model and prior closure")
 require(H(q["actual_case_report"])==q["actual_case_report_SHA"],"actual new112 case receipt")
 case=read(q["actual_case_report"]);require(case["actual_waited_exit"]==0 and case["case"]["passed"] and not case["errors"],"one actual complete frozen case")
 require(read(S/"reports/SOURCE113_REAL_CORE_SYNTHETIC_ACTION_SEQUENCE_AND_NEGATIVES_CPU_ACTUAL.json")["passed_source_CPU_only"],"source synthetic proof")
 put("NEW113_PURPOSE_CONSUMED_BEFORE_RAW_OR_MODEL_ACTUAL.json",dict(epoch=time.time(),source_index_SHA=H(S/"FROZEN_UNUSED_SOURCE113_CPU_PURPOSE_INDEX_V2.json"),maximum_control_raw_reads=1,maximum_full_checkpoint_decodes=1,normal86_separate_PT_reads=0,CPU_only=True,no_retry=True,purpose=q["purpose"]))
 import psutil,torch
 p=psutil.Process();put("NEW113_OWN_LOCAL_CPU_IDENTITY_ACTUAL.json",dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),cwd=p.cwd()))
 torch.set_num_threads(2);require(not torch.cuda.is_initialized(),"CUDA initialized before source purpose")
 sys.path[:0]=[str(S),str(B/"source")]
 from actual_action_forward113_core_v1 import decode_records,evaluate_horizon,summary
 from supermimic_wheel_leg_v3 import augmented_wheel_leg_world_model_v1 as wm_module
 from supermimic_wheel_leg_v3 import geometry as geom
 import compact_episode_static31_v1 as context
 for module,relative in [(wm_module,"source/supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py"),(geom,"source/supermimic_wheel_leg_v3/geometry.py"),(context,"source/compact_episode_static31_v1.py")]:
  require(Path(module.__file__).resolve()==(B/relative).resolve(),"actual imported module path "+relative)
 row=q["raw_control_producer"];rp=Path(row["local_path"]);before=rp.stat()
 require(before.st_size==row["bytes"],"new113 producer input bytes")
 raw_reads+=1;raw=rp.read_bytes();require(hashlib.sha256(raw).hexdigest()==row["SHA"],"new112 control producer SHA")
 require((rp.stat().st_size,rp.stat().st_mtime_ns)==(before.st_size,before.st_mtime_ns),"raw file changed")
 records=[json.loads(line) for line in raw.splitlines() if line.strip()];del raw
 data=decode_records(records);del records
 put("NEW113_TYPED_DATA_GUARDS_PASSED_BEFORE_MODEL_ACTUAL.json",dict(epoch=time.time(),raw_reads=raw_reads,rows=len(data["s"]),source_SHA=row["SHA"],private_frames_exact=True,single_time_out_episode=True,state127_action6_xi31_finite=True,actual_executed_actions_not_mean=True,context_fields_definition=context.FIELDS,input_next_terminal_continuity_max_abs_by_block={k:float(data["continuity"][a:b].max()) for k,a,b in [("position_m",0,3),("canonical_quaternion",3,7),("world_velocity_m_s",7,10),("world_angular_velocity",10,13),("q30",13,43),("dq30",43,73),("dynamic54",73,127)]},all_before_new_model_load=True,no_PhysX_or_model_read_before_this_gate=True))
 mp=Path(q["formal_local_path"]);st=mp.stat();require(st.st_size==q["formal_bytes"],"formal bytes before purpose decode")
 with mp.open("rb") as f:
  model_hash_passes+=1;digest=hashlib.file_digest(f,"sha256").hexdigest();require(digest==q["formal_SHA"],"formal full integrity before trusted checkpoint decode");f.seek(0)
  checkpoint_decodes+=1;saved=torch.load(f,map_location="cpu",weights_only=False)
 require((mp.stat().st_size,mp.stat().st_mtime_ns)==(st.st_size,st.st_mtime_ns),"formal changed")
 native=saved["UniSuperMimic_H1_test"];pub=saved["UniSuperMimic_publication"]
 require(native["iteration"]==q["expected_native_iteration"] and pub["world_updates"]==q["expected_world_updates"] and pub["policy_updates"]==q["expected_policy_updates"],"qualified111 global header")
 args=native["args"];require(args["num_joints"]==30 if "num_joints" in args else True,"native joint count")
 wm=wm_module.AugmentedWheelLegWorldModel(context_dim=31,hidden=args["wm_hidden"],num_joints=30,auxiliary_dim=54,action_dim=6)
 wm.load_state_dict(native["wm"],strict=True)
 for k,v in wm.state_dict().items():require(torch.isfinite(v).all(),"finite WM parameter/norm "+k)
 wm.eval()
 for x in wm.parameters():x.requires_grad_(False)
 frozen={k:v.detach().clone() for k,v in wm.state_dict().items()}
 del saved,native
 put("NEW113_MODEL_ONCE_DECODE_AND_WM_ONLY_FROZEN_ADMITTED_ACTUAL.json",dict(epoch=time.time(),raw_reads=raw_reads,full_checkpoint_decodes=checkpoint_decodes,source_integrity_hash_passes=model_hash_passes,source_SHA=digest,whole_checkpoint_decoded_once_only_WM_used=True,separate_normal86_PT_reads=0,no_Pi_Critic_or_optimizer_construction_or_forward=True,WM_hidden=args["wm_hidden"],CPU_torch_version=torch.__version__,producer_GPU_runtime="Torch2.10cu128 with TF32 allowed; CPU fullfloat32 results not bitwise GPU equivalence",no_CUDA_initialized=not torch.cuda.is_initialized()))
 def deadline():require(time.monotonic()-start<q["CPU_wall_budget_seconds"],"new113 CPU finite purpose budget")
 all_rows={};summaries={}
 for h in q["declared_horizons"]:
  rows=evaluate_horizon(wm,geom.unflatten_state,context.normalize_static31,data,h,batch_size=256,check_deadline=deadline)
  all_rows[str(h)]=rows;summaries[str(h)]=dict(all=summary(rows),request_only=summary([r for r in rows if r["age_for_action"]>=200]),settle_only=summary([r for r in rows if r["age_for_action"]+h<=200]),crosses_request_onset_windows=sum(r["age_for_action"]<200<=r["age_for_action"]+h-1 for r in rows))
  put("NEW113_HORIZON_"+str(h)+"_ACTUAL_ACTION_FORWARD_PREDICTIONS.json",dict(rows=rows,summaries=summaries[str(h)],horizon=h,no_policy_action_resampling=True,state_rollout_open_loop_after_real_initial_state=True))
 require(all(torch.equal(wm.state_dict()[k],v) for k,v in frozen.items()),"WM parameters/normalizers changed during inference")
 require(not torch.cuda.is_initialized(),"CUDA initialized during CPU numerical purpose")
 result=dict(epoch=time.time(),passed_execution=True,purpose=q["purpose"],raw_controls_reads=raw_reads,full_checkpoint_decodes=checkpoint_decodes,model_integrity_hash_passes=model_hash_passes,separate_normal86_checkpoint_reads=0,no_Pi_Critic_optimizer_or_training=True,WM_parameters_and_norms_literal_unchanged=True,CPU_wall_seconds=time.monotonic()-start,actual_case_control_count=2000,clock_source="actual action ages0..1999/private4096; original20s physical case already closed",summary=summaries,actual_next_world_vx_range=[float(data["t"][:,7].min()),float(data["t"][:,7].max())],actual_next_world_vx_requested_target=.5,scope="One NEW112 frozenmean lowhop trajectory; overlapping windows not independent population trials. Actual actions at everyoffset, not newpolicy actions. No27cm/highspeed extrapolation/unique root cause or new reward/SDK/GPU/GO proof. Frozen diagnostic did not train WM. CPU vs savedGPU rootZ is consistency readout, not a bitwise/tolerance admission gate.",source_model_SHA=q["formal_SHA"],all_data_and_source_gates_preceded_model=True)
 put("NEW113_ACTUAL_ACTION_WM_WORLD_X_VELOCITY_CPU_COMPLETE_ACTUAL.json",result)
 output=dict(passed=True,raw_reads=raw_reads,checkpoint_decodes=checkpoint_decodes,seconds=result["CPU_wall_seconds"],horizons={h:dict(windows=v["all"]["windows"],X_MAE_m=v["all"]["world_position_error"]["x"]["mean_abs"],Vx_MAE_m_s=v["all"]["world_velocity_error"]["x"]["mean_abs"],request_Vx_MAE=v["request_only"]["world_velocity_error"]["x"]["mean_abs"],sign_subset=v["request_only"]["significant_vx_sign_subset"]) for h,v in summaries.items()},one_step_CPU_vs_savedGPU_Z=summaries["1"]["all"]["CPU_vs_saved_GPU_one_step_root_z_max_abs"])
 print(json.dumps(output),flush=True)
if __name__=="__main__":
 try:main()
 except BaseException:
  put("NEW113_ORIGINAL_ERROR_"+str(time.time_ns())+".json",dict(epoch=time.time(),traceback=traceback.format_exc(),raw_reads=raw_reads,checkpoint_decode_attempts=checkpoint_decodes,model_integrity_hash_passes=model_hash_passes,no_retry=True,no_GPU_physics_or_account=True))
  raise

