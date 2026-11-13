"""Preserve every attempt, measured limits, source revision and user deliverable."""
from pathlib import Path
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
import shutil
import sys
import tarfile

import numpy as np

from analyze_and_render import analyze, read_trace
from moving_jump import write_json

T = Path(__file__).resolve().parent
R = T.parents[2]
REMOTE = '/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_MOVING_CROUCH_JUMP_20261113_R1'
p = argparse.ArgumentParser()
p.add_argument('--out', type=Path, required=True)
p.add_argument('--access-dir', required=True)
a = p.parse_args()
out = a.out.resolve()
out.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, a.access_dir)
from ssh72 import connect, execute

result = analyze()
rows = result['rows']
final = [r for r in rows if r['batch'].startswith('flat_confirmed')]
stairs = [r for r in rows if r['terrain']=='stairs']
final_stairs = [r for r in stairs if r['batch'].startswith('stairs_confirmed')]
assert len(final) == 30 and len(final_stairs) == 6
assert all((T/'evidence'/r['batch']/'COMPLETE.json').is_file() for r in rows)

client = connect()
try:
    sftp = client.open_sftp()
    sftp.get(REMOTE+'/flat_pilot_teacher_r1.log', str(T/'evidence/invalid_launcher_r1.log'))
    sftp.close()
    status, stdout, stderr = execute(client,
        "date --iso-8601=seconds; pgrep -af '[m]oving_jump.py' || true; "
        "nvidia-smi --query-gpu=index,name,memory.used,utilization.gpu --format=csv,noheader; "
        "nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory --format=csv,noheader")
    assert status == 0
    (T/'evidence/REMOTE_COMPLETION.txt').write_text(stdout+stderr, encoding='utf8')
finally:
    client.close()

with tarfile.open(Path(a.access_dir)/'moving_jump_inputs.tar.gz', 'r:gz') as tar:
    (T/'reference/remote_io_v1.py').write_bytes(tar.extractfile('remote_io.py').read())
write_json(T/'evidence/ATTEMPT_NOTES.json', dict(
    invalid_launch=dict(id='flat_pilot_teacher_r1', status='invalid_launcher_no_simulation',
        error='A Windows Path converted the literal Linux runtime path into backslashes.',
        source='reference/remote_io_v1.py', log='evidence/invalid_launcher_r1.log',
        replacement='flat_pilot_teacher_r2', training_seconds=0, environment_episodes=0),
    reader_v1=dict(status='original_strict_false_preserved', source='reference/runner_v1.py',
        original_cases=7, detail='The first reader required uninterrupted400Hz paired support for0.5s. '
        'Normal rolling has contact micro gaps. Original RESULT.json files are unchanged. '
        'The rolling criterion and its full measurements are reported separately.'),
    timing_v2=dict(source='reference/runner_v2.py', detail='The3.2s earliest stair trigger '
        'collapsed some lead40/50 trials onto one starting state. Results remain separate actual attempts; '
        'the2.3s trigger revision was tested in18 new cases, with no first-step success.'),
    aerial_trigger_v3=dict(source='reference/runner_v3.py', detail='Single-sample unsupported '
        'phase detection could precede continuous flight. Saved physical trajectories did include '
        'real flight, but final controller requires8 consecutive2.5ms unsupported samples. '
        'Final validation is30 new flat cases and6 new stair cases. Earlier maxima are not final maxima.')))

metrics = []
for row in rows:
    data = read_trace(T/row['trajectory'])
    t = data['time']
    events = {e['phase']:e['time'] for e in row['events']}
    f = data['body_contact_force']
    entry = dict(id=row['batch']+'/'+row['id'],
                 peak_abs_torque_env_order=np.abs(data['torque_env_order']).max(0).tolist(),
                 peak_guide_contact_N=float(np.linalg.norm(f[:, data['guide_body_ids']], axis=2).max()),
                 peak_chassis_contact_N=float(np.linalg.norm(f[:, int(data['base_body_id'])], axis=1).max()))
    if row['primary_air']:
        air = row['primary_air']
        peak = air['index_start']+int(np.argmax(data['wheel'][air['index_start']:air['index_end'], :, 2].min(1)))
        start = int(np.abs(t-events['crouch']).argmin())
        compressed = int(np.abs(t-events['push']).argmin())
        entry.update(air=air, actual_vx_at_crouch_m_s=float(data['vx_body'][start]),
            root_height_at_crouch_m=float(data['root'][start, 2]),
            root_height_compressed_m=float(data['root'][compressed, 2]),
            root_height_peak_m=float(data['root'][:, 2].max()),
            com_height_at_crouch_m=float(data['com'][start, 2]),
            com_height_peak_m=float(data['com'][:, 2].max()),
            paired_rim_peak_m=float(data['wheel'][peak, :, 2].min()-.0625),
            peak_wheel_x_from_first_edge_m=(data['wheel'][peak, :, 0]+2.9).tolist(),
            hip_to_wheel_compressed_m=data['hip_to_wheel'][compressed].tolist(),
            hip_to_wheel_at_takeoff_m=data['hip_to_wheel'][air['index_start']].tolist(),
            hip_to_wheel_tucked_m=data['hip_to_wheel'][peak].tolist(),
            actual_delta_compressed=data['leg_delta_actual'][compressed].tolist(),
            actual_delta_at_rim_peak=data['leg_delta_actual'][peak].tolist(),
            rolling_landing_window=row['rolling_landing_window'],
            peak_total_wheel_force_N=float(np.linalg.norm(f[:, data['wheel_body_ids']], axis=2).sum(1).max()))
    if 'flight_extend' in events:
        before = int(np.searchsorted(t, events['flight_extend']-1e-8))
        window = np.linalg.norm(f[max(0, before-8):before], axis=2).sum(1)
        entry['preceding_20ms_air_confirmed'] = bool(len(window)==8 and (window<1.).all())
        entry['preceding_20ms_contact_peak_N'] = float(window.max(initial=0))
    metrics.append(entry)

by_id = {m['id']:m for m in metrics}
final_metrics = [by_id[r['batch']+'/'+r['id']] for r in final]
confirmed_count = sum(m['preceding_20ms_air_confirmed'] for m in final_metrics)
assert confirmed_count == len(final_metrics)
rep = next(r for r in final if r['model']=='parent' and r['speed_command']==.6 and r['seed']==0)
rm = by_id[rep['batch']+'/'+rep['id']]
stair_active = [r for r in stairs if not r['baseline']]
stair_best = max(stair_active, key=lambda r: r['primary_air']['peak_paired_rim_z_m'])
sm = by_id[stair_best['batch']+'/'+stair_best['id']]
summary = dict(total_cases=len(rows), invalid_launches=1,
    flat_final_cases=len(final), flat_final_airborne=sum(r['genuine_airborne'] for r in final),
    flat_final_full_sequence=sum(r['phase_sequence_completed'] for r in final),
    flat_final_rolling_landing=sum(r['stable_landing'] for r in final),
    flat_final_strict_contiguous_support=sum(r['strict_contiguous_support_landing'] for r in final),
    flat_final_air_confirmed_before_tuck=confirmed_count,
    flat_final_airtime_range_s=[min(r['primary_air']['duration_s'] for r in final), max(r['primary_air']['duration_s'] for r in final)],
    flat_final_paired_rim_peak_range_m=[min(m['paired_rim_peak_m'] for m in final_metrics), max(m['paired_rim_peak_m'] for m in final_metrics)],
    flat_final_crouch_vx_range_m_s=[min(m['actual_vx_at_crouch_m_s'] for m in final_metrics), max(m['actual_vx_at_crouch_m_s'] for m in final_metrics)],
    flat_final_peak_abs_pitch_roll_deg=np.max([r['peak_abs_pitch_roll_deg'] for r in final], axis=0).tolist(),
    stairs_all_cases=len(stairs), stairs_active_cases=len(stair_active), stairs_final_cases=len(final_stairs),
    first_step_stable=sum(r['first_step_stable'] for r in stairs),
    second_step_stable=sum(r['second_step_stable'] for r in stairs),
    max_closure_all_m=max(r['closure_max_m'] for r in rows),
    guard_reset_reasons={x:sum(r['reason']==x for r in rows) for x in sorted({r['reason'] for r in rows})},
    nominal_frozen_replay_only=True, native_physx_run=False, optimizer_updates=0,
    training_budget_seconds=0, default_policy_unchanged='db6e9ccf',
    representative=rm, stair_highest_rim=sm)
write_json(T/'METRICS.json', dict(summary=summary, cases=metrics))

media = T/'media'
media.mkdir(exist_ok=True)
for file in out.iterdir():
    if file.suffix in ('.png', '.gif'):
        shutil.copy2(file, media/file.name)

artifacts = []
for path in sorted((T/'evidence').rglob('*')):
    if not path.is_file() or path.suffix not in ('.npz', '.msh'):
        continue
    rel = path.relative_to(T).as_posix()
    artifacts.append(dict(path=str(path), remote_path=REMOTE+'/'+rel, bytes=path.stat().st_size,
                          sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                          storage='original_on_both_hosts_sha_index_in_git'))
archive = Path(a.access_dir)/'moving_jump_inputs.tar.gz'
artifacts.append(dict(path=str(archive), remote_path=REMOTE+'/inputs.tar.gz',
    bytes=archive.stat().st_size, sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
    storage='full_original_runtime_plant_and_frozen_weights_bundle', manifest='evidence/INPUTS.json'))
write_json(T/'ARTIFACT_INDEX.json', dict(root=str(T), remote_root=REMOTE, artifacts=artifacts))

names = {'approach':'前进', 'crouch':'压腿', 'push':'蹬伸', 'flight_extend':'确认腾空后伸腿',
         'flight_tuck':'空中收腿', 'landing_extend':'下降伸腿准备落地', 'recover':'落地恢复', 'done':'返回冻结策略'}
start = rep['events'][0]['time']
timeline = '\n'.join('| '+names[e['phase']]+' | '+f"{e['time']-start:.3f}"+' | '
    +f"{e['root'][2]:.3f}"+' | '+f"{e['vx']:.3f}"+' |' for e in rep['events'])
table = '\n'.join('| '+g['batch']+' | '+str(g['cases'])+' | '+str(g['airborne'])+' | '
    +str(g['stable_landing'])+' | '+str(g['first_step'])+' |' for g in result['groups'])
lo, hi = summary['flat_final_paired_rim_peak_range_m']
alo, ahi = summary['flat_final_airtime_range_s']
report = f'''# 前进压腿、蹬伸起跳、空中收腿、落地：实测报告

试验于2026年11月13日开始，跨日至11月14日完成，时区Asia/Shanghai。

**最终版在平地实现了用户要求的完整动作。** 两个冻结模型、0.4/0.6/0.8m/s指令、
每档5个初始姿态，共30次，真正腾空、完整时序及滚动落地恢复均为30/30。
最终版双轮下沿最高距地{lo*100:.2f}–{hi*100:.2f}cm，连续无承重接触{alo:.4f}–{ahi:.4f}s。
这里的高度是双轮下沿的净空，包含空中收腿贡献；不能当作质心上升量或台阶技能高度。

**200mm台阶仍未成功。** 共{len(stairs)}条台阶轨迹，其中{len(stair_active)}次动作尝试、6次原策略对照；
首阶及双阶稳定成功都为0。最终连续20ms腾空确认版另做6次，同样没有落稳首阶。
因此本次成立的是前进中的平地跳跃动作，默认策略仍为db6，未晋级或替换模型。

## 工作区与范围

- 主机：lc01@10.24.0.72，hostname=amax，双RTX4090。
- 独立远端目录：`{REMOTE}`。
- 本机版本：`{T}`。
- 使用原HW300N60 R3资产；MJCF SHA256为77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f。
- 冻结teacher=715c40b6…、parent=db6e9ccf…；未训练，optimizer updates=0，新增训练预算消耗0秒。
- 本次为MuJoCo名义物理评测，不包含新PhysX结果、随机化训练或实机试验。动作前速度由冻结策略自然形成。
- 未向210号机训练或用户原查看窗口发任何控制操作。所有本次进程已自然结束，完成回执保留。

## 最终动作

动作在前进中触发。腿前后关节差目标从冻结策略的站姿渐变到0.50rad，压腿目标时长0.30s；
随后蹬到原允许上限1.7508938rad。所有外部接触力范数之和连续8个2.5ms采样均<1N，
且机体竖直速度>0.10m/s，才确认进入腾空。保持短时伸腿后收至0.20rad；下降时伸至1.35rad，
接触后在0.30s内回到冻结策略。实际相位切换受50Hz控制采样影响，并非所有时长都精确等于目标。
四个腿动作保留策略原有的每对关节均值，轮子仍由策略控制。

最终30条轨迹已逐条回读，腾空相位入口前20ms无承重条件为{confirmed_count}/30。
动作开始时实际前向速度范围为{summary['flat_final_crouch_vx_range_m_s'][0]:.3f}–{summary['flat_final_crouch_vx_range_m_s'][1]:.3f}m/s，
和速度指令分别记录。没有人工注入速度、上抬机体、外力或瞬移。

代表例：parent、0.6m/s指令、初始姿态0，最终版。

| 阶段 | 自压腿开始/s | 机体根高度/m | 实际前向速度/m/s |
| --- | ---: | ---: | ---: |
{timeline}

该例压腿使根高度从{rm['root_height_at_crouch_m']:.3f}m降到{rm['root_height_compressed_m']:.3f}m；
质心峰值{rm['com_height_peak_m']:.3f}m，压腿开始时质心为{rm['com_height_at_crouch_m']:.3f}m。
连续腾空期间质心继续上升{rm['air']['com_rise_m']:.3f}m，水平前移{rm['air']['dx_m']:.3f}m；
双轮下沿最高{rm['paired_rim_peak_m']:.3f}m，连续腾空{rm['air']['duration_s']:.4f}s。
髋到轮心距离在压腿/腾空入口/最大净空处分别约为
{np.mean(rm['hip_to_wheel_compressed_m']):.3f}/{np.mean(rm['hip_to_wheel_at_takeoff_m']):.3f}/{np.mean(rm['hip_to_wheel_tucked_m']):.3f}m。
整段地面支撑中导轮与底盘的最大接触力分别为{rm['peak_guide_contact_N']:.1f}/{rm['peak_chassis_contact_N']:.1f}N。
该例双轮合接触力单个2.5ms采样峰值约{rm['peak_total_wheel_force_N']:.0f}N，落地仍有明显冲击和回弹，
不据此宣称缓冲已经优化。

## 落地判据与原始失败

原第一版读者要求每个400Hz采样点双轮都>5N并持续0.5s。普通滚动也有微小接触间隙，
因此该严格指标仍单独保留；最终版按此指标为{summary['flat_final_strict_contiguous_support']}/30，未改写成成功。

报告中的“滚动落地恢复”指落地后的一个0.5s窗口：每只轮子的支撑占比>=80%，
整机无支撑间隙<20ms，pitch/roll均<15度，根高度变化<=30mm，根竖直速度绝对值<=0.30m/s，
底盘/导轮接触均<1N。每条实际窗口及占比写入METRICS.json及原RESULT.json。
代表例的实际每轮支撑占比为{rm['rolling_landing_window']['per_wheel_support_duty']}。
这是一种带间歇轮地接触的运动恢复判断，不能描述为双轮连续不间断承重。

第一版7条RESULT.json、原始读者false、启动路径错误日志和全部源码修订均保留。
早期单采样腾空触发版本曾测得约28.5cm净空，最终20ms确认版的峰值应使用上面的最终范围。
早期0.42m高度指令的两个teacher例在落地后冲出场地，tile_boundary重置照实保留，未选为最终方案。

## 台阶失败的几何证据

最高轮下沿的台阶例为`{stair_best['batch']}/{stair_best['id']}`：
下沿高{sm['paired_rim_peak_m']:.3f}m，但两轮中心相对首阶边缘仍是
{sm['peak_wheel_x_from_first_edge_m'][0]:+.3f}/{sm['peak_wheel_x_from_first_edge_m'][1]:+.3f}m，仍在边缘外侧。
其腾空中质心水平位移为{sm['air']['dx_m']:+.3f}m。
其他失败也能看到在台阶前起跳偏早或接近阶段减速/后退，下降前没有同时满足越缘和顶面承重。
没有把导轮碰边、轮子仅高于台阶或机体局部越缘记成登阶成功。

| 组别 | 轨迹数 | 动作真正腾空数 | 滚动落地恢复数 | 首阶成功数 |
| --- | ---: | ---: | ---: | ---: |
{table}

共{len(rows)}条真实物理轨迹，外加1次未进入模拟的无效启动。所有轨迹原件在两端保存，SHA/字节数/位置见ARTIFACT_INDEX.json。

## 未改的物理与保护

35维策略输入、6维输出；2.5ms物理、50Hz策略、100Hz腿、400Hz轮。
腿电机原40Nm平台及53.333333Nm堵转、16.75516rad/s空载包络；轮原5.7759098Nm平台及28.1852538Nm堵转、55.3557319rad/s空载包络。
保留连续关节目标钳制、原刚度/阻尼、闭环实体、碰撞与摩擦、每轴40度持续0.2s、底盘及非豁免导轮接触规则。
按仓库记录的人类2026-11-01更新，新实验闭链episode重置阈值为10mm；旧2mm试验未改。
本次全部轨迹的闭链误差峰值仅{summary['max_closure_all_m']*1000:.4f}mm，未发生闭链或非有限重置。
高度指令上限仍为0.42m。最终动作采用0.36m，未把指令上限称为机械最大高度。

## 复现与归档

完整输入原件清单见evidence/INPUTS.json；最初完整运行包在独立远端inputs.tar.gz及本机work中，均有SHA索引。
moving_jump.py为最终控制器；reference/runner_v1.py、runner_v2.py、runner_v3.py保留旧动作/读者；
selected_flat_config.json和final_stair_config.json为最终参数。每条轨迹都有独立batch/id、原RESULT.json和400Hz NPZ。
动画及关键帧取自保存的实际qpos，未重新驱动机器人或替换姿态；渲染相机跟随机体，动画标注世界x和实际前向速度。
视觉上取的qpos为积分步末，比力/几何采样晚2.5ms，这一时钟差在原数据中保留。

本阶段所有源码、配置、报告、失败及媒体经record_experiment.py形成独立annotated trial，
远端branch/tag/tag peeled/main验证以工具回执为准。默认模型没有改变，无新PT需要交付。
'''
(T/'FINAL_REPORT.md').write_text(report, encoding='utf8')
write_json(T/'RESULTS.json', dict(summary=summary, groups=result['groups'], source_analysis='ANALYSIS.json',
    all_cases=rows, real_robot_certified=False, native_physx_run=False, deployment_changed=False))
for filename in ('FINAL_REPORT.md', 'RESULTS.json', 'ARTIFACT_INDEX.json', 'METRICS.json'):
    shutil.copy2(T/filename, out/filename)
print(json.dumps(summary, indent=2), flush=True)
