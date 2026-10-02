"""Typeset measured MATLAB outputs; never invent success or hardware data."""
from pathlib import Path
import json
import math
import shutil
import hashlib
import zipfile
from xml.sax.saxutils import escape
import numpy as np
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Preformatted

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
RESULTS=HERE/'results'
FIG=RESULTS/'figures'
S=json.loads((RESULTS/'summary.json').read_text(encoding='utf8'))
P=json.loads((HERE/'mod4_extracted_parameters.json').read_text(encoding='utf8'))
G=json.loads((RESULTS/'posture_geometry.json').read_text(encoding='utf8'))
historyPath=HERE/'reference_inputs/tunnel_drive_dynamic_report_20260913.json'
if not historyPath.exists():historyPath=ROOT/'chassis_mod4_work/folded_pose_sim/tunnel_drive_dynamic_report.json'
H=json.loads(historyPath.read_text(encoding='utf8'))
CASES={c['name']:c for c in S['cases']}
pdfmetrics.registerFont(TTFont('YaHei','C:/Windows/Fonts/msyh.ttc'))
pdfmetrics.registerFont(TTFont('YaHeiBold','C:/Windows/Fonts/msyhbd.ttc'))
pdfmetrics.registerFont(TTFont('Mono','C:/Windows/Fonts/consola.ttf'))
NAVY=colors.HexColor('#16324F');BLUE=colors.HexColor('#216AA5');ORANGE=colors.HexColor('#CD7434')
LIGHT=colors.HexColor('#EEF3F7');GRAY=colors.HexColor('#526271')
styles={
 'title':ParagraphStyle('title',fontName='YaHeiBold',fontSize=26,leading=35,textColor=NAVY,spaceAfter=12),
 'h1':ParagraphStyle('h1',fontName='YaHeiBold',fontSize=18,leading=26,textColor=NAVY,spaceAfter=12),
 'h2':ParagraphStyle('h2',fontName='YaHeiBold',fontSize=12,leading=18,textColor=BLUE,spaceBefore=8,spaceAfter=5),
 'body':ParagraphStyle('body',fontName='YaHei',fontSize=10.3,leading=16,spaceAfter=7,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName='YaHei',fontSize=8.3,leading=12,textColor=GRAY,spaceAfter=6,wordWrap='CJK'),
 'cell':ParagraphStyle('cell',fontName='YaHei',fontSize=8.4,leading=12,wordWrap='CJK'),
 'head':ParagraphStyle('head',fontName='YaHeiBold',fontSize=8.4,leading=12,textColor=colors.white,wordWrap='CJK'),
 'mono':ParagraphStyle('mono',fontName='Mono',fontSize=8,leading=11,spaceAfter=6),
}
WIDTH=A4[0]-36*mm
story=[]
def p(text,style='body'):story.append(Paragraph(text,styles[style]))
def h(text):p(text,'h2')
def newpage(title):story.append(PageBreak());p(title,'h1')
def fig(name,caption,width=WIDTH,maxheight=None):
    path=FIG/name
    iw,ih=PILImage.open(path).size
    height=width*ih/iw
    if maxheight and height>maxheight:width*=maxheight/height;height=maxheight
    story.append(Image(str(path),width=width,height=height));p(caption,'small')
def table(rows,widths=None,small=False):
    if widths is None:widths=[WIDTH/len(rows[0])]*len(rows[0])
    cells=[[Paragraph(escape(str(x)).replace('\n','<br/>'),styles['head' if i==0 else 'cell']) for x in row] for i,row in enumerate(rows)]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LIGHT]),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#D6E2EA')),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(t);story.append(Spacer(1,7))
def f(v,n=3):return f'{v:.{n}f}'
def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor('#D6E2EA'));canvas.line(18*mm,16*mm,A4[0]-18*mm,16*mm)
    canvas.setFont('YaHei',8);canvas.setFillColor(GRAY);canvas.drawString(18*mm,10*mm,'MOD4  |  MATLAB / Simulink 仿真  |  2026-09-17')
    canvas.drawRightString(A4[0]-18*mm,10*mm,str(doc.page));canvas.restoreState()

p('MOD4 轮腿底盘<br/>MATLAB 仿真与控制报告','title')
p('参考浙江大学 HelloWorld 串联腿开源模型 · 使用本机 MATLAB R2024b 实际运行','body')
fig('cad_pose_0.png','图 1  原 MOD4 CAD 网格的平衡参考姿态。车体水平，腿部前倾用于补偿质心偏置。',maxheight=94*mm)
table([['本次交付','实际做到什么'],['动力学与控制','10 状态动力学；36 组数学增益、25 组关节限位内参考；可运行 Simulink 模型'],
       ['闭环工况','站立、1.2 m/s 加减速、20 N 推扰、正弦 6 rad/s 偏航、12°坡度等效阻力'],
       ['弹簧与机械能力','300-700 N 弹簧扫描；未知弹簧力高度控制；起伏与起跳力矩/能量预算']],[98,WIDTH-98])
h('先说结论')
p('在这套简化模型里，基础平衡可以实现，500 N 弹簧下基础站跑的腿电机需求约 11-12 N·m。弹簧越强不一定越好：700 N 会让电机在普通姿态下接近连续扭矩边界；弹簧力估错还会明显改变车身高度。')
p('这份报告给出的是可复算的控制设计依据。它没有替远端 RL 做验收，也没有证明真车已经能跨台阶、飞坡、跳跃或通过狗洞。','small')

newpage('01  参数从哪里来')
nom=S['nominal_pose'];lm=P['motor_parameters']['leg_motor'];wm=P['motor_parameters']['wheel_motor']
table([['参数','本次 MOD4 数值','依据 / 状态'],
 ['总质量',f(P['total_mass_kg'],3)+' kg','STEP/MJCF 材料与电机质量估算，尚未实车称重'],
 ['车体聚合质量',f(nom['body_mass_kg'],3)+' kg','车架 + 固定驱动转子组件'],
 ['单腿 / 单轮质量',f(nom['left_leg_mass_kg'],3)+' / '+f(nom['wheel_mass_kg'],3)+' kg','逐刚体聚合，不套开源机质量'],
 ['主轮半径 / 轮距','62.5 / 437.6 mm','现有 MOD4 CAD 参数'],
 ['车体俯仰惯量',f(nom['body_pitch_inertia_kg_m2'],4)+' kg·m²','CAD 主惯量旋转 + 平行轴聚合'],
 ['单腿俯仰惯量',f(nom['leg_pitch_inertia_kg_m2'],4)+' kg·m²','随腿长重新计算'],
 ['轮物理惯量 / armature',f(nom['wheel_pitch_inertia_kg_m2'],6)+' / '+f(nom['wheel_armature_kg_m2'],6),'后者为转子反射估算，均为 kg·m²'],
 ['腿部电机','4 × DM8009P，24 V','用户确认；20 N·m 连续 / 40 N·m 峰值按现有参数合同'],
 ['轮电机','2 × DM3519，总减速比 15.8','用户确认替换原装减速箱'],
 ['轮输出连续 / 峰值',f(wm['continuous_torque_nm'],2)+' / '+f(wm['peak_torque_nm'],2)+' N·m','从原厂总成缩放，效率比 0.9 为假设'],
 ['弹簧参考力 / 刚度','每支 300-700 N / 3500 N/m','用户要求的 DR 范围；刚度与阻尼待标定']],[98,153,WIDTH-251])
h('哪些数值还不能当成真机标定')
p('整车比赛质量、额外载荷位置、转子惯量、替换减速箱效率、峰值持续时间和电池功率限制尚未测定。模型的额外 payload 为 0，不能把 14.2 kg 直接当成带云台、弹药和电池的比赛质量。')
p('MATLAB 使用现有速度-扭矩工程包络，并施加峰值力矩与轮地牵引上限。包络不是实测完整电机曲线，RMS 扭矩也不等于已验证温升。','small')
p('来源：mod4_extracted_parameters.json、原 model_parameters.json；输入 MJCF SHA256：'+P['source_mjcf_sha256'][:32]+'…','small')

newpage('02  串联腿拓扑与姿态')
fig('cad_kinematics.png','图 2  由同一 CAD 销点推得的三种姿态。红虚线仅表示 247.2 mm 净高，不表示任何姿态已完成动态通过。',maxheight=92*mm)
table([['构件','连接关系','处理方式'],['大腿 / 曲柄','O-P-K 为大腿；O-A 为输入曲柄','两路腿电机在 O 处作用，角度不能混为一条普通膝关节'],
 ['第一闭链','O-A-B-P-O','曲柄、耦杆、摇杆与大腿构成回路'],
 ['第二闭链','P-C-D-K-P','摇杆经耦杆驱动小腿，使用连续装配分支'],
 ['弹簧 / 轮','弹簧 S-T；主轮中心 W','气弹簧长度随传动变化；主轮半径 62.5 mm']],[94,175,WIDTH-269])
h('CAD 闭链和本次控制模型是什么关系')
p('几何与静态负载来自完整 CAD 闭链；LQR 模型把每侧腿折算为固定虚拟长度和摆角，保留车体、两轮和两腿的惯性关系。它不是把 CAD 闭链删掉后当作一台散架机器人。')
p('36 个数学格点覆盖左右腿长约 155.5-333.9 mm；其中 11 点的水平车体参考超过 motor hip ±0.5 rad，已从限位内表剔除。25 个剩余格点的腿长约 192.7-333.9 mm。10 状态模型没有 roll、离地与限位/台阶/屋顶碰撞，左右腿长不等仍需完整接触验证。','small')

newpage('03  LQR 算法，用人话解释')
p('LQR 同时看位置、速度、偏航、左右腿摆角和车体俯仰。车体前倾时，它让轮子接住重心，同时用腿部力矩调整车体与腿的相对姿态。它不会只把“速度误差”交给轮子、把“倾角误差”交给腿，两个动作必须协调。')
table([['状态顺序','含义','单位'],['1-2  s, ds','轮轴中点位置、前向速度','m，m/s'],['3-4  ψ, dψ','偏航角、偏航角速度','rad，rad/s'],
 ['5-6  αL, dαL','左虚拟腿摆角、角速度','rad，rad/s'],['7-8  αR, dαR','右虚拟腿摆角、角速度','rad，rad/s'],['9-10  θ, dθ','车体俯仰、俯仰角速度','rad，rad/s']],[125,WIDTH-220,95])
h('计算流程')
p('先用开源动力学消去轮地与腿体内力，得到 M·q̈ = Bu·U + Bx·角度 + b0。代入 MOD4 的质量、惯量和几何后，构造 10×10 的 A 和 10×4 的 B。')
p('CAD 的质心不在轮轴正上方，因此先解平衡偏置，约束车体 θ=0，仅调整左右腿摆角，并求四个虚拟力矩前馈 Ud。电机 armature 按轮-腿、腿-车体的相对转动加入惯量交叉项，再精确离散化并调用 dlqr()。')
story.append(Preformatted('J = sum(x_error.T * Q * x_error + du.T * R * du)\nU = Ud - K * (x - x_ref)\nTs = 0.002 s  (500 Hz)',styles['mono']))
p('Q = diag([120,500,100,30,450,15,450,15,9000,150])；R = diag([12,12,1.5,1.5])。这些权重是本次工程设计选择，还需要结合实车带宽与噪声调试。')
h('虚拟力矩怎么落到四个腿电机')
p('由 CAD 计算 Jv = ∂[腿长, 腿摆角, 弹簧伸长] / ∂[hip, crank]，按虚功将轴向支持力、摆腿力矩和气弹簧作用映射成两台电机的输出扭矩。所有图里的腿力矩包含静态支撑与弹簧抵消量，不是只画 LQR 增量。')

newpage('04  实际生成的控制矩阵')
N=S['nominal_system'];K=np.array(N['K'])
p('标称腿长 '+f(nom['leg_length_m']*1000,2)+' mm；车体水平；虚拟腿平衡前倾 '+f(math.degrees(N['trim']),2)+'°。对应 motor hip/crank 约 '+f(G[0]['hip_rad'],4)+' / '+f(G[0]['crank_rad'],4)+' rad。')
columns=['输入 / 状态','s','ds','ψ','dψ','αL','dαL','αR','dαR','θ','dθ']
rows=[columns]+[[label]+[f(v,3) for v in row] for label,row in zip(['左轮','右轮','左腿摆矩','右腿摆矩'],K)]
table(rows,[52]+[(WIDTH-52)/10]*10)
p('上表为 Kd（4×10）。状态均使用相对平衡参考的误差，角度用弧度，控制律的负号已明确。角度零点、左右电机正负号或单位变化后不能原样抄到固件。完整精度见 K_discrete.csv。','small')
fig('closed_loop_poles.png','图 3  离散闭环极点。最大模为 '+f(N['max_discrete_pole'],7)+'；可控秩 '+str(N['controllability_rank'])+'/10；平衡方程残差 '+f(N['trim_residual'],12)+'。',maxheight=78*mm)
p('36 组均重新求 dlqr；关节限位内表为 25 组，另存 feasible_gain_schedule.json。155.5 mm 短腿点虽数学稳定，但水平平衡需 hip 约 0.650 rad，超过 0.5 rad，禁止使用该参考。交付原始表，不把未经验证的 poly33 直接当固件表。')

newpage('05  基础站立和 1.2 m/s 跑动')
fig('flat_accel_brake.png','图 4  加速到 1.2 m/s、保持、再减速停车。弹簧每支 500 N，曲线由 MATLAB 实际仿真生成。',maxheight=113*mm)
c=CASES['flat_accel_brake'];stand=CASES['stand_recovery']
table([['指标','站立恢复','1.2 m/s 加减速'],['速度 RMS 误差（全 12 s）',f(stand['speed_rms_error_m_s'],4),f(c['speed_rms_error_m_s'],4)+' m/s'],
 ['启动 2 s 后最大俯仰',f(stand['post_startup_max_body_pitch_deg'],4)+'°',f(c['post_startup_max_body_pitch_deg'],3)+'°'],
 ['4-6 s 速度 RMS 误差',f(stand['steady_speed_rms_error_m_s'],4),f(c['steady_speed_rms_error_m_s'],4)+' m/s'],
 ['2 s 后主轮峰值扭矩',f(max(stand['post_startup_peak_motor_torque_nm'][:2]),3),f(max(c['post_startup_peak_motor_torque_nm'][:2]),3)+' N·m'],
 ['2 s 后腿电机峰值扭矩',f(max(stand['post_startup_peak_motor_torque_nm'][2:]),2),f(max(c['post_startup_peak_motor_torque_nm'][2:]),2)+' N·m']],[210,(WIDTH-210)/2,(WIDTH-210)/2])
p('站立初始人为加入 5°车体倾角和 2°腿角误差。表中区分启动瞬态与后续运行，避免把初始倾角当作稳态摇晃。平跑的速度跟踪仍有约 0.08 m/s 稳态窗口误差；这套初始权重可以继续优化。')
p('俯仰稳定只对当前等效模型成立。这里没有导轮抢载、轮胎打滑、车底碰撞或 ONNX 观测接口，不能据此宣称远端 RL 的抽搐已经解决。','small')

newpage('06  外力推扰后能否恢复')
fig('push_20N.png','图 5  0.6 m/s 行进，5.0-5.3 s 在车体施加 20 N 水平推力，等效冲量 6 N·s。',maxheight=122*mm)
c=CASES['push_20N']
table([['检查项','本次结果'],['启动后最大车体俯仰',f(c['post_startup_max_body_pitch_deg'],3)+'°'],['末端俯仰误差',f(c['final_pitch_error_deg'],5)+'°'],
 ['全程速度 RMS 误差',f(c['speed_rms_error_m_s'],4)+' m/s'],['启动后轮 / 腿峰值',f(max(c['post_startup_peak_motor_torque_nm'][:2]),3)+' / '+f(max(c['post_startup_peak_motor_torque_nm'][2:]),2)+' N·m'],
 ['峰值扭矩饱和比例',f(c['motor_saturation_fraction']*100,2)+'%']],[210,WIDTH-210])
p('这个幅度的推扰可在模型中恢复。实际推扰会同时改变左右轮载荷，也可能产生 roll；这些作用本次没有覆盖。台阶冲击、落地冲击不能用这项结果代替。')

newpage('07  正弦小陀螺：6 rad/s 指令')
fig('yaw_tracking.png','图 6  偏航角速度指令为 6·sin(2π·0.2·t) rad/s，启动有平滑包络，同时前进约 0.4 m/s。',maxheight=85*mm)
c=CASES['yaw_sine_6rad_s']
table([['项目','数值'],['偏航速度峰值指令','6 rad/s ≈ 57.3 rpm'],['偏航角速度 RMS 误差',f(c['yaw_rate_rms_error_rad_s'],3)+' rad/s'],
 ['启动后俯仰峰值',f(c['post_startup_max_body_pitch_deg'],3)+'°'],['左右轮峰值扭矩',f(c['post_startup_peak_motor_torque_nm'][0],3)+' / '+f(c['post_startup_peak_motor_torque_nm'][1],3)+' N·m'],
 ['四个腿电机峰值',', '.join(f(x,2) for x in c['post_startup_peak_motor_torque_nm'][2:])+' N·m']],[205,WIDTH-205])
h('这项结果说明什么')
p('模型中的偏航追踪没有触及轮电机峰值上限，说明电机选型与该转速指令之间存在理论余量。正弦指令持续加减速，测到的是力矩与响应需求，不是恒速空转。')
h('高速小陀螺还缺哪部分验证')
p('10 状态模型未纳入离心侧向力、roll、左右轮法向载荷转移、回正力和轮胎接触斑。6 rad/s 的模型跟踪成功不能等同于真车稳定高速小陀螺。下一步应在完整闭链接触模型里做逐级升速，并验收轮载荷、侧倾、功率和扭矩饱和。')

newpage('08  坡度阻力：前馈确实有用')
fig('slope_feedforward_comparison.png','图 7  对比同一 12°坡度等效阻力下的纯 LQR 与坡度前馈 + LQR。只模拟沿坡阻力，未模拟坡脚/坡顶几何接触。',maxheight=91*mm)
a=CASES['slope_load_12deg'];b=CASES['slope_load_12deg_feedforward']
table([['指标','纯 LQR','前馈 + LQR'],['全程速度 RMS 误差',f(a['speed_rms_error_m_s'],3),f(b['speed_rms_error_m_s'],3)+' m/s'],
 ['4-6 s 速度 RMS 误差',f(a['steady_speed_rms_error_m_s'],3),f(b['steady_speed_rms_error_m_s'],3)+' m/s'],
 ['2 s 后最大俯仰',f(a['post_startup_max_body_pitch_deg'],3)+'°',f(b['post_startup_max_body_pitch_deg'],3)+'°'],
 ['2 s 后轮峰值扭矩',f(max(a['post_startup_peak_motor_torque_nm'][:2]),3),f(max(b['post_startup_peak_motor_torque_nm'][:2]),3)+' N·m']],[200,(WIDTH-200)/2,(WIDTH-200)/2])
p('纯反馈遇到持续阻力会先偏离目标再补力矩，速度误差明显增大。前馈根据估计坡度求轮边补偿力矩和腿角参考，LQR 再处理剩余误差。前馈是否准确取决于坡度、质量与电机力矩标定。')
p('沿坡重力约 '+f(P['total_mass_kg']*9.81*math.sin(math.radians(12)),1)+' N，低速静态抵消约需每轮 '+f(P['total_mass_kg']*9.81*math.sin(math.radians(12))*P['wheel_radius_m']/2,3)+' N·m；动态需求见曲线。台阶边缘需要额外接触仿真。','small')

newpage('09  六个电机的扭矩总表')
labels={'stand_recovery':'站立恢复','flat_accel_brake':'1.2 m/s 加减速','push_20N':'20 N 推扰','yaw_sine_6rad_s':'正弦小陀螺','slope_load_12deg':'12°阻力纯反馈','slope_load_12deg_feedforward':'12°阻力前馈'}
rows=[['工况（500 N/支）','左轮','右轮','左 hip','左 crank','右 hip','右 crank']]
for name,label in labels.items():rows.append([label]+[f(x,2) for x in CASES[name]['post_startup_peak_motor_torque_nm']])
table(rows,[127]+[(WIDTH-127)/6]*6)
p('上表为启动 2 s 后绝对峰值，单位 N·m。完整全程峰值和 RMS 均保存在 summary.json。初始 5°恢复瞬态可能高于表值；强冲击、离地和落地不在这些数值内。','small')
rows=[['弹簧参考力 / 支','平跑腿电机全程最大','平跑腿电机最大 RMS','性质']]
for c in S['spring_extreme_cases']:
    rows.append([str(c['spring_left_n'])+' N',f(max(c['peak_motor_torque_nm'][2:]),2)+' N·m',f(max(c['rms_motor_torque_nm'][2:]),2)+' N·m','实际弹簧力已补偿的负载扫描'])
table(rows,[88,120,120,WIDTH-328])
h('连续额定值不能当峰值长期使用')
p('DM8009P 按 20 N·m 连续、40 N·m 峰值核算。700 N 弹簧的基础负载已接近连续值；未知弹簧力高度控制中，峰值约 21.3 N·m。即使远低于 40 N·m，也不能据此保证长期不过热。')
p('这里画的是输出端力矩，不是电机转子力矩。轮减速比按总比 15.8 使用，未再乘原装约 19.2 的减速比。电池 24 V 的母线限功率、回生和热模型尚未标定。')
h('现有 RL 抽搐应怎样排查')
p('先核对动作/观测语义、左右正负号、motor hip/crank 目标限位、力矩饱和、轮与导轮载荷、弹簧前馈和实际 PD 带宽，再谈增加 DR 或改奖励。MATLAB 的结果支持“结构在合适控制下有基础平衡能力”，不能证明当前 RL 控制接口正确。')

newpage('10  氮气弹簧：300-700 N 不是常数力')
fig('spring_torque_scan.png','图 8  CAD 姿态、弹簧眼距、实际弹簧力与两台腿电机静态扭矩之间的关系。',maxheight=120*mm)
p('定义：每支弹簧在 gas_slide q=0 时参考力为 Fref。当前模型 F(q,q̇)=Fref-3500·q-3·q̇。q 用 m，伸长为正；因此 300-700 N 是参考力范围，整个行程中的瞬时力可以超出该范围。')
table([['项目','CAD 扫描数值'],['本次竖直腿长范围','155.5-333.9 mm'],['弹簧眼距范围',f(P['poses'][0]['spring_eye_length_m']*1000,2)+'-'+f(P['poses'][-1]['spring_eye_length_m']*1000,2)+' mm'],
 ['标称姿态眼距',f(nom['spring_eye_length_m']*1000,2)+' mm'],['标称姿态气弹簧力','300 / 500 / 700 N（此处 q=0）']],[205,WIDTH-205])
p('300 N 更利于低静态负载；500 N 储能与持续负载较折中；700 N 更需要主动压住弹簧。500 N 可作为仿真参考候选，但它定义在约 179.36 mm 眼距；按当前线性模型，200 mm 全伸展时仅约 427.8 N，不能直接等同于商品标称“500 N”。硬件必须按实测曲线换算。','small')

newpage('11  未知弹簧力会改变高度')
fig('gas_height_uncertainty.png','图 9  控制器始终按 500 N/支前馈，实际每支为 300、500 或 700 N。对比相同 PD 与加积分补偿；5-13 s 另加入 ±20 mm 高度指令。',maxheight=112*mm)
rows=[['实际力 / 支','纯 PD 末端偏差','加积分末端偏差','加积分全程 RMS']]
hc=S['gas_height_study']['cases']
for F in [300,500,700]:
    a=next(x for x in hc if x['spring_left_n']==F and x['spring_right_n']==F and not x['integral_enabled'])
    b=next(x for x in hc if x['spring_left_n']==F and x['spring_right_n']==F and x['integral_enabled'])
    rows.append([str(F)+' N',f(a['final_stand_bias_mm'],2)+' mm',f(b['final_stand_bias_mm'],3)+' mm',f(b['height_rms_error_mm'],2)+' mm'])
table(rows,[86,(WIDTH-86)/3,(WIDTH-86)/3,(WIDTH-86)/3])
p('这不是把 DR 打开就自然得到鲁棒性的证据：力估错会留下厘米级偏差。积分补偿、力估计，或能从历史观测识别负载的 RL 策略，可以用于补这类偏差；仍需验证启动、动作切换和限位附近的瞬态。')
p('竖直模型的有效惯量由完整 MJCF 的动能和 CAD 连续关节分支推得；KP=4000 N/m、KD=350 N·s/m、KI=3000 N/(m·s)，不是直接填给电机的关节 PD 增益。它假设已有理想俯仰调节。左右 300/700 N 的总力会在该 1 DOF 模型中抵消，不能验证左右不等力造成的 roll。','small')

newpage('12  起伏、起跳和飞坡的能力边界')
fig('jump_budget.png','图 10  不同弹簧力下的理想起跳扭矩预算。横轴是离地后的质心上升，不是比赛台阶高度。',maxheight=82*mm)
rows=[['离地后上升','所需离地速度','动能','300 / 500 / 700 N 最大电机扭矩']]
for rise in [.15,.20,.25,.30]:
    js=[x for x in S['mechanics']['jump_budget'] if abs(x['ballistic_rise_m']-rise)<1e-8]
    rows.append([str(round(rise*1000))+' mm',f(js[0]['required_launch_speed_m_s'],2)+' m/s',f(js[0]['kinetic_energy_at_takeoff_j'],1)+' J',' / '.join(f(x['estimated_peak_leg_motor_nm'],2) for x in js)+' N·m'])
table(rows,[78,90,61,WIDTH-229])
p('可用伸腿位移约 '+f(S['mechanics']['available_extension_stroke_m']*1000,1)+' mm。伸腿期间还要克服约 '+f(S['mechanics']['jump_budget'][0]['extension_gravity_work_j'],1)+' J 的重力功，不能把弹簧放能直接全部当作腾空动能。')
rows=[['弹簧 / 支','±25 mm，0.8 Hz 起伏估算 hip / crank 峰值','伸腿弹簧放能（两支）']]
for d in S['mechanics']['undulation_inverse_dynamics']:
    j=next(x for x in S['mechanics']['jump_budget'] if x['force_ref_n']==d['force_ref_n'])
    rows.append([str(d['force_ref_n'])+' N',f(d['peak_hip_nm'],2)+' / '+f(d['peak_crank_nm'],2)+' N·m',f(j['spring_released_energy_j'],1)+' J'])
table(rows,[76,WIDTH-190,114])
p('起跳预算检查了估算电机转速与力矩包络，但仍忽略连杆加速峰值、气体非线性、摩擦、动作轨迹约束与落地冲击。飞坡还要用实际坡面速度和几何求出射角。此处不作“能上某个 RM2026 台阶”的放行结论。','small')

newpage('13  狗洞姿态：几何与牵引要一起看')
fig('cad_pose_2.png','图 11  此前推演姿态附近的 CAD 微调姿态，本次重新渲染与计算几何，未重新跑 Isaac 狗洞策略。',maxheight=89*mm)
table([['几何量','微调姿态数值'],['hip / crank','+0.47017 / -0.59584 rad'],['crank-hip','-1.06601 rad'],['root 高度',f(G[2]['root_height_m']*1000,3)+' mm'],
 ['完整可视 CAD 顶高',f(G[2]['full_visual_height_m']*1000,3)+' mm'],['247.2 mm 静态顶面余量',f((.2472-G[2]['full_visual_height_m'])*1000,3)+' mm']],[205,WIDTH-205])
p('223.36 mm 指腿顶的量测基准，不是整个车的最高点。此前硬限位姿态 hip≈0.45029、crank≈-0.63603，与此微调姿态不同；微调是为了给主轮留载荷，不能只追求最低腿顶。')
p('归档 MuJoCo 动态报告曾记录：0.18 m/s 指令下主轮平均法向载荷约 '+f(H['cases'][1]['mean_drive_wheel_normal_force_n'],1)+' N，最小动态顶隙约 '+f(H['cases'][1]['minimum_dynamic_roof_clearance_m']*1000,2)+' mm。该测试用了可转动被动导轮；这些是旧测试结果，本次未复测。','small')
p('静态余量只有约 1.57 mm，远小于常见装配、轮胎变形和地面变化量级。300-700 N 引起的高度瞬态也足以超过顶隙。赛场鲁棒通过必须在完整 CAD 包络、真实导轮、轮载荷与屋顶碰撞中验收；不能靠奖励函数或本次 LQR 报告直接认证。')

newpage('14  模型层面的随机化验证')
fig('model_robustness.png','图 12  120 个固定种子样本；所有样本复用标称 K，不为每个扰动重调控制器。',maxheight=87*mm)
table([['随机参数','范围'],['每支弹簧参考力','300-700 N，包含左右 300/700 与 700/300 边界'],['车体/腿质量倍率','0.85-1.15'],['主要惯量倍率','0.8-1.2'],['观测延迟','0-10 ms'],['摩擦系数','0.45-1.0'],['角度测量噪声','标准差 0.0015 rad']],[205,WIDTH-205])
r=S['robustness']
p('12 s 简化模型滚动试验有界 '+str(r['bounded_count'])+'/'+str(r['n'])+'；最差速度 RMS 误差 '+f(r['worst_speed_rms_error_m_s'],3)+' m/s。判定“有界”仅表示未超过模型中设置的 35°误差/8 m/s 截止条件，没有接触通过率或赛场任务成功率。')
p('弹簧在这一批固定腿长试验中按实际力做静态补偿，主要考察力矩余量。它没有检验未知弹簧力识别；第 11 页另做了未知力试验。当前扭矩未触及轮地牵引上限，摩擦 DR 在这批低负载样本中并没有充分被激活。','small')
p('所以结果可用于筛选基础 LQR 权重，不能称为 sim2real 鲁棒性通过。下一轮必须补轮胎、被动导轮、上下台阶/落地、roll、限位接触、延迟与实际载荷组合。')

newpage('15  复现方法与后续任务')
h('本次已经运行并交付')
p('MATLAB R2024b：完整动力学符号矩阵生成、MOD4 参数替换、36 组 LQR、6 个闭环工况、120 个随机样本、10 个未知弹簧力高度试验，以及力矩/能量曲线。Simulink 站立模型运行成功，与 MATLAB 状态最大差 '+f(S['simulink_cross_check']['max_state_difference'],16)+'。')
story.append(Preformatted("cd('.../matlab_mod4_wbr_20260917')\naddpath(pwd)\nrun_mod4_wbr\nopen_system('MOD4_WBR_Balance_20260917.slx')",styles['mono']))
p('需要 MATLAB + Control System Toolbox；缓存的 wbr_linear_matrices.m 已交付，重跑不需要再次符号推导。修改动力学后重新生成矩阵需要 Symbolic Math Toolbox。Simulink 独立模型使用数值字面量，可直接运行。')
h('优先完成的工程任务')
table([['顺序','任务','完成标准'],['1','实测质量、质心、惯量与弹簧力-行程曲线','比赛载荷明确；左右弹簧分别标定'],['2','验证控制接口与电机带宽','正负号、单位、零点、目标限位、输出力矩均一致'],
 ['3','完整闭链接触模型做基础站跑','主轮有载荷；导轮不抢载；动作平滑；碰撞无漏检'],['4','在未知 300-700 N 下验收高度与姿态','站跑维持低误差；左右不等力和切换瞬态通过'],
 ['5','逐项加入坡/台阶/起伏/飞坡/跳跃/狗洞','每项独立通过率、最差样本、力矩饱和与净空报告']],[45,211,WIDTH-256])
h('开源参考与许可证')
p('<link href="https://github.com/Particlela/WBR_simulation" color="#216AA5">Particlela/WBR_simulation</link>，固定提交 '+P['reference_commit']+'。借鉴 equation.m 的整体动力学和按腿长生成 dlqr 增益的流程；本次使用自己的 MOD4 参数、力矩分配、随机化与报告代码。参考源码为 MIT，许可证保留在交付包内。','small')
p('原始 STEP/SolidWorks 文件未修改；本次任务未上传或切换目标机 RL 训练。报告、脚本、数据与可运行模型均在本机交付包中。','small')

newpage('附录  连续状态空间 A 与 B')
p('标称腿长 273.24 mm、水平车体平衡参考。状态列顺序与第 3 页一致；下表显示 3 位有效数字，完整精度见 A_continuous.csv 与 B_continuous.csv。')
def matrixnum(v):return '0' if abs(v)<1e-10 else f'{v:.3g}'
table([['A']+[str(i) for i in range(1,11)]]+[[str(i+1)]+[matrixnum(v) for v in row] for i,row in enumerate(N['A'])],[25]+[(WIDTH-25)/10]*10)
table([['B','左轮力矩','右轮力矩','左腿摆矩','右腿摆矩']]+[[str(i+1)]+[matrixnum(v) for v in row] for i,row in enumerate(N['B'])],[25]+[(WIDTH-25)/4]*4)
p('位置与角度对应的一阶积分行为奇数行；加速度行为偶数行。B 的量纲随状态行不同而不同。A、B、Kd 与 Ud 必须作为同一套模型使用，不能把其他底盘的矩阵拼进来。','small')

OUT=ROOT/'output/pdf/MOD4_MATLAB_WBR仿真报告_20260917.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=21*mm,
                     title='MOD4轮腿底盘MATLAB仿真与控制报告',author='MOD4 simulation study')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
shutil.copy2(OUT,HERE/OUT.name)
print(str(OUT))
