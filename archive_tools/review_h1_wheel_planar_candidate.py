"""Inspect actual469 saved motion and score planar wheel tracking offline."""
from pathlib import Path
import json
import time

import numpy as np

from analyze_h1_saved_route import dense_view, identity, load_case, read, reconstruct, rpy

S=Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102')
T=S/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021'
N=S/'runs/h1_reward_tail_20261103'
O=S/'analysis/20261103_rewardtail469_vs455'


def main():
    destination=O/'WHEEL_PLANAR470_OFFLINE_CANDIDATE.json'
    assert not destination.exists()
    receipt=read(N/'evaluation/reports/ROOT469_SELECTED_REPLAY_TRANSFERS.json')
    baseline=T/'RL455_FINAL_INDEPENDENT_EVAL_V456_20261102'
    with np.load(baseline/'reference389.npz',allow_pickle=False)as p:
        reference={k:p[k].copy()for k in p.files}
    commands=np.asarray(read(baseline/'feedforward389.json')['commands'])
    contract=read(T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/assets/import_contract.json')
    hips=np.asarray([contract['joints'][s+'_hip']['local_pos0']for s in ('left','right')])
    rows,packets=[],{}
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(11,8))
    for row in receipt['cases']:
        p=load_case(row);packets[row['env']]=p
        c=reconstruct(p,row,reference,commands,hips)
        cost=c['cost']+.5*((c['geodesic']/.2)**2-c['terms']['rotation'])
        cost+=(((c['wheel'][:,:,2]-c['wheel_reference'][:,:,2])/.05)**2).mean(-1)
        planar=(((c['wheel'][:,:,:2]-c['wheel_reference'][:,:,:2])/.1)**2).sum(-1).mean(-1)
        actual=1/(1+cost/5);candidate=1/(1+(cost+planar)/5)
        assert abs(float(actual.mean())-row['result']['tracking_reward_mean'])<.001
        samples=[]
        for seconds in (.2,.4,.6,.76,.8,.9,1.,1.12):
            i=round(seconds/.02)-1
            samples.append(dict(seconds=seconds,actual_total_cost=float(cost[i]),
                added_planar_cost=float(planar[i]),actual_reward=float(actual[i]),candidate_reward=float(candidate[i]),
                wheel_x_reference_minus_actual=(c['wheel_reference'][i,:,0]-c['wheel'][i,:,0]).tolist(),
                wheel_y_actual_minus_reference=(c['wheel'][i,:,1]-c['wheel_reference'][i,:,1]).tolist(),
                actual_pitch_deg=float(np.rad2deg(c['rpy'][i,1])),
                reference_pitch_deg=float(np.rad2deg(rpy(c['reference'][i:i+1,3:12].reshape(-1,3,3))[0,1])),
                root_position_cost=float(c['terms']['position'][i])))
        before=c['t']<=.74
        rows.append(dict(env=row['env'],samples=samples,
            first20_motor_position_target_mean=p['motor_pos_target'][:20,[0,1,3,4]].mean(0).tolist(),
            first20_motor_position_mean=p['motor_q'][:20,[0,1,3,4]].mean(0).tolist(),
            right_hip_upperlimit_fraction_before_launch=float((p['motor_q'][before,3]>.499).mean()),
            limitation='Target exceeding jointlimit observed, no physics/PD/limits changed; not sole causal proof'))
        label=f"env{row['env']}"
        axes[0,0].plot(c['t'],(c['wheel_reference'][:,:,0]-c['wheel'][:,:,0]).mean(-1),label=label)
        axes[0,1].plot(c['t'],(c['wheel'][:,:,1]-c['wheel_reference'][:,:,1]).mean(-1),label=label)
        axes[1,0].plot(c['t'],planar,label=label)
        color=axes[1,1].plot(c['t'],actual,label=label+' actual')[0].get_color()
        axes[1,1].plot(c['t'],candidate,'--',color=color,label=label+' offline')
    for ax,title in zip(axes.flat,['Wheel forward lag (m)','Wheel lateral error (m)',
                                  'Added planar cost, scale .10m','Actual vs offline candidate reward']):
        ax.set(xlim=(0,1.25),xlabel='Time (s)',title=title)
        ax.grid(alpha=.2);ax.legend(fontsize=8)
    fig.tight_layout();plot=O/'wheel_planar470_candidate.png';fig.savefig(plot,dpi=150);plt.close(fig)
    late=N/'evaluation/recorded_native_late';late.mkdir(exist_ok=False)
    long=dict(receipt,cases=[r for r in receipt['cases']if r['controls']==400])
    media=dense_view(T,long,packets,late,times=[1.5,1.8,2.1,2.5,3.,4.,5.,6.,8.],
                     title='Actual469 RL468',prefix='actual469',suffix='late')
    with(late/'RENDER_REPORT.json').open('x',encoding='utf8')as f:
        json.dump(dict(model_SHA=receipt['model_SHA'],media=media,NN=0,physics_steps=0),f,indent=2)
    report=dict(epoch=time.time(),kind='OFFLINE_WHEEL_PLANAR470_CANDIDATE',source_model_SHA=receipt['model_SHA'],
        actual_evaluation=469,actual_analysis=identity(O/'analysis.json'),selected=rows,
        added_cost='mean_wheels(sum_xy(((actual wheel_world-reference wheel_world)/.10m)^2))',
        weight=1.,mapping='Same reciprocal1/(1+totalcost/5)',reference_unchanged=True,
        basis='Firstground beforeedge; wheel horizontal lag evident before takeoff, current bodyposition weak and heightonly misses horizontal error',
        limits='Offline saved selected motion; nonpairedDR, not actualnewonpolicy orpolicyimprovement. Fullnonwheelmanifold unavailable.',
        media=[identity(plot),*media],modelreads=0,network=0,SDK=0,physics_steps=0,production_optimizers=0)
    with destination.open('x',encoding='utf8')as f:json.dump(report,f,indent=2,allow_nan=False)
    print(json.dumps(dict(output=str(destination),cases=len(rows),late_images=len(media))))


if __name__=='__main__':main()
