from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
T=Path(__file__).resolve().parent;E=T/'evidence';font=FontProperties(fname='C:/Windows/Fonts/msyh.ttc');plt.rcParams.update({'font.family':font.get_name(),'axes.unicode_minus':False,'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
d=json.loads((E/'SPEED_RESPONSE.json').read_text());hy=json.loads((E/'hybrid_followup/GEOMETRY_AND_HYBRIDS.json').read_text());fig,ax=plt.subplots(1,3,figsize=(16,5.1),gridspec_kw={'width_ratios':[1.2,1.1,1.]});fig.patch.set_facecolor('#f8fafc')
cs=(0.,1.,1.5,2.,2.2)
for m,label,color in [('parent','原父模型','#334155'),('005m','5分钟','#3b82f6'),('010m','10分钟','#f97316')]:
 vals=[next(r['tail_horizontal_vx'] for r in d['rows'] if r['model']==m and r['delay_ms']==5 and r['height']==.28 and r['cmd_vx']==c) for c in cs];ax[0].plot(cs,vals,'o-',color=color,label=label,lw=2)
ax[0].plot([0,2.2],[0,2.2],'--',color='#94a3b8',label='准确跟踪');ax[0].set(xlabel='前进指令（m/s）',ylabel='实际水平速度（m/s）',title='0.28米站姿：前向偏差扩大');ax[0].legend(frameon=False,loc='upper left');ax[0].grid(alpha=.15)
models=['parent','parent_legs_child_wheels','child_legs_parent_wheels','010m'];vals=[next(r['tail_horizontal_vx'] for r in hy['rows'] if r['model']==m and r['height']==.28 and r['cmd_vx']==2.2) for m in models]
bars=ax[1].bar(np.arange(4),vals,color=['#64748b','#94a3b8','#fb923c','#ea580c'],width=.67);ax[1].set_xticks(np.arange(4),['父腿\n父轮','父腿\n新轮','新腿\n父轮','新腿\n新轮']);ax[1].axhline(2.2,color='#dc2626',ls='--',lw=1.4);ax[1].set(ylim=(1.9,3.17),ylabel='实际水平速度（m/s）',title='替换输出对照：偏移跟随腿控')
for b,v in zip(bars,vals):ax[1].text(b.get_x()+b.get_width()/2,v+.035,f'{v:.3f}',ha='center',fontsize=10)
for i,(m,label,color) in enumerate([('parent','原父模型','#64748b'),('010m','10分钟','#f97316')]):
 vals=[next(r['tail_horizontal_vx'] for r in d['rows'] if r['model']==m and r['delay_ms']==5 and r['height']==h and r['cmd_vx']==2.2) for h in (.28,.38)];bs=ax[2].bar(np.arange(2)+(i-.5)*.34,vals,.34,label=label,color=color)
 for b,v in zip(bs,vals):ax[2].text(b.get_x()+b.get_width()/2,v+.035,f'{v:.3f}',ha='center',fontsize=10)
ax[2].axhline(2.2,color='#dc2626',ls='--',lw=1.4);ax[2].set_xticks([0,1],['高度0.28米','高度0.38米']);ax[2].set(ylim=(1.7,3.17),ylabel='实际水平速度（m/s）',title='高站姿改善，低站姿退化');ax[2].legend(frameon=False)
fig.suptitle('平地超速调查：腿控与轮控的耦合发生了迁移',fontsize=17,y=.99);fig.text(.5,.025,'同一MuJoCo名义plant · 2.5/10/20ms时序 · 固定5ms动作/传感器延迟 · 每例12s，取末4s · 冻结权重，无训练',ha='center',fontsize=10,color='#475569');fig.tight_layout(rect=[0,.07,1,.93]);fig.savefig(E/'SPEED_CAUSE.png',dpi=170,facecolor=fig.get_facecolor());print(E/'SPEED_CAUSE.png')
