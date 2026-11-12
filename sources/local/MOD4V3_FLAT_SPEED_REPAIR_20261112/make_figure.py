from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
T=Path(__file__).resolve().parent;E=T/'evidence';font=FontProperties(fname='C:/Windows/Fonts/msyh.ttc');plt.rcParams.update({'font.family':font.get_name(),'axes.unicode_minus':False,'font.size':10})
old=json.loads((E/'dense_parent/RESULT.json').read_text())['rows'];new=json.loads((E/'dense_final/RESULT.json').read_text())['rows'];history=json.loads((E/'REPLAY_SCOREBOARD.json').read_text())['rows'];native=json.loads((E/'NATIVE_FORMAL_METRICS.json').read_text())['groups']
fig,ax=plt.subplots(2,2,figsize=(12,8.5),layout='constrained');fig.suptitle('平地速度恢复对照 · 2026-11-12',fontproperties=font,fontsize=17)
for rs,color,label in [(old,'#8b96a5','原父模型'),(new,'#087e8b','最终候选')]:
 rows=sorted([r for r in rs if r['cmd_vx']==2.2],key=lambda r:r['cmd_height']);ax[0,0].plot([r['cmd_height'] for r in rows],[r['vx_mean'] for r in rows],'o-',color=color,label=label,lw=2)
ax[0,0].axhline(2.2,color='#d1495b',ls='--',label='2.2 m/s 指令');ax[0,0].axhspan(2.05,2.35,color='#d1495b',alpha=.06);ax[0,0].set(title='相同速度指令，不同高度指令',xlabel='高度指令 (m)',ylabel='MuJoCo 实测前向速度 (m/s)');ax[0,0].legend()
x=[r['minutes'] for r in history];ax[0,1].plot(x,[r['forward_mean_error'] for r in history],'o-',c='#087e8b',label='平均绝对误差');ax[0,1].plot(x,[r['forward_max_error'] for r in history],'s-',c='#e49b0f',label='最大绝对误差');ax[0,1].axvline(17.507,ls=':',c='#687386');ax[0,1].text(18,.74,'全策略接续',fontproperties=font,color='#687386');ax[0,1].set(title='7项扩展前进回放 × 0/5 ms 延迟',xlabel='累计 PPO 时间 (分钟)',ylabel='速度误差 (m/s)');ax[0,1].legend()
names=['parent','candidate','latest'];xs=np.arange(3)
for k,var,color,label in [(0,'nominal0','#8b96a5','名义 PhysX'),(1,'Step7_all_remaining_DR','#087e8b','完整 DR')]:
 vals=[next(r['formal_pre_pass'] for r in native if r['model']==n and r['variant']==var) for n in names];bars=ax[1,0].bar(xs+(k-.5)*.34,vals,width=.34,color=color,label=label)
 for b,v in zip(bars,vals):ax[1,0].text(b.get_x()+b.get_width()/2,v+.4,f'{v}/30',ha='center',fontsize=9)
ax[1,0].set(xticks=xs,xticklabels=['原父模型','35分钟','最终候选'],ylim=(0,34),title='原生原六项：5初态/项，推扰前稳定窗口',ylabel='通过样本数');ax[1,0].legend(loc='upper right',fontsize=8)
for rs,color,label,marker in [(old,'#a4acb7','原父模型','o'),(new,'#087e8b','最终候选','x')]:ax[1,1].scatter([r['cmd_vx'] for r in rs],[r['vx_mean'] for r in rs],s=32,c=color,label=label,marker=marker,alpha=.8)
v=np.linspace(-2.3,2.3,200);tol=np.where(v<0,.20,.15);ax[1,1].plot(v,v,'--',c='#d1495b',lw=1);ax[1,1].fill_between(v,v-tol,v+tol,color='#d1495b',alpha=.05);ax[1,1].set(title='扩展49点网格：7高度 × 7速度，均无重置',xlabel='速度指令 (m/s)',ylabel='MuJoCo 实测速率 (m/s)');ax[1,1].legend()
for a in ax.flat:a.grid(alpha=.2);a.set_axisbelow(True)
fig.savefig(E/'SPEED_REPAIR_COMPARISON.png',dpi=160,bbox_inches='tight');plt.close(fig)
