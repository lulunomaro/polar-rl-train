"""NEW concrete purpose: distinguish lack of approach drive from wheel/step-face blockage.
Only already-returned NEW112 geometry/contact/processed-queue frames; no old raw/model/runtime.
"""
from pathlib import Path
import json,math,time,statistics
S=Path(__file__).resolve().parent;R=S/"reports"
m=json.loads((R/"FROZEN112_CASE_FULL_TEXT_AND_NEW_RAW_TRANSFER_ACTUAL.json").read_bytes())
row=next(x for x in m["rows"] if x["relative"]=="case/episode/ACTUAL_400HZ_31BODY_FRAMES.jsonl")
front=[];back=[];processed=[];near=[];rootx=[];wheel_norm=[];end_vx=[]
with Path(row["local_path"]).open(encoding="utf8") as f:
 for line in f:
  x=json.loads(line);k=x["physics_callback"]
  if not k:continue
  z=x["state"];g=z["metrics"]
  if not g["wheel_cache_available"]:continue
  fg=g["wheel_front_edge_gap_m"];bg=g["wheel_rear_edge_gap_m"]
  front.append(fg);back.append(bg);rootx.append(z["root13_sdk_xyzw"][0])
  if k%4==0 and k>=804:
   processed.append(z["physical_applied_processed6"]);end_vx.append(z["root13_sdk_xyzw"][7])
  if min(fg)<=0:
   near.append(dict(callback=k,front_gap2_m=fg,bottom2_m=g["wheel_bottom_above_floor_m"],world_vx=z["root13_sdk_xyzw"][7],processed6=z["physical_applied_processed6"]))
assert len(front)==8000
def stats(v):return dict(min=min(v),max=max(v),mean=statistics.fmean(v),mean_absolute=statistics.fmean(abs(x) for x in v))
value=dict(epoch=time.time(),purpose="NEW112 exact wheel front-gap and actual processed PD queue hypothesis check; prior body-root<.35 alone does not establish whether wheels reached the step face.",source=row,local_new112_returned_only=True,one_additional_targeted_raw_pass_for_mechanical_blockage_not_stats_or_Git=True,no_PT_model_oldcase_or_physics_rerun=True,physics_callbacks=len(front),anywheel_front_crossing_plane_callbacks=len(near),bothwheel_front_crossing_plane_callbacks=sum(max(x)<=0 for x in front),closest_any_front_gap_m=min(min(x) for x in front),closest_both_front_gap_m=min(max(x) for x in front),front_gap2_bounds=[stats([x[i] for x in front]) for i in range(2)],rear_gap2_bounds=[stats([x[i] for x in back]) for i in range(2)],first_cross_examples=near[:3],last_cross_examples=near[-3:],request_control_terminal_processed6=[stats([x[i] for x in processed]) for i in range(6)],processed_units="first4 actual leg-position targets rad; last2 actual wheel velocity targets rad/s, original physics queue actuator order retained",request_world_vx=stats(end_vx),contact_pair_scope="Net force vectors do not identify individual floor/step/internal pairs; no unique face-collision cause inferred.",coarse_body_position_interpretation_corrected=True)
with (R/"NEW112_ACTUAL_WHEEL_FRONT_GAP_AND_PROCESSED_QUEUE_BLOCKAGE_PURPOSE_ACTUAL.json").open("x",encoding="utf8") as f:json.dump(value,f,indent=2,allow_nan=False)
print(json.dumps({k:value[k] for k in ["anywheel_front_crossing_plane_callbacks","bothwheel_front_crossing_plane_callbacks","closest_any_front_gap_m","closest_both_front_gap_m","request_control_terminal_processed6","request_world_vx"]},indent=2))

