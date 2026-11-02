"""Review actual467 saved poses and score one reward mapping candidate offline."""
from pathlib import Path
import json
import sys
import time

import numpy as np

from analyze_h1_saved_route import dense_view, identity, load_case, read, reconstruct

S = Path('F:/RMPOLAR-RL/mjcf_mod4_h1_archive_01a1967f_20261102')
T = S/'workspace/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021'
N = S/'runs/h1_wheel_height_20261103'
O = S/'analysis/20261103_wheelheight467_vs455'


def main():
    output = O/'RECIPROCAL468_OFFLINE_CANDIDATE.json'
    assert not output.exists()
    receipt = read(N/'evaluation/reports/ROOT467_SELECTED_REPLAY_TRANSFERS.json')
    baseline = T/'RL455_FINAL_INDEPENDENT_EVAL_V456_20261102'
    with np.load(baseline/'reference389.npz', allow_pickle=False) as p:
        reference = {k: p[k].copy() for k in p.files}
    commands = np.asarray(read(baseline/'feedforward389.json')['commands'])
    contract = read(T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/package/payload/job0/assets/import_contract.json')
    hips = np.asarray([contract['joints'][s+'_hip']['local_pos0'] for s in ('left','right')])
    rows, packets = [], {}
    for row in receipt['cases']:
        packet = load_case(row)
        packets[row['env']] = packet
        c = reconstruct(packet, row, reference, commands, hips)
        base = c['cost']+.5*((c['geodesic']/.2)**2-c['terms']['rotation'])
        height = (((c['wheel'][:,:,2]-c['wheel_reference'][:,:,2])/.05)**2).mean(-1)
        cost = base+height
        old = np.exp(-cost/5.)
        candidate = 1./(1.+cost/5.)
        assert abs(float(old.mean())-row['result']['tracking_reward_mean']) < .001
        hypothetical = (((c['wheel'][:,:,2]+.01-c['wheel_reference'][:,:,2])/.05)**2).mean(-1)
        samples = []
        for seconds in (.4,.78,.9,1.,1.12,1.5,4.,8.):
            i = round(seconds/.02)-1
            if i >= len(cost):
                continue
            samples.append(dict(seconds=seconds, unchanged_total_cost=float(cost[i]),
                reward_actual=float(old[i]), reward_candidate=float(candidate[i]),
                height_raise10mm_old_delta=float(np.exp(-(base[i]+hypothetical[i])/5.)-old[i]),
                height_raise10mm_candidate_delta=float(1./(1.+(base[i]+hypothetical[i])/5.)-candidate[i])))
        rows.append(dict(env=row['env'], actual_controls=row['controls'], samples=samples,
                         actual_reward_mean=float(old.mean()), candidate_reward_mean=float(candidate.mean())))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    cost = np.linspace(0,60,601)
    fig, axes = plt.subplots(1,2,figsize=(11,4))
    axes[0].plot(cost,np.exp(-cost/5),label='actual466 exp(-cost/5)')
    axes[0].plot(cost,1/(1+cost/5),label='candidate468 1/(1+cost/5)')
    axes[1].semilogy(cost,np.exp(-cost/5)/5,label='exponential sensitivity')
    axes[1].semilogy(cost,1/(5*(1+cost/5)**2),label='reciprocal sensitivity')
    for ax,title in zip(axes,['Same cost and optimum','Absolute reward change per cost unit']):
        ax.set(xlabel='Unchanged total tracking cost',title=title)
        ax.grid(alpha=.2)
        ax.legend()
    fig.tight_layout()
    plot = O/'reward_mapping_candidate.png'
    if not plot.exists():
        fig.savefig(plot,dpi=150)
    plt.close(fig)
    late = N/'evaluation/recorded_native_late'
    late.mkdir(exist_ok=True)
    long_receipt = dict(receipt,cases=[r for r in receipt['cases'] if r['controls']==400])
    media = dense_view(T,long_receipt,packets,late,times=[1.5,1.8,2.1,2.5,3.,4.,5.,6.,8.],
                       title='Actual467 RL466',prefix='actual467',suffix='late')
    with (late/'RENDER_REPORT.json').open('x',encoding='utf8') as f:
        json.dump(dict(model_SHA=receipt['model_SHA'],media=media,NN=0,physics_steps=0),f,indent=2)
    report = dict(epoch=time.time(),kind='OFFLINE_RECIPROCAL_MAPPING468_CANDIDATE',
        source_model_SHA=receipt['model_SHA'],actual_evaluation=467,
        actual_analysis=identity(O/'analysis.json'),selected=rows,
        formula='1/(1+cost/5)',unchanged_cost='All approved attitude464 and height466 terms/scales/weights',
        optimum_and_order_preserved=True,small_error_slope_preserved=-.2,
        hypothesis='Prevent exponential near-zero scores from masking later improvements; independent RL validation still required',
        other_candidate='Separate averaged exponential terms considered offline; not adopted because it permits one good component to compensate other poor tracking',
        limits='10mm perturbations are counterfactual scores, not physically achievable steps or new onpolicy data. No causal skill claim.',
        media=[identity(plot),*media],modelreads=0,network=0,SDK=0,physics_steps=0,production_optimizers=0)
    with output.open('x',encoding='utf8') as f:
        json.dump(report,f,indent=2,allow_nan=False)
    print(json.dumps(dict(output=str(output),cases=len(rows),late_images=len(media))))


if __name__ == '__main__':
    main()
