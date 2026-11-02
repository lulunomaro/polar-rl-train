"""Readable Chinese review chart from measured saved control curves; no experiment rerun."""
from pathlib import Path
import csv,hashlib,json,time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
N=Path(__file__).resolve().parent;R=N/'reports'
plt.rcParams.update({'font.family':'Microsoft YaHei','font.size':11,'axes.unicode_minus':False,'axes.grid':True,'grid.alpha':.22})
fig,axes=plt.subplots(2,2,figsize=(14,9),layout='constrained');colors=['#2364aa','#b43c39','#279063','#8c55a5']
for color,env in zip(colors,(0,40,1,41)):
    with(N/f'env{env}_aligned_control_curves.csv').open(encoding='utf8')as f:rows=list(csv.DictReader(f))
    v=lambda name:np.asarray([float(r[name])for r in rows]);t=v('time_s')
    axes[0,0].plot(v('root_x'),v('root_y'),c=color,label=f'实际 env{env}')
    axes[0,1].plot(t,np.rad2deg(v('yaw_rad')),c=color,label=f'env{env}')
    if env==0:
        axes[0,0].plot(v('ref_x'),v('ref_y'),'k--',lw=2,label='参考路线')
        for name,field,col in(('左轮','wheel_L','#2364aa'),('右轮','wheel_R','#b43c39')):
            axes[1,0].plot(t,v(field+'_requested_rad_s'),c=col,label=name+'目标')
            axes[1,0].plot(t,v(field+'_measured_rad_s'),c=col,ls=':',label=name+'实测')
    origin=json.loads((N.parent/'RL445_ACTUAL446_REPLAY_RECOVERY_V451_20261102/reports/ROOT451_ACTUAL446_SELECTED_REPLAY_TRANSFERS.json').read_bytes())
    row=next(r for r in origin['cases']if r['env']==env)
    with np.load(row['local_path'],allow_pickle=False)as p:
        wi=[row['body_names'].index(side+'_wheel')for side in('left','right')];bottom=p['body_position_w'][:,wi,2].min(-1)-row['origin'][2]-.0637
    axes[1,1].plot(t,bottom,c=color,label=f'env{env}')
axes[0,0].axvline(.8,c='#008ac3',label='台阶前沿 x=0.8m');axes[0,0].set(title='路线：起跳前已斜向左偏离',xlabel='前进 x（米）',ylabel='横移 y（米）',xlim=(-.05,1.45),ylim=(-.2,.7))
axes[0,1].set(title='偏航：0.4秒约30°，参考接近0°',xlabel='时间（秒）',ylabel='偏航（度）',xlim=(0,1.6),ylim=(-65,45));axes[0,1].axhline(0,c='k',ls='--',label='参考约0°')
axes[1,0].set(title='前0.6秒：策略让左右轮显著差速',xlabel='时间（秒）',ylabel='轮速（rad/s）',xlim=(0,.6),ylim=(-20,30))
axes[1,1].axhline(.27,c='k',ls='--',label='台面 0.270m');axes[1,1].set(title='双轮最低轮底：最高仅约0.18–0.21米',xlabel='时间（秒）',ylabel='轮底高度估计（米）',xlim=(0,1.6),ylim=(-.01,.30))
for ax in axes.flat:ax.legend(fontsize=9,ncol=2)
fig.suptitle('RL445 实际独立评测446：先跑偏，轮子未抬过台面，在台前落地｜0/80成功',fontsize=16)
p=N/'08_实际路线_轮速_偏航_越台高度.png';assert not p.exists();fig.savefig(p,dpi=150);plt.close(fig)
report=dict(epoch=time.time(),passed=True,path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest(),
    source='Saved actual446 control traces and451 verified recordedbodyposes',plot_only=True,modelreads=0,physics=0,
    note='Limits focus actual displayed time interval; preserves all earlier plots and their receiptSHA unchanged.')
with(R/'PLOT457_CHINESE_REVIEW_V2.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2,ensure_ascii=False)
print(json.dumps(report,ensure_ascii=False))
