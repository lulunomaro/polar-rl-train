"""Compare matched airborne controllers, render saved states and preserve evidence."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from base_jump import write_json

T = Path(__file__).resolve().parent
R = T.parents[2]
REMOTE = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_MOVING_JUMP_AIR_BALANCE_20261114_R1'


def trace(row):
    with np.load(T/row['trajectory']) as a:
        return {k:a[k] for k in a.files}


def analyze():
    rows = []
    for path in sorted((T/'evidence').glob('*/*/RESULT.json')):
        row = json.loads(path.read_text(encoding='utf8'))
        row.update(batch=path.parents[1].name, trajectory=(path.parent/'trajectory.npz').relative_to(T).as_posix())
        rows.append(row)
    verified = [r for r in rows if r['batch'].startswith('air_verify')]
    baseline = [r for r in verified if not r['config']['air_balance']]
    instant = [r for r in verified if r['config']['air_balance']]
    rejected = [r for r in rows if r['batch'].startswith('air_final')]
    balanced = instant
    final = baseline+balanced
    assert len(balanced)==30 and len(baseline)==30
    groups = []
    for model in ('teacher', 'parent'):
        for mode in (False, True):
            group = [r for r in final if r['model']==model and r['config']['air_balance']==mode]
            groups.append(dict(model=model, balanced=mode, cases=len(group),
                constraint_pass=sum(r['within_pitch10_roll5'] for r in group),
                air_peak_pitch_deg=max(r['air_peak_abs_pitch_deg'] for r in group),
                air_peak_roll_deg=max(r['air_peak_abs_roll_deg'] for r in group),
                mean_case_pitch_rms_deg=float(np.mean([r['air_rms_pitch_deg'] for r in group])),
                genuine_airborne=sum(r['genuine_airborne'] for r in group),
                stable_landing=sum(r['stable_landing'] for r in group),
                complete_sequence=sum(r['phase_sequence_completed'] for r in group),
                rim_peak_range_m=[min(r['primary_air']['peak_paired_rim_z_m'] for r in group), max(r['primary_air']['peak_paired_rim_z_m'] for r in group)]))
    matched = []
    for row in balanced:
        other = next(r for r in baseline if (r['model'],r['speed_command'],r['seed'])==(row['model'],row['speed_command'],row['seed']))
        matched.append(dict(model=row['model'], command=row['speed_command'], seed=row['seed'],
            baseline=other['batch']+'/'+other['id'], balanced=row['batch']+'/'+row['id'],
            baseline_air_pitch_deg=other['air_peak_abs_pitch_deg'], balanced_air_pitch_deg=row['air_peak_abs_pitch_deg'],
            reduction_fraction=1.-row['air_peak_abs_pitch_deg']/other['air_peak_abs_pitch_deg']))
    rep = next(r for r in balanced if r['model']=='parent' and r['speed_command']==.6 and r['seed']==0)
    control = next(r for r in baseline if r['model']=='parent' and r['speed_command']==.6 and r['seed']==0)
    detailed = []
    for row in rows:
        data = trace(row)
        f = data['body_contact_force']
        item = dict(id=row['batch']+'/'+row['id'],
            peak_guide_force_N=float(np.linalg.norm(f[:,data['guide_body_ids']],axis=2).max()),
            peak_chassis_force_N=float(np.linalg.norm(f[:,int(data['base_body_id'])],axis=1).max()),
            peak_torque_env_order_Nm=np.abs(data['torque_env_order']).max(0).tolist())
        if row['primary_air']:
            landing=(data['time']>=row['primary_air']['end']) & (data['time']<=row['primary_air']['end']+1.)
            item['landing_next1s_peak_pitch_deg']=float(np.abs(data['pose_deg'][landing,0]).max())
        if row['config']['air_balance']:
            event = next((e for e in row['events'] if e['phase']=='flight_extend'),None)
            if event:
                i=int(np.searchsorted(data['time'],event['time']-1e-8))
                before=np.linalg.norm(f[max(0,i-8):i],axis=2).sum(1)
                item['preceding_20ms_air_confirmed']=bool(len(before)==8 and (before<1).all())
            if 'leg_pitch_offset' in data:
                item['peak_leg_pitch_offset_rad']=float(np.abs(data['leg_pitch_offset']).max())
        detailed.append(item)
    final_ids={r['batch']+'/'+r['id'] for r in balanced}
    detail_final=[d for d in detailed if d['id'] in final_ids]
    instant_ids={r['batch']+'/'+r['id'] for r in instant}
    detail_instant=[d for d in detailed if d['id'] in instant_ids]
    rejected_ids={r['batch']+'/'+r['id'] for r in rejected}
    detail_rejected=[d for d in detailed if d['id'] in rejected_ids]
    summary=dict(total_cases=len(rows), final_matched_pairs=len(matched),
        airborne=sum(r['genuine_airborne'] for r in balanced),
        full_sequence=sum(r['phase_sequence_completed'] for r in balanced),
        rolling_landing=sum(r['stable_landing'] for r in balanced),
        strict_contiguous_support=sum(r['strict_contiguous_support_landing'] for r in balanced),
        pitch10_roll5_pass=sum(r['within_pitch10_roll5'] for r in balanced),
        baseline_peak_air_pitch_deg=max(r['air_peak_abs_pitch_deg'] for r in baseline),
        balanced_peak_air_pitch_deg=max(r['air_peak_abs_pitch_deg'] for r in balanced),
        baseline_peak_air_roll_deg=max(r['air_peak_abs_roll_deg'] for r in baseline),
        balanced_peak_air_roll_deg=max(r['air_peak_abs_roll_deg'] for r in balanced),
        balanced_rim_peak_range_m=[min(r['primary_air']['peak_paired_rim_z_m'] for r in balanced),max(r['primary_air']['peak_paired_rim_z_m'] for r in balanced)],
        balanced_airtime_range_s=[min(r['primary_air']['duration_s'] for r in balanced),max(r['primary_air']['duration_s'] for r in balanced)],
        improved_pairs=sum(m['reduction_fraction']>0 for m in matched),
        mean_pair_pitch_reduction_fraction=float(np.mean([m['reduction_fraction'] for m in matched])),
        all_final_air_entry_confirmed=all(d['preceding_20ms_air_confirmed'] for d in detail_final),
        final_peak_guide_force_N=max(d['peak_guide_force_N'] for d in detail_final),
        final_peak_chassis_force_N=max(d['peak_chassis_force_N'] for d in detail_final),
        final_landing_next1s_peak_pitch_deg=max(d['landing_next1s_peak_pitch_deg'] for d in detail_final),
        instant_exit_landing_next1s_peak_pitch_deg=max(d['landing_next1s_peak_pitch_deg'] for d in detail_instant),
        rejected_fadeout_landing_next1s_peak_pitch_deg=max(d['landing_next1s_peak_pitch_deg'] for d in detail_rejected),
        rejected_fadeout_cases=len(rejected),
        rejected_fadeout_rolling_landing=sum(r['stable_landing'] for r in rejected),
        selected_end_reasons={x:sum(r['reason']==x for r in balanced) for x in sorted({r['reason'] for r in balanced})},
        max_closure_m=max(r['closure_max_m'] for r in rows),
        reset_reasons={x:sum(r['reason']==x for r in rows) for x in sorted({r['reason'] for r in rows})},
        selected_gains=rep['config'], representative=rep['batch']+'/'+rep['id'],
        training_updates=0, training_seconds=0, default_policy_unchanged=True,
        nominal_mujoco_only=True, native_physx_run=False, real_robot_certified=False,
        stair_transfer_tested=False,
        selected_controller_sha256=hashlib.sha256((T/'air_balance.py').read_bytes()).hexdigest(),
        selected_controller_matches_recorded=all(r['controller_sha256']==hashlib.sha256((T/'air_balance.py').read_bytes()).hexdigest() for r in balanced),
        prior_jump_trial=dict(commit='a82216f9d9c6284a86b7a2cdf866742795e1bdaf',tag='trial-20261114-moving-crouch-jump-01'))
    assert summary['selected_controller_matches_recorded']
    result=dict(summary=summary, groups=groups, matched=matched, details=detailed, rows=rows)
    write_json(T/'RESULTS.json',result)
    print(json.dumps(summary,indent=2),flush=True)
    return result,rep,control


def model_for(row,out):
    scene=next((T/'evidence'/row['batch']/'scene_assets').glob('scene*.xml'))
    tree=ET.parse(scene)
    delivery=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
    for node in tree.getroot().iter():
        for key in ('file','meshdir'):
            value=node.get(key)
            if value and '/delivery/' in value:
                node.set(key,str(delivery/value.split('/delivery/',1)[1]))
            elif value and '/scene_assets/' in value:
                node.set(key,str(scene.parent/value.split('/scene_assets/',1)[1]))
    target=out/'render_scene.xml'
    tree.write(target,encoding='utf8',xml_declaration=True)
    return mujoco.MjModel.from_xml_path(str(target))


def render(rep,control,out):
    data,old=trace(rep),trace(control)
    start=next(e['time'] for e in rep['events'] if e['phase']=='crouch')
    fig,axes=plt.subplots(2,2,figsize=(11,7),constrained_layout=True)
    for row,arr,color,label in [(control,old,'#8b8586','Original jump'),(rep,data,'#147e75','Air balance')]:
        t=arr['time']-start
        use=(t>=-.15)&(t<=1.5)
        axes[0,0].plot(t[use],arr['pose_deg'][use,0],color=color,label=label)
        axes[0,1].plot(t[use],arr['pose_deg'][use,1],color=color,label=label)
        axes[1,0].plot(t[use],arr['qvel_after'][use,4],color=color,label=label)
        axes[1,1].plot(t[use],arr['wheel'][use,:,2].min(1)-.0625,color=color,label=label)
    for ax,title,unit in zip(axes.flat,['Pitch','Roll','Body pitch rate','Paired wheel lower rim'],['degrees','degrees','rad/s','m']):
        ax.set_title(title)
        ax.set_xlabel('Time from crouch (s)')
        ax.set_ylabel(unit)
        ax.grid(alpha=.2)
        ax.axvspan(rep['primary_air']['start']-start,rep['primary_air']['end']-start,color='#a5cfb7',alpha=.2)
    for ax,bound in [(axes[0,0],10),(axes[0,1],5)]:
        ax.axhline(bound,color='#b05442',linestyle='--',linewidth=.8)
        ax.axhline(-bound,color='#b05442',linestyle='--',linewidth=.8)
    axes[0,0].legend(fontsize=9)
    fig.suptitle('Same forward jump | parent | command0.6m/s | seed0',fontsize=13)
    fig.savefig(out/'air_balance_comparison.png',dpi=160)
    plt.close(fig)
    m=model_for(rep,out)
    d=mujoco.MjData(m)
    m.vis.headlight.ambient[:]=[.7,.7,.7]
    m.vis.headlight.diffuse[:]=[.9,.9,.9]
    cam=mujoco.MjvCamera()
    cam.distance=1.5
    cam.azimuth=90
    cam.elevation=-10
    opt=mujoco.MjvOption()
    opt.geomgroup[5]=0
    events={e['phase']:e['time'] for e in rep['events']}
    air=rep['primary_air']
    peak=air['index_start']+int(np.argmax(data['wheel'][air['index_start']:air['index_end'],:,2].min(1)))
    keys=[(start-.1,'A. Forward'),(events['push'],'B. Compressed'),
          (air['start']+.005,'C. Extended takeoff'),(float(data['time'][peak]),'D. Balanced aerial tuck'),
          (air['end']+.01,'E. Landing'),(rep['stable_landing_time']+.25,'F. Recovered rolling')]
    captured=[]
    animation=[]
    def frame(renderer,arr,index):
        d.qpos[:]=arr['qpos_after'][index]
        d.qvel[:]=arr['qvel_after'][index]
        mujoco.mj_forward(m,d)
        cam.lookat[:]=[arr['root'][index,0],arr['root'][index,1],.31]
        renderer.update_scene(d,camera=cam,scene_option=opt)
        return Image.fromarray(renderer.render()).copy()
    with mujoco.Renderer(m,height=360,width=600) as renderer:
        for tt,label in keys:
            i=int(np.abs(data['time']-tt).argmin())
            captured.append((frame(renderer,data,i),i,label))
        for tt in np.arange(start-.2,air['end']+1.,.05):
            pair=[]
            for arr in (old,data):
                i=int(np.abs(arr['time']-tt).argmin())
                pair.append((frame(renderer,arr,i),arr,i))
            animation.append(pair)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    canvas=Image.new('RGB',(1800,960),'white')
    for k,(image,i,label) in enumerate(captured):
        x,y=(k%3)*600,(k//3)*480
        canvas.paste(image,(x,y+38))
    draw=ImageDraw.Draw(canvas)
    for k,(image,i,label) in enumerate(captured):
        x,y=(k%3)*600,(k//3)*480
        draw.text((x+14,y+6),label,font=font,fill='#222222')
        draw.text((x+14,y+410),f't={data["time"][i]:.3f}s  pitch={data["pose_deg"][i,0]:+.1f}deg  roll={data["pose_deg"][i,1]:+.1f}deg',font=small,fill='#222222')
        draw.text((x+14,y+439),f'paired rim={data["wheel"][i,:,2].min()-.0625:.3f}m',font=small,fill='#222222')
    canvas.save(out/'air_balance_keyframes.png')
    frames=[]
    for pair in animation:
        image=Image.new('RGB',(1200,422),'white')
        for j,(picture,arr,i) in enumerate(pair):
            image.paste(picture,(j*600,62))
        draw=ImageDraw.Draw(image)
        for j,(picture,arr,i) in enumerate(pair):
            label='Original jump' if j==0 else 'Air balance'
            draw.text((j*600+12,5),f'{label}  t={arr["time"][i]:.2f}s',font=small,fill='#222222')
            draw.text((j*600+12,31),f'pitch={arr["pose_deg"][i,0]:+.1f}deg  roll={arr["pose_deg"][i,1]:+.1f}deg  vx={arr["vx_body"][i]:.2f}m/s',font=small,fill='#222222')
        frames.append(image)
    frames[0].save(out/'air_balance.gif',save_all=True,append_images=frames[1:],duration=50,loop=0,optimize=False)
    (out/'render_scene.xml').unlink()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--access-dir',required=True)
    a=p.parse_args()
    out=a.out.resolve()
    out.mkdir(parents=True,exist_ok=True)
    result,rep,control=analyze()
    render(rep,control,out)
    sys.path.insert(0,a.access_dir)
    from ssh72 import connect,execute
    client=connect()
    try:
        status,stdout,stderr=execute(client,"date --iso-8601=seconds; pgrep -af '[a]ir_balance.py' || true; nvidia-smi --query-gpu=index,name,memory.used,utilization.gpu --format=csv,noheader; nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory --format=csv,noheader")
        assert status==0
        (T/'evidence/REMOTE_COMPLETION.txt').write_text(stdout+stderr,encoding='utf8')
    finally:
        client.close()
    original_bundle=Path(a.access_dir)/'air_balance_inputs.tar.gz'
    artifacts=[]
    for path in sorted((T/'evidence').rglob('*')):
        if path.is_file() and path.suffix in ('.npz','.msh'):
            artifacts.append(dict(path=str(path),remote_path=REMOTE+'/'+path.relative_to(T).as_posix(),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    artifacts.append(dict(path=str(original_bundle),remote_path=REMOTE+'/inputs.tar.gz',bytes=original_bundle.stat().st_size,sha256=hashlib.sha256(original_bundle.read_bytes()).hexdigest(),manifest='evidence/INPUTS.json'))
    write_json(T/'ARTIFACT_INDEX.json',dict(root=str(T),remote_root=REMOTE,artifacts=artifacts))
    s=result['summary']
    table='\n'.join('| '+g['model']+' | '+('平衡' if g['balanced'] else '原跳跃')+' | '+f"{g['air_peak_pitch_deg']:.2f}"+' | '+f"{g['air_peak_roll_deg']:.2f}"+' | '+str(g['constraint_pass'])+'/'+str(g['cases'])+' | '+str(g['stable_landing'])+'/'+str(g['cases'])+' |' for g in result['groups'])
    pilots='\n'.join('| '+r['config']['id']+' | '+f"{r['air_peak_abs_pitch_deg']:.2f}"+' | '+f"{r['air_peak_abs_roll_deg']:.2f}"+' | '+str(r['stable_landing'])+' |' for r in result['rows'] if r['batch'].startswith(('air_pilot','air_leg','air_exit')))
    text=f'''# 前进跳跃中的空中平衡控制

2026年11月14日，人类追加要求“在空中约束平衡”。在已完成的跳跃版本基础上新建独立版本，不覆盖先前133条轨迹。

最终对照为两个冻结模型、0.4/0.6/0.8m/s指令、各5个初始状态，共30对、60条轨迹。
平衡版空中俯仰峰值从全对照最大{s['baseline_peak_air_pitch_deg']:.2f}度降到{s['balanced_peak_air_pitch_deg']:.2f}度，
侧倾峰值为{s['balanced_peak_air_roll_deg']:.2f}度。全腾空区间满足俯仰±10度且侧倾±5度的为{s['pitch10_roll5_pass']}/30。
真正腾空{s['airborne']}/30，完整压腿/蹬伸/空中收腿/落地时序{s['full_sequence']}/30，滚动落地恢复{s['rolling_landing']}/30。
30个匹配条件中{s['improved_pairs']}个俯仰峰值改善；逐对平均降低{s['mean_pair_pitch_reduction_fraction']*100:.1f}%。

| 模型 | 控制 | 空中最大俯仰/度 | 空中最大侧倾/度 | 10度/5度目标 | 滚动落地恢复 |
| --- | --- | ---: | ---: | ---: | ---: |
{table}

平衡版各例的双轮下沿峰值为{s['balanced_rim_peak_range_m'][0]*100:.2f}–{s['balanced_rim_peak_range_m'][1]*100:.2f}cm，
连续真正腾空{s['balanced_airtime_range_s'][0]:.4f}–{s['balanced_airtime_range_s'][1]:.4f}s。这是轮下沿净空，包含空中收腿贡献。
全腾空区间均按400Hz原始样本评价，包含最初20ms检测延迟，不仅截取控制器已稳定的后半段。

## 控制方法

冻结策略仍控制前进与原平衡。保持原压腿0.50rad/0.30s、蹬伸1.7508938rad、空中收腿0.20rad、下降伸腿1.35rad和落地0.30s返回策略。
连续8个2.5ms采样外部接触力范数和<1N并向上运动后才确认腾空，再允许空中反馈。本次最终腾空入口条件逐条核验为{s['all_final_air_entry_confirmed']}。

空中反馈同时利用现有电机：

- 俯仰轮反作用请求为body torque=-8*pitch-1*pitch_rate，等分反向请求到双轮；经原0.6轮速伺服换算成速度目标。
- 两侧腿共同角偏移=2*pitch+0.20*pitch_rate，限制在±0.35rad。它调整前后腿的共同角度，保留蹬伸/收腿的前后关节差。
- 左右腿差动=0.6*roll+0.08*roll_rate，限制在±0.15rad；左右分别反向，实际腿目标继续钳制到原差值范围。
- 落地接触后返回原策略；另试过0.30s渐退补偿，因完整复测恶化而拒绝，最终采用此前已验证的直接退出版本。
- 全部请求经过原action clip6、连续角目标钳制、PD和原电机电压/扭矩/转速包络。没有改变物理资产、重力或姿态积分。

前一组只用轮反作用，俯仰只能从20.31度改善到18.26度；加大增益会令轮速接近原空载/指令上限，并未继续改善。
加入腿的共同角反馈后先导例降到6.40度。最终固定这组腿参数，并加入已经单独试过的小幅左右腿反馈，进行完整60条匹配复测。
这属于反馈控制器实验，actor/critic及默认策略没有学习或替换，optimizer updates=0，新增训练预算消耗0秒。

## 全部先导结果

| 参数ID | 空中最大俯仰/度 | 空中最大侧倾/度 | 滚动落地恢复 |
| --- | ---: | ---: | --- |
{pilots}

负反馈方向探针leg_negative恶化到约32.56度，保留为失败对照；轮增益较大的失败目标也全部保留。
本阶段共{s['total_cases']}条实际轨迹，原RESULT.json与NPZ均保留。未把未达到10度目标的配置写成通过。

## 物理、落地与适用范围

使用HW300N60 R3原资产，MJCF SHA256=77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f；teacher715c40b6、parentdb6e9ccf。
策略35/6、2.5ms物理、50Hz策略、100Hz腿、400Hz轮，腿40Nm及轮5.7759098Nm平台和原DC包络均保持。
原每轴40度/0.2s、底盘/非豁免导轮接触与10mm闭链单episode重置仍生效。闭链误差最大{s['max_closure_m']*1000:.4f}mm。
最终平衡版导轮/底盘接触峰值分别{s['final_peak_guide_force_N']:.1f}/{s['final_peak_chassis_force_N']:.1f}N。
实际结束原因分布为{s['reset_reasons']}。

“滚动落地恢复”沿用原0.5s判据：每只轮支撑占比>=80%、整机无支撑间隙<20ms、pitch/roll<15度、
根高度变化<=30mm、根竖直速度<=0.30m/s、底盘/导轮接触<1N。逐样本双轮连续承重的严格指标仍单独保存，平衡版为{s['strict_contiguous_support']}/30。
落地交接另做4条瞬间退出/0.30s渐退先导对照，再做30条渐退版复测。渐退版虽在先导条件稍好，完整复测只有{s['rejected_fadeout_rolling_landing']}/30滚动落地恢复，10次后续冲出场地，已拒绝。
最终选回30/30恢复且无重置的直接退出版本，结束原因为{s['selected_end_reasons']}。其落地后1秒内全组最大俯仰仍有{s['final_landing_next1s_peak_pitch_deg']:.2f}度，
拒绝的渐退版为{s['rejected_fadeout_landing_next1s_peak_pitch_deg']:.2f}度。落地后的姿态不宣称满足空中±10度目标；落地冲击与回摆仍是未完成项。

这是MuJoCo名义物理结果；本阶段没有新PhysX/实机验证或新训练模型，也未对平衡版新增台阶复测。
前一跳跃试验200mm首阶及双阶仍为0；本阶段空中姿态改善不等于已能登阶。默认模型保持db6。
未操作210号机的训练或用户原查看窗口。本次所有评测进程自然结束，主机完成回执在evidence/REMOTE_COMPLETION.txt。

## 工作区与复现

远端：`{REMOTE}`。
本机：`{T}`。
air_balance.py为已验证并选回的直接退出空中反馈；base_jump.py冻结上一版本的跳跃；final_configs.json保存最终选中参数，verify_configs.json保存30对对照参数。
reference/air_balance_wheel_only_v1.py及pilot_configs.json保留最初轮反馈源码；leg_pilot_configs.json保留第二阶段全部增益。
reference/air_balance_instant_exit_v2.py、exit_configs.json保留交接渐退修改前源码与对照。
reference/air_balance_failed_fadeout_v3.py保留被拒绝渐退版源码，air_final_*_r5保留其30条实际失败/成功轨迹，目录名是原尝试名，不代表最终被采纳。
reports/fadeout_candidate_reader_r1.md/json保留错误候选读者输出；该读者一度将渐退版作为最终候选，并用了“降低”字样，即使统计数值已经变差，本报告已纠正。原错误文件不改写。
最初75例阶段的临时聚合报告被后一次读者覆盖，未保留其原始字节SHA；该报告字节历史存在缺口，75例独立RESULT.json/NPZ和全部源代码均在。本报告的最终选中方案即由其中60条匹配轨迹重新汇总，无动力学重跑。
evidence/INPUTS.json与ARTIFACT_INDEX.json索引完整来源、原件SHA、字节数和两端位置。动画使用保存的真实qpos并列渲染相同时间。
力/几何在积分步开始，保存qpos在积分步末，视觉与力采样相差2.5ms，原时钟未插入mj_forward改变动力学。
所有代码、报告、失败和媒体通过record_experiment.py形成独立annotated trial；Git远端验证作为工具回执保存。
前阶段已验证提交a82216f9d9c6284a86b7a2cdf866742795e1bdaf，tag=trial-20261114-moving-crouch-jump-01。
'''
    (T/'FINAL_REPORT.md').write_text(text,encoding='utf8')
    media=T/'media'
    media.mkdir(exist_ok=True)
    for path in out.iterdir():
        if path.suffix in ('.png','.gif'):
            shutil.copy2(path,media/path.name)
    for name in ('FINAL_REPORT.md','RESULTS.json','ARTIFACT_INDEX.json'):
        shutil.copy2(T/name,out/name)


if __name__=='__main__':
    main()
