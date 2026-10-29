from pathlib import Path
import json,os,time
S=Path(__file__).resolve().parent;R=S/'reports'
def main():
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 v=json.loads((R/'NEW108_ACTUAL20S_MOTION_CONTACT_CLOCK_AND_CONTIGUOUS_WM_ANALYSIS_ACTUAL.json').read_bytes());d=json.loads((R/'NEW108_DERIVED_CONTROL_CURVES_FOR_PLOT_ONLY.json').read_bytes())['rows']
 rows=json.loads((R/'FROZEN108_CASE_FULL_TEXT_AND_NEW_RAW_TRANSFER_ACTUAL.json').read_bytes())['rows'];f=next(x['local_path'] for x in rows if x['relative'].endswith('NEW108_ACTUAL_ACTION_CONTIGUOUS_8_32_WM_WINDOWS_ACTUAL.json'));windows=json.loads(Path(f).read_bytes())['rows'];extremes={}
 for h in (8,32):
  points=[]
  for row in windows:
   if row['horizon']!=h:continue
   for step in row['steps']:
    if step['actual_phase']['airborne_both_above5mm_and_unloaded']:
     points.append(dict(start_control=row['start_control'],offset=step['offset'],target_control=row['start_control']+step['offset']-1,predicted_bottom2=step['predicted_wheel_bottom2'],actual_bottom2=step['actual_wheel_bottom2'],signed_error2=[a-b for a,b in zip(step['predicted_wheel_bottom2'],step['actual_wheel_bottom2'])],max_abs_error=max(step['wheel_bottom_abs_error2'])))
  extremes[str(h)]=max(points,key=lambda x:x['max_abs_error']) if points else None
 with (R/'NEW108_WM_AIRBORNE_ENDPOINT_ERROR_EXTREMES_TEXT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),rows=extremes,derived_source_only_no_raw_or_model_read=True,one_case_not_unseen270mm_accuracy=True),f,indent=2)
 t=[x['time_s'] for x in d];both=[1000*min(x['wheel_bottom2']) for x in d]
 fig,ax=plt.subplots(3,1,figsize=(11,8.5),sharex=True,layout='constrained')
 fig.suptitle('NEW108: frozen qualified107 mean policy, one 20-second case',fontsize=14)
 ax[0].plot(t,both,color='#1764ab',lw=1.2,label='simultaneous both-wheel bottom (100 Hz endpoint)');ax[0].axhline(5,color='#777777',ls=':',lw=1,label='5 mm diagnostic line');ax[0].set_ylabel('Wheel clearance [mm]');ax[0].set_ylim(-5,12);ax[0].legend(loc='upper right',fontsize=8)
 ax[0].text(.5,10,'400 Hz peak: %.2f mm; task requires 270 mm (outside scale)'%(v['both_wheel_simultaneous_peak_m']*1000),fontsize=10)
 ax[1].plot(t,[x['root_x'] for x in d],color='#1764ab',label='actual chassis x');ax[1].axhline(.35,color='#d87500',ls='--',label='step leading edge x=0.35 m');ax[1].axhline(.75,color='#a22727',ls='--',label='terminal chassis goal x=0.75 m');ax[1].set_ylabel('Forward position [m]');ax[1].set_ylim(-.12,.85);ax[1].legend(loc='upper right',fontsize=8)
 ax[2].plot(t,[x['actor_request_bit'] for x in d],color='#1764ab',label='actual actor request bit');ax[2].step(t,[float(x['request_for_action']) for x in d],where='post',color='#d87500',ls='--',label='declared 2..20 s request');ax[2].set_ylabel('Request bit');ax[2].set_xlabel('Simulation time [s]');ax[2].set_ylim(-.1,1.2);ax[2].legend(loc='upper right',fontsize=8)
 for a in ax:a.axvline(2,color='#555555',ls=':',lw=.8);a.grid(alpha=.2);a.set_xlim(0,20)
 p=S/'NEW108_ACTUAL20S_MOTION_AND_ALIGNED_REQUEST.png';assert not p.exists();fig.savefig(p,dpi=150);plt.close(fig)
 print(json.dumps(dict(plot=str(p),bytes=p.stat().st_size,raw_model_or_oldcase_reads=0,WM_air_endpoint_extremes=extremes)))
if __name__=='__main__':main()
