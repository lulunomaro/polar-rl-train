"""Compile preserved data/static evidence into an independent R00 diagnosis."""
from pathlib import Path
import ast,hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parent

def js(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def link(p,label=None,lines=None):
    p=Path(p);suffix='' if lines is None else '#L'+lines
    return '['+(label or p.name)+'](<'+p.as_posix()+suffix+'>)'

def main():
    report=OUT/'R00_DATA_DIAGNOSTIC.md';index=OUT/'DATA_DIAGNOSTIC_INDEX.json';assert not report.exists() and not index.exists()
    p=js(OUT/'PACKET_DIAGNOSTIC.json');q=js(OUT/'PACKET_QUICK_SUMMARY.json');c=js(OUT/'CONDITIONED_QUICK_SUMMARY.json');s=js(OUT/'STATIC_FRAME_GEOMETRY.json');cond=js(OUT/'CONDITIONED_DYNAMICS.json')
    f=q['r00_forward_nominal_sensors']['tail'];sp=q['r00_spin_nominal_sensors']['tail'];fs=c['r00_forward_nominal_sensors'];ss=c['r00_spin_nominal_sensors'];base=s['actual_model_FK_geometry_samples'][0]
    L=[];a=L.append
    a('# R00 forward/spin 失败的独立 source/data-only 诊断\n')
    a('## 结论先行\n')
    a('1. **forward尾约0.15rad倾角偏置，主要可定位到动态specific-force姿态纠正路径，而不是本批100Hz gyro积分漏掉0.15rad。** 对相同已保存packets重放冻结估计器，14状态逐元素最大差0；仅用同一rawgyro、真实reset姿态初始化，尾pitch RMSE为0.00522662rad；原冻结估计器为0.15025583rad。该对照只定位记录轨迹上的算法误差，不是关掉acc校正后新闭环物理通过。')
    a('2. **spin的速度估计与无滑轮测量适用条件失效证据更强。** 尾200帧contact_proxy全0，源码仍无条件wheel-KF更新；其中176帧两轮均未满足原>1N支撑记录。原估计vx RMSE=1.42385m/s，报告std均值仅0.04443m/s。只修gyro采样或姿态初始化并不解决这条记录上的主要速度误差。')
    a('3. **IMU主惯性轴混用假说未被本轮数据支持。** site quat为identity，3组静态重力方向和3组已知body角速度校验通过，site与chassis R相同；惯性iquat另有定义，非传感器坐标。')
    a('4. **存在强0.5ms子步stage混采证据，已与10ms整行差分开。** 对齐轮中点的encoder-FK vs日志差，在forward尾由1.32605mm经一阶末子步修正降至0.000768mm；spin由0.57458mm降至0.001128mm。')
    a('5. **轮中点/wholeCOM与chassis origin参考确实不同，但不能用4π命令代替实际ω解释R00。** 初态两者x约−34.2024mm，若真的绕其4π纯转，origin残留向心模板x约−5.401m/s²；R00 spin尾实际yaw约0.613rad/s，对应轮中点yaw-only模板RMS仅0.02014m/s²。\n')
    a('## 1. 输入、来源固定与时间对齐\n')
    a('读取R00冻结 '+link(ROOT/'source_snapshots/r00/sensor_core.py')+'、'+link(ROOT/'source_snapshots/r00/physics_bridge.py')+'、'+link(ROOT/'source_snapshots/r00/run_ground_case.py')+'，与两case的SOURCE_MANIFEST逐文件SHA核对。原两case '+link(ROOT/'results/r00_forward_nominal_sensors/result.json','forward原结果')+' / '+link(ROOT/'results/r00_spin_nominal_sensors/result.json','spin原结果')+'、原trace及父 '+link(ROOT/'reports/r00_first_six_analysis.json')+'均保持不变。\n')
    a('每行estimator输入时刻为sensor_timestamp_s，输出行time是执行下一10ms动作后的时刻。本文用前一行grade作该packet真值，首包t=0姿态来自已冻结gain/reset定义。验证rawgyro与前一行grade.gyro逐元素完全相同，time−sensor_timestamp−0.01最大偏差约浮点舍入。原结果中同row对比的RMSE在本报告重新校时；没有把10ms相位差当新bias。\n')
    a('|尾200帧（post time≥6s）|forward|spin|\n|---|---:|---:|\n|原物理尾vx m/s|2.613284|−1.099958|\n|原物理尾yaw rad/s|0.002649|0.612849|\n|校时pitch估计RMSE rad|0.15025583|0.01878764|\n|校时vx估计RMSE m/s|0.12777624|1.42385185|\n|两轮原>1N支撑帧|3/200|1/200|\n|至少一轮支撑帧|54/200|24/200|\n|原post非轮接触帧|0/200|6/200（全8s为35）|\n')
    a('所有本报告派生运算仅使用既有记录。没有新physics step、rollout、DR重跑或父代码改写。静态frame/FK允许mj_forward，不构成新物理试验。\n')
    a('## 2. 最小可证：forward姿态纠正受动态加速度污染\n')
    a('冻结估计器的 '+link(ROOT/'source_snapshots/r00/sensor_core.py','姿态与KF更新', '110-L123')+' 先把IMU properaccel补到chassis origin，再减去`expected=[filtered_wheel_acc, omega_z*vx_est, 0]`；剩余量按norm接近g的置信度当up方向纠正姿态。补到origin不等于从properaccel中去除了origin平移、竖直冲击和完整转动加速度。\n')
    a('|相同packet离线重放（不改原轨迹）|forward尾pitch RMSE rad|spin尾pitch RMSE rad|\n|---|---:|---:|')
    for name,label in [('original','原冻结算法'),('truth_init','仅初始化用真实reset姿态'),('gyro_only_truth_init','真实reset初始化＋gyro-only'),('gyro_only_original_init','原rawacc初始化＋gyro-only')]:
        a('|'+label+'|'+f"{f['offline_variants'][name]['pitch_error']['rms']:.8f}"+'|'+f"{sp['offline_variants'][name]['pitch_error']['rms']:.8f}"+'|')
    a('\n- 首包rawacc=(-2.77343,−0.01038,24.11739)m/s²，norm=24.27633，confidence=0；但first-update仍直接据此初始化pitch=+0.114494rad，而已知reset真实pitch=0。首次dt=0，因此该误差来自初始化，不是gyro积分。')
    a('- 仅修此初始化时forward尾RMSE仍0.15172rad，故它不是尾bias的充分解释。')
    a('- forward尾rawacc norm范围0.486–61.183m/s²，姿态候选−真实up的逐轴RMS=(5.671,8.580,10.497)m/s²；source confidence>0仍占46.5%。')
    a('- 按算法自身confidence加权的acc候选pitch−真pitch均值 **−0.184075rad**，而实际估计bias均值−0.150050rad。记录中body-Y姿态纠正率积分为−0.268962rad；与初始化+0.114494及最终约−0.15的方向一致（不是把body积分在任意旋转下当精确Euler分解）。')
    a('- spin中原acc校正反而将gyro-only尾pitch RMSE从0.03579降至0.01879；因此“统一禁用acc校正”不是由两case支持的通用解决方案。\n')
    a('## 3. Gyro采样/预积分：有误差与高频风险，但归因要分量级\n')
    a('由校时root R相邻姿态计算`log(R_kᵀR_{k+1})/dt`，再与rawgyro左端、右端、梯形平均比较；另从真实reset R积分整条rawgyro quaternion，避免以Euler pitch导数替代body角速度。\n')
    a('|尾统计|forward|spin|\n|---|---:|---:|\n|右端gyro-only pitch RMSE rad|0.00522662|0.03579002|\n|右端gyro-only SO(3)误差RMSE rad|0.00660604|0.06230234|\n|右端gyro−root区间平均ω RMS x/y/z rad/s|(0.09509,0.05123,0.02685)|(0.14831,0.23169,0.10447)|\n|梯形gyro−root区间平均ω RMS x/y/z rad/s|(0.03440,0.01361,0.01613)|(0.09386,0.14409,0.07353)|\n')
    a('实际轮mesh有24个径向polygon侧面；按记录的绝对wheel-y角速度推算几何facetpass频率，forward尾左右均值约166.06/168.03Hz（范围约152–201Hz），高于100Hz采样Nyquist50Hz。该数是几何激励率模板，不是已经测得>50Hz频谱。只有100Hz瞬时数据时，高频内容及其别名并不唯一可逆。\n')
    a('建议下一采样链保留实际物理/ADC高频IMU时间戳与预积分Δθ/Δv、窗内方差/冲击统计，控制100Hz消费这些窗统计；以1kHz真实INS或现有0.5ms physics stage作采样结构参考。后续应验证高频链带来的闭环变化，而不是声称本文已通过高频物理测试。当前forward约0.15rad主要来自acc纠正路径的归因，不应被“100Hz gyro alias”一词覆盖。\n')
    a('## 4. Spin速度KF在无支撑/滑移时仍假设轮无滑\n')
    a('源码 '+link(ROOT/'source_snapshots/r00/sensor_core.py','wheel-KF更新', '117-L123')+' 仅按左右轮速度不一致提高R（封顶31倍），每包都做wheel update；contact_proxy是更新之后才构造的返回字段，没有用于禁止或改写此次wheel测量。左右轮一致并不能证明两轮都在地面无滑。\n')
    a('|spin尾条件（按packet时刻的原>1N真支撑分类）|n|wheel-mean测量vx误差RMSE m/s|KF vx误差RMSE m/s|\n|---|---:|---:|---:|')
    for name,label in [('both_supported','双轮支撑'),('one_supported','仅一轮支撑'),('neither_supported','两轮均不支撑'),('source_contact_proxy_zero','source contact_proxy=0')]:
        cc=ss['conditioned'][name];a('|'+label+'|'+str(cc['n'])+'|'+f"{cc['wheel_mean_vx_measurement_error']['rms']:.6f}"+'|'+f"{cc['KF_vx_error']['rms']:.6f}"+'|')
    a('\n双轮支撑仅1帧，不能据其单点统计推断一般性能。spin尾估计vx误差总RMS=1.42385m/s，而报告std均值0.04443m/s，误差相对自身std的RMS约31.95；forward约6.27。该协方差未覆盖当前接触模式失配。')
    a('改回硬件名义半径0.0625的同包数学变化：forward wheel-mean约−0.05248m/s，spin均值+0.01135m/s；量级不足解释spin约1.42m/s估计误差，不能以换半径替代接触/滑移模型。')
    a('建议基于真实可读IMU、编码器、轮/电机响应的接触/飞行/滑移检测来切换或降权wheel观测，维护失配协方差；离线真支撑分类只作诊断，绝不移入可部署控制输入。\n')
    a('## 5. 0.5ms stage混采的独立证据\n')
    a('冻结 '+link(ROOT/'source_snapshots/r00/physics_bridge.py','sensor_packet与grade', '25-L42')+' 的encoder直接取当前qpos/qvel，grade通过旧 '+link(ROOT.parent/'traditional_control_20261101/control_core.py','health', '163-L167')+' 同时读取当前qpos xyz、已计算的xpos/xmat。末次mj_step后未重新统一采样kinematics/sensordata，存在末子步stage与积分后状态的时刻差。\n')
    a('独立验证：从packet的hip/crank用纯几何FK得到wheelmid_B；日志用校时grade的`Rᵀ(mean(wheel_xyz)-xyz)`得到另一wheelmid_B。用编码器导数求relative wheel velocity，以`(v_origin_body+v_relative_FK)*0.0005`修正两者差：\n')
    a('|尾RMS轮中点差|修正前 m|一阶修正后 m|\n|---|---:|---:|\n|forward|0.0013260548|0.0000007685|\n|spin|0.0005745767|0.0000011280|\n')
    a('该数值强支持0.5ms阶段混采，不是模型frame错误；仍是记录上的一阶对照，未保存每个子步状态，不能宣称恢复了全部高频真实状态。下阶段应明确IMU、encoder、root/geom grading各自的真实采样时间或统一到同一stage。该改造独立于整行10ms校时，也不单独解释forward的0.15rad。\n')
    a('## 6. IMU frame / wholeCOM / wheelmid参考核定\n')
    a('实际site quat=identity，虽chassis惯性principal iquat近(−.005,.716,.0056,.698)，二者不是同一语义。独立COM锚定nv1静止场景中，pitch=+0.25rad得到proper=(-2.42703284,0,9.50503086)，严格等于Rᵀ(0,0,9.81)；roll=.15,pitch=−.2,yaw=.3亦同。freebody在三组姿态给定bodyω=(.2,−.3,.7)，site gyro最大误差约3e−16，site_R−body_R最大差0。\n')
    a('|R00初态body-frame位置 m|x|y|z|\n|---|---:|---:|---:|\n|wheelmid|−0.0342023945|0|−0.2385431982|\n|wholeCOM|−0.0342023945|−0.0001727055|−0.0703524817|\n|IMU（虚拟外参）|0.0300000000|0|0.0400000000|\n|COM→IMU|0.0642023945|0.0001727055|0.1103524817|\n')
    a('若固定几何并绕wheelmid/COM作4π纯yaw，chassis origin的向心模板约(−5.4010,0,0)m/s²；只把IMU补到origin不会去掉这项。**R00实际没达到4π**：spin尾按实测ω的wheelmid yaw-only模板x RMS约0.02014m/s²，forward仅0.000238m/s²，不能用命令模板解释它们全部实际误差。')
    a('更换参考点必须保持velocity/acceleration定义一致，且moving linkage下`r_OC(q)`变化：`a_C=a_O+alpha×r+omega×(omega×r)+2omega×r_dot+r_ddot`。不应把真实O→IMU外参(.03,0,.04)直接改成一个固定COM杆臂来掩盖参考点加速度。\n')
    a('## 7. 优先建议与证据限制\n')
    a('1. 先固定采样stage/时间戳，保留高频IMU预积分与窗统计；再讨论姿态/KF参数。')
    a('2. 姿态初始化使用可证静止/可信重力窗口；动态acc纠正至少结合加速度预测残差、窗口方差及飞行/落地状态，而不只依赖瞬时norm≈g。')
    a('3. 轮无滑观测按接触/滑移模式处理，维护协方差；spin尾contact_proxy=0仍KF更新是当前可直接定位的逻辑缺口。')
    a('4. 旋转参考点与二维速度/完整Coriolis、杆臂定义一致；不能把目标4π当已实现运动。')
    a('5. 父R01/R02解耦yaw或固定腿试验属独立新物理证据；本文不凭R00重放证明其性能。后续固定chart yaw bias另存独立JSON，不冒充严格全转动闭链控制模型。\n')
    a('完整证据：'+link(OUT/'PACKET_DIAGNOSTIC.json')+'、'+link(OUT/'CONDITIONED_DYNAMICS.json')+'、'+link(OUT/'STATIC_FRAME_GEOMETRY.json')+'。同包数学消融不产生新episode，gyro-only/reset真值仅诊断。本文不新增物理验收门槛，不修改原报告。\n')
    a('## 8. 尝试/错误记录\n')
    a('首个静态全nv0固定fixture的加速度读数未满足静止重力预期，原 '+link(OUT/'STATIC_FRAME_FAILURE_001.txt')+' 与 '+link(OUT/'STATIC_FRAME_001.log')+' 保留；未把该无DOF夹具结果归因于真实机器人IMU轴。改用有质量中心锚定铰链、nv1且零速度/零角加速度的独立静止夹具后，重力方向校验通过。'+link(OUT/'STATIC_SENSOR_PRECHECK_002.json')+'同时保留两种夹具原读数。成功静态分支共27次forward，首失败夹具6次forward，均0physicssteps、data.time=0。\n')
    report.write_text('\n'.join(L),encoding='utf-8')
    sources=p['sources']+[meta(ROOT/'reports/r00_first_six_analysis.json'),meta(ROOT.parent/'traditional_control_20261101/control_core.py'),meta(ROOT.parent/'traditional_control_20261101/full_lqr.py'),meta(ROOT/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml'),meta(ROOT.parent/'traditional_control_20261101/kinematics.py')]
    assert all(sha(x['path'])==x['sha256'] for x in sources)
    names=['analyze_r00_packets.py','diagnose_static_frames.py','analyze_conditioned_dynamics.py','write_r00_report.py','PACKET_DIAGNOSTIC.json','PACKET_QUICK_SUMMARY.json','CONDITIONED_DYNAMICS.json','CONDITIONED_QUICK_SUMMARY.json','STATIC_FRAME_GEOMETRY.json','STATIC_SENSOR_PRECHECK_002.json','STATIC_FRAME_FAILURE_001.txt','STATIC_FRAME_001.log','STATIC_FRAME_002.log','PACKET_ANALYSIS_001.log','CONDITIONING_001.log','r00_forward_nominal_sensors_derived_arrays.npz','r00_spin_nominal_sensors_derived_arrays.npz']
    for name in names:
        if name.endswith('.py'):ast.parse((OUT/name).read_text(encoding='utf-8'))
    ix={'kind':'R00_SOURCE_RECORDED_DATA_STATIC_FRAME_DIAGNOSTIC','status':'COMPLETE_DATA_ONLY_NO_NEW_PHYSICS','report':meta(report),'sources':sources,'all_sources_unchanged':True,'new_physics_steps':0,'new_rollout_episodes':0,'successful_static_forward_calls':s['mj_forward_calls'],'first_unsuitable_fixture_forward_calls':6,'time_advanced_s':0,'packet_math_replay_max_error':{k:v['replay_max_est14_error'] for k,v in p['cases'].items()},'skill_selection':'Office/ACL catalog checked; no model/control/data-analysis matching skill; existing filesystem/CLI used','artifacts':[meta(OUT/name) for name in names],'principal_findings':['Forward dynamic-acc attitude correction corruption, not dominant .15rad gyro-only integration loss','Spin wheel no-slip KF always updated even contact proxy zero; observed ground-support condition mostly absent','Independent IMU axis/sign fixtures pass; inertia axes are not sensor axes','Strong0.5ms mixed-stage sampling evidence separate from10ms row timing','COM/pivot template must use actual omega;4pi target was not achieved']}
    index.write_text(json.dumps(ix,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({'report':meta(report),'index':meta(index),'sources_unchanged':True,'new_physics_steps':0},indent=2))
if __name__=='__main__':main()
