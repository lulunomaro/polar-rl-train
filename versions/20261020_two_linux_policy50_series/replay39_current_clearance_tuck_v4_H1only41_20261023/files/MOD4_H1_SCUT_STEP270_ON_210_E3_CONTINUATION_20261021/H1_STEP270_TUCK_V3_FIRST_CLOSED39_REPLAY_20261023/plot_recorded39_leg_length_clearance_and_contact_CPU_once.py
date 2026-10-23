from pathlib import Path
import hashlib,json,time,traceback
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

D=Path(__file__).resolve().parent;R=D/'reports'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
try:
    g=json.loads((R/'RECORDED_USD_KINEMATICS_CPU_ACTUAL.json').read_bytes());names=g['body_names']
    with np.load(D/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False) as z,np.load(D/'RECORDED_KINEMATIC_RECONSTRUCTION.npz',allow_pickle=False) as k:
        pos=k['body_pose'][:,:,:,:3,3];delta=np.take(pos,[names.index('left_wheel'),names.index('right_wheel')],axis=2)-pos[:,:,None,0,:];length=np.linalg.norm(delta,axis=-1).mean(-1)*1000;bottom=k['wheel_min'][:,:,:,2].min(-1)*1000;force=np.linalg.norm(z['history5ms'],axis=-1).max(axis=(2,3));t=np.arange(48)*10
        fig,axs=plt.subplots(3,2,figsize=(13,8),sharex=True,constrained_layout=True)
        for col,env in enumerate((13253,18844)):
            e=int(np.where(z['env_ids']==env)[0][0]);axs[0,col].plot(t,length[:,e],color='#1766a5',lw=2);axs[0,col].set_title(f'Closed39 recorded case {env}');axs[0,col].set_ylabel('Body-to-axle mean (mm)')
            axs[1,col].plot(t,bottom[:,e],color='#1766a5',lw=2);axs[1,col].axhline(5,color='#cc6438',ls='--',label='Existing runtime 5mm air clause');axs[1,col].set_ylabel('Lower wheel bottom (mm)');axs[1,col].legend(fontsize=8)
            axs[2,col].plot(t,force[:,e],color='#cc6438',lw=2);axs[2,col].set_ylabel('Recent contact history peak (N)');axs[2,col].set_xlabel('Time within saved clip (ms)')
            for ax in axs[:,col]:
                ax.grid(alpha=.2);ax.axvline(410,color='#777777',ls=':',lw=1)
                ended=~z['public_request'][:,e].astype(bool)
                if ended.any():ax.axvspan(t[np.where(ended)[0][0]],470,color='#b5c5d5',alpha=.16)
        fig.suptitle('Leg retraction is recorded, but the strongest contraction is near the floor\nShading: public request ended | Dotted line: frame41',fontsize=13)
        fig.supxlabel('48 saved100Hz controls,0.48s; kinematics reconstructed from saved root/q, not a new policy rollout.\nContact curve is max over3 cached5ms samples, not instantaneous force. No crossing/landing success claimed.',fontsize=9)
        out=D/'RECORDED39_TUCK_NEAR_GROUND_DIAGNOSTIC.png';assert not out.exists();fig.savefig(out,dpi=140);plt.close(fig)
    put('RECORDED39_TUCK_NEAR_GROUND_PLOT_CPU_ACTUAL.json',dict(epoch=time.time(),artifact=dict(path=str(out),bytes=out.stat().st_size,SHA=hashlib.sha256(out.read_bytes()).hexdigest()),source_small_derived_motion_and_kinematics=True,no_original_raw_or_PT_read=True,not_callback_replay_or_new_policy_evaluation=True,not_comparison_to_old_policy_or_skill_proof=True,contact_history_not_instantaneous=True))
    print(json.dumps(dict(path=str(out),bytes=out.stat().st_size)))
except BaseException:
    put('RECORDED39_PLOT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
