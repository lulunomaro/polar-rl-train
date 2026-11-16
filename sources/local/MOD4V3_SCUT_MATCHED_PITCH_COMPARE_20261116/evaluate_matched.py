"""Match attained braking speeds by frozen-policy command calibration; retain every attempt."""
from pathlib import Path
import argparse,contextlib,json,time,traceback,hashlib
import numpy as np
from backends import Adapter,COLUMNS
p=argparse.ArgumentParser();p.add_argument('--kind',choices=['scut','mod4'],required=True);p.add_argument('--direction',type=int,choices=[-1,1],required=True);p.add_argument('--resume',action='store_true');p.add_argument('--contact',choices=['hard','soft'],default='hard');args=p.parse_args()
A=Path(__file__).resolve().parent;O=A/'evidence'/(f'{args.kind}_{"forward"if args.direction>0 else"reverse"}'+('_soft'if args.contact=='soft'else''));O.mkdir(parents=True,exist_ok=args.resume)
def dump(path,d):path.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
started=time.monotonic();adapter=Adapter(args.kind,O,materials='uniform1',contact=args.contact);records=json.loads((O/'ATTEMPTS.json').read_text())['attempts']if args.resume and(O/'ATTEMPTS.json').exists()else[];all_results=json.loads((O/'RESULT.json').read_text())['results']if args.resume and(O/'RESULT.json').exists()else[];serial=len(records)

def run_case(family,height,amplitude,stop=False):
 global serial
 serial+=1;trial_id=f'{family}_h{height:.2f}_{serial:03d}_a{amplitude:.6f}';trace=[];row=dict(id=trial_id,family=family,height_command=height,direction=args.direction,command_amplitude=amplitude,brake=stop)
 with (O/'backend.log').open('a',encoding='utf8')as log,contextlib.redirect_stdout(log):
  control=adapter.create(family,height,args.direction)
  try:
   for k in range(250 if stop else 150):
    command=args.direction*amplitude if 100<=k<150 else 0.;stage=0 if k<100 else 1 if k<150 else 2
    trace.append(adapter.step(command,stage))
    if adapter.failed:break
   z=np.asarray(trace);np.savez_compressed(O/(trial_id+'.npz'),trace=z)
   drive=z[z[:,12]==1];rest=z[z[:,12]==0];brake=z[z[:,12]==2]
   row.update(complete=not adapter.failed and len(z)==(250 if stop else 150),failure=adapter.failed,samples=len(z),max_closure_m=adapter.max_closure,control=control,trajectory=trial_id+'.npz')
   if len(rest):row.update(rest_end_vx=float(rest[-1,5]),rest_end_pitch_deg=float(np.rad2deg(rest[-1,7])),rest_end_height=float(rest[-1,9]))
   if len(drive):row.update(entry_vx=float(drive[-1,5]),signed_entry_speed=float(args.direction*drive[-1,5]),entry_pitch_deg=float(np.rad2deg(drive[-1,7])),entry_height_m=float(drive[-1,9]),entry_x_m=float(drive[-1,3]),startup_peak_deg=float(np.rad2deg(abs(drive[:40,7])).max()),acceleration_peak_deg=float(np.rad2deg(abs(drive[:,7])).max()),startup_rate_peak_rad_s=float(abs(drive[:40,8]).max()),acceleration_mean_m_s2=float(drive[-1,5]-rest[-1,5]),height_MAE_drive_m=float(np.mean(abs(drive[:,9]-height))))
   if len(brake):
    first=brake[:40];entry=drive[-1];allphase=np.vstack([drive,brake]);deltas=np.diff(np.r_[entry[3],brake[:,3]])
    stopped=(np.linalg.norm(brake[:,5:7],axis=1)<.1)&(abs(np.rad2deg(brake[:,7]))<2.)&(abs(brake[:,8])<.2)
    settle=None
    for j in range(len(stopped)-9):
     if stopped[j:j+10].all():settle=float((j+1)*.02);break
    row.update(braking_peak_first0p8_deg=float(np.rad2deg(abs(np.r_[entry[7],first[:,7]])).max()),braking_peak_full2s_deg=float(np.rad2deg(abs(np.r_[entry[7],brake[:,7]])).max()),braking_rate_peak_first0p8_rad_s=float(abs(first[:,8]).max()),braking_rate_peak_full2s_rad_s=float(abs(brake[:,8]).max()),pitch_RMS_active3s_deg=float(np.rad2deg(np.sqrt(np.mean(allphase[:,7]**2)))),first0p8_path_m=float(np.abs(deltas[:40]).sum()),full2s_path_m=float(np.abs(deltas).sum()),first0p8_net_displacement_m=float(abs(first[-1,3]-entry[3])),settle_time_s=settle,brake_end_speed_m_s=float(np.linalg.norm(brake[-1,5:7])),brake_end_pitch_deg=float(np.rad2deg(brake[-1,7])),brake_pitch_change_peak_deg=float(np.rad2deg(abs(brake[:,7]-entry[7])).max()),min_height_brake_m=float(brake[:,9].min()),contact_material_verified=bool(np.allclose(z[z[:,13]>0,14:16],1.)))
  finally:adapter.close()
 records.append(row);dump(O/'ATTEMPTS.json',dict(kind=args.kind,direction=args.direction,columns=COLUMNS,attempts=records));return row
try:
 for family in ['flat','rough']:
  for height in [.28,.4]:
   cache={round(float(row['command_amplitude']),7):row for row in records if row['family']==family and row['height_command']==height and not row['brake']}
   if sum(row['family']==family and row['height_command']==height for row in all_results)==3:continue
   def evaluate(amp):
    amp=round(float(amp),7)
    if amp not in cache:cache[amp]=run_case(family,height,amp)
    return cache[amp]
   for amp in [.3,.6,.9,1.2,1.5,1.8,2.1,2.4,2.7]:evaluate(amp)
   for target in [.6,1.2,2.0]:
    if any(q['family']==family and q['height_command']==height and q['target_speed']==target for q in all_results):continue
    def eligible():return sorted((amp,row)for amp,row in cache.items()if row['complete']and'signed_entry_speed'in row)
    def best():return min(eligible(),key=lambda x:abs(x[1]['signed_entry_speed']-target))if eligible()else None
    found=best()
    if found is not None and abs(found[1]['signed_entry_speed']-target)>.01:
     for amp in [found[0]-.15,found[0]+.15]:
      if .15<=amp<=2.7:evaluate(amp)
     for iteration in range(10):
      found=best()
      if found is not None and abs(found[1]['signed_entry_speed']-target)<=.01:break
      grid=eligible();brackets=[(lo,hi)for lo,hi in zip(grid,grid[1:])if(lo[1]['signed_entry_speed']-target)*(hi[1]['signed_entry_speed']-target)<0]
      if not brackets:break
      lo,hi=min(brackets,key=lambda pair:(pair[1][0],pair[1][0]-pair[0][0]));mid=(lo[0]+hi[0])/2
      if round(mid,7)in cache:break
      evaluate(mid)
    found=best();matched=found is not None and abs(found[1]['signed_entry_speed']-target)<=.01
    result=dict(kind=args.kind,family=family,height_command=height,direction=args.direction,target_speed=target,calibration_matched=matched,attempt_count=len(cache),amplitude_range=[min(cache),max(cache)],best_calibration=found[1]if found else None)
    if matched:
     final=run_case(family,height,found[0],stop=True);result.update(final=final,validated=bool(final['complete']and abs(final['signed_entry_speed']-target)<=.01 and final.get('contact_material_verified',False)))
    else:result.update(validated=False,reason='No speed match within±0.01m/s in this fixed1s acceleration protocol and scanned command range; not a maximum-speed assertion')
    all_results.append(result);dump(O/'RESULT.json',dict(kind=args.kind,direction=args.direction,complete=False,results=all_results,wall_seconds=time.monotonic()-started));print('CASE',args.kind,args.direction,family,height,target,result['validated'],flush=True)
 dump(O/'RESULT.json',dict(kind=args.kind,direction=args.direction,complete=True,results=all_results,wall_seconds=time.monotonic()-started));print('WORKER_COMPLETE',args.kind,args.direction,len(all_results),flush=True)
except Exception:
 (O/'ERROR.txt').write_text(traceback.format_exc(),encoding='utf8');raise
