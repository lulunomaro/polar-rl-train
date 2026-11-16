"""Freeze observed results and scientific plots; no additional training."""
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
 before=guard();d=json.loads((T/'dagger/COLLECTION.json').read_text());sep=json.loads((T/'evidence/SEPARABILITY.json').read_text());fit=json.loads((T/'offline_probe_keep1/FIT.json').read_text());probe=json.loads((T/'offline_probe_keep1/independent_student200/RESULT.json').read_text());rows=[]
 for row in probe['rows']:
  p=T/f"offline_probe_keep1/independent_student200/start_{row['start_offset_mm']:+04d}mm/rollout.npz";z=np.load(p);tr=z['trace'];o=z['obs'];mask=tr[:,0]<=1.6
  physical=(tr[:,9]>0)&(tr[:,10]>0)&(tr[:,1]>1.23)
  rows.append(dict(**row,physical_bilateral_top_body_any=bool(physical.any()),pre1s_drift_m=float(tr[49,1]-row['start_offset_mm']/1000),pre1s_peak_speed=float(tr[:50,5].max()),first1p6s_min_root_z=float(tr[mask,3].min()),first1p6s_peak_speed=float(tr[mask,5].max())))
 summary=dict(PPO_updates=0,offline_optimizer_steps=fit['optimizer_steps'],offline_fit_seconds=fit['wall_seconds'],teacher_attempts=d['attempts'],teacher_qualified=d['qualified'],teacher_rejected=d['failed'],new_qualified_frames=d['qualified_frames'],new_prewall_idle_frames=sep['new_flat_frames'],new_low_wheel_frames=sep['new_low_wheel_frames'],probe_independent_student_passed=probe['passed'],probe_independent_student_requested=probe['requested'],probe_physical_any_bilateral_body_crossing=sum(r['physical_bilateral_top_body_any']for r in rows),probe_rows=rows,probe_adopted=False,source_hashes_before_after_identical=True,teacher_model_profile_changed=False,source_inputs_unchanged=before,missing_user_instruction='User message truncated at 带keep=1与临时; no keep0 comparison or second-step PPO inferred',all_failure_artifacts_retained=True)
 put(T/'evidence/STAGE1_SUMMARY.json',summary)
 fig,axs=plt.subplots(2,2,figsize=(13,8));colors=['#b54846','#258160','#416db5']
 old=np.load(P/'evidence/checkpoint_evals/model_010m/single_step/start_+000mm/rollout.npz');cor=np.load(T/'dagger/model_010m/start_+000mm/command_onset/correction.npz');pr=np.load(T/'offline_probe_keep1/independent_student200/start_+000mm/rollout.npz')
 for label,z,color,teacher in [('repair10m (28360ac4)',old,colors[0],False),('frozen teacher: live handoff at 1.0s',cor,colors[1],True),('offline keep=1 probe, 64 Adam steps',pr,colors[2],False)]:
  tr=z['features']if teacher else z['trace'];time=tr[:,0];xx=tr[:,1];zz=tr[:,3];vx=tr[:,7]if teacher else tr[:,4];aa=z['actions'];rear=aa[:,[1,3]].mean(1)
  axs[0,0].plot(time,xx,color=color,label=label);axs[0,1].plot(time,zz,color=color,label=label);axs[1,0].plot(time,vx,color=color,label=label);axs[1,1].plot(time-.02,rear,color=color,label=label)
 for ax in axs.flat:ax.set_xlim(0,6);ax.grid(alpha=.25);ax.axvline(1,color='#888',ls=':',lw=1);ax.set_xlabel('Simulation time (s)')
 axs[0,0].axhline(1.2,color='#555',ls='--',lw=1,label='step edge x=1.2m');axs[0,0].set_ylabel('Base x (m)');axs[0,0].set_title('Physical approach / crossing')
 axs[0,1].axhline(.4091,color='#555',ls='--',lw=1);axs[0,1].set_ylabel('Base origin z (m)');axs[0,1].set_title('Pre-wall height collapses before contact')
 axs[1,0].axhline(.47,color='#555',ls='--',lw=1);axs[1,0].axhline(.6,color='#aaa',ls=':',lw=1);axs[1,0].set_ylabel('World forward vx (m/s)');axs[1,0].set_title('Actual forward speed')
 axs[1,1].set_ylabel('Mean rear-joint action');axs[1,1].set_title('Actor output / teacher action, PPO order')
 handles,labels=axs[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=2,fontsize=9);fig.suptitle('200mm center: unchanged physics, teacher recovery and an unsuccessful offline probe');fig.tight_layout(rect=(0,.1,1,.95));out=T/'evidence/figures';out.mkdir(exist_ok=True);fig.savefig(out/'PREWALL_REAL_TRACE_COMPARISON.png',dpi=150);plt.close(fig)
 print('STAGE1_SUMMARY',json.dumps({k:v for k,v in summary.items()if k not in ['probe_rows','source_inputs_unchanged']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
