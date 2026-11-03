"""Own static evidence writer only: no archive/project-code imports or execution."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent.parent;O=Path(__file__).resolve().parent
S=ROOT/'DEPLOYED_BASELINE_AUDIT_V1/source/StandardRobotpp-balance1'
M=ROOT/'DEPLOYED_BASELINE_AUDIT_V1/SELECTED_SOURCE_MANIFEST.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def rec(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)).replace('\\','/'),bytes=len(b),SHA=sha(b))
def save(n,v):
 with(O/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def L(label,p,a=None,b=None):
 q=(S/p).relative_to(ROOT).as_posix();q+=(''if a is None else '#L'+str(a)+(''if b is None else '-L'+str(b)))
 return '['+label+'](<'+'../'+q+'>)'
assert rec(M)['SHA']=='33a79a69e5ebd1be437b05c75de378359d969f63d0761aa9303e79ce2a47a98d'
manifest=json.loads(M.read_bytes());assert manifest['selected_text_count']==391
index={r['member'].split('/',1)[1]:r for r in manifest['files']}
paths=['MDK-ARM/standard_robot.uvprojx','MDK-ARM/standard_tpye_c/standard_tpye_c.sct','MDK-ARM/startup_stm32f407xx.s','standard_robot.ioc','Src/main.c','Src/freertos.c','Src/can.c','Src/spi.c','Src/dma.c','Src/gpio.c','Src/stm32f4xx_it.c','Inc/FreeRTOSConfig.h','Inc/stm32f4xx_hal_conf.h','Inc/main.h','application/robot_param.h','application/robot_param_balanced_infantry.h','application/typedef/robot_typedef.h','application/chassis/chassis_task.c','application/chassis/chassis_task.h','application/chassis/chassis_balance.c','application/chassis/chassis_balance.h','application/robot_cmd/CAN_cmd_damiao.c','application/robot_cmd/CAN_cmd_damiao.h','application/robot_cmd/CAN_receive.c','application/robot_cmd/CAN_receive.h','application/robot_cmd/motor.c','application/robot_cmd/motor.h','application/robot_cmd/CAN_cmd_lingkong.c','bsp/boards/bsp_can.c','bsp/boards/bsp_delay.c','application/IMU/IMU_task.c','application/IMU/IMU_task.h','application/IMU/IMU.h','application/IMU/IMU_solve.c','components/devices/BMI088driver.c','components/devices/BMI088driver.h','components/devices/BMI088Middleware.h','components/algorithm/user_lib.c','application/assist/detect_task.c','application/other/remote_control.c','application/other/test_task.c','application/calibrate/calibrate_task.c']
verified=[]
for p in paths:
 assert p in index and not (S/p).is_symlink() and (S/p).resolve().is_relative_to(S.resolve())
 r=index[p];b=(S/p).read_bytes();assert len(b)==r['readable_bytes']and sha(b)==r['readable_SHA'];b.decode('utf-8')
 verified.append(dict(member=r['member'],readable_relative=p,bytes=len(b),readable_SHA=sha(b),original_CRC32=r['CRC32'],original_raw_SHA=r['raw_SHA'],original_encoding=r['encoding']))
proj=ET.fromstring((S/paths[0]).read_bytes());targets=proj.findall('./Targets/Target');assert len(targets)==1;t=targets[0]
assert t.findtext('./TargetOption/TargetCommonOption/Device')=='STM32F407IGHx'
buildfiles=[]
for g in t.findall('./Groups/Group'):
 for f in g.findall('./Files/File'):
  fp=f.findtext('FilePath');gp=g.findtext('./GroupOption/CommonProperty/IncludeInBuild');inc=f.findtext('./FileOption/CommonProperty/IncludeInBuild')
  assert fp is not None
  buildfiles.append(dict(group=g.findtext('GroupName'),file=fp,included_by_project=(gp!='0'and inc!='0'),group_override=gp,file_override=inc))
required=['chassis_task.c','chassis_balance.c','CAN_cmd_damiao.c','CAN_receive.c','motor.c','IMU_task.c','IMU_solve.c','test_task.c','bsp_can.c']
for n in required:assert sum(x['included_by_project']for x in buildfiles if x['file'].replace('\\','/').split('/')[-1]==n)==1
save('SOURCE_SUBSET.json',dict(kind='STATIC_SELECTED_TEXT_AND_SOURCE_LINE_REVIEW_NOT_EXECUTED_FIRMWARE',manifest=rec(M),scope='42 focused files were read fully/excerpted or content-searched; selected application symbol searches were not a full semantic review of every file',files=verified,project_target=t.findtext('TargetName'),compiler_record=t.findtext('pCCUsed'),defines=t.findtext('./TargetOption/TargetArmAds/Cads/VariousControls/Define'),required_project_included=required,archive_opened_or_hashed=False,git_opened=False,original_payloads_reread=False,selected_CRC_and_raw_SHA_are_parent_lineage=True))
B=[]
def bind(name,old,reuse,need,src):B.append(dict(name=name,observed_old_source=old,reusable_candidate=reuse,MOD4_binding_required=need,source_locations=src,status='CANDIDATE_ONLY_NOT_MOD4_MEASUREMENT_OR_SEND_PERMISSION'))
bind('MCU_clock_memory',dict(MCU='STM32F407IGHx',IOC_CPN='STM32F407IGH6',package='UFBGA176',HSE_Hz=12000000,SYSCLK_Hz=168000000,APB1_Hz=42000000,APB2_Hz=84000000,flash_bytes=1048576,scatter_RW_bytes=131072),'original startup/HAL pin-clock initialization and Keil project layout','actual PCB/crystal/carrier, linker/ABI/helper libs/RAM/stack/WCET and flashed image SHA', ['MDK-ARM/standard_robot.uvprojx:10-21,337-370','standard_robot.ioc:140-172,543-576','Src/main.c:172-215','Inc/stm32f4xx_hal_conf.h:95-97'])
bind('RTOS_chassis',dict(API='CMSIS-RTOS v1 over FreeRTOS ARM_CM4F',tick_Hz=1000,startup_delay_ticks=357,relative_delay_ticks=2,priority='AboveNormal'),'existing main→MX_FREERTOS_Init→chassis_task and priority/IRQ setup','separate math and actual driver cadence, absolute release/deadline and admission gates; vTaskDelay(2) is not 2ms hard period',['Src/freertos.c:198-239','application/chassis/chassis_task.c:56-83','Inc/FreeRTOSConfig.h:55-66'])
bind('CAN1',dict(RX='PD0',TX='PD1',AF=9,bitrate_Hz=1000000,prescaler=3,BS1=10,BS2=3,SJW=1,IRQ_priority=6),'hcan1/MSP/filter/RX0 interrupt pipeline','physical transceiver/termination/wiring/ID collision and bitrate measurement; error/busoff recovery',['Src/can.c:31-49,77-107','bsp/boards/bsp_can.c:3-23'])
bind('CAN2',dict(RX='PB5',TX='PB6',AF=9,bitrate_Hz=1000000,prescaler=3,BS1=10,BS2=3,SJW=1,IRQ_priority=6),'hcan2/MSP/filter/RX0 interrupt pipeline','same physical verification; this old wheel protocol is not a DM3519 implementation',['Src/can.c:53-71,111-137'])
bind('joint_DM8009_MIT_TX',dict(joint_indices=[0,1,2,3],CAN=1,TX_STD_ID=[1,2,3,4],mode=0,enable_lastbyte='FC',disable_lastbyte='FD',clear_error_lastbyte='FB',save_zero_lastbyte='FE',prefix='FF*7',normal='P=V=Kp=Kd=0,T=set.tor',standup='MIT position, Kp20/Kd1'),'existing DM command packer and caller dispatch pattern','actual motor model including DM8009P distinctions, firmware mode/ranges, torque coordinate and zero persistence; no active disable/clearErr caller established',['application/chassis/chassis_balance.c:157-160,1504-1619','application/robot_cmd/CAN_cmd_damiao.c:45-185,291-389'])
bind('DM_codec_RX',dict(P_rad=[-12.5,12.5],V_rad_s=[-30,30],T_nominal_Nm=[-10,10],Kp=[0,500],Kd=[0,5],bits=[16,12,12,12,12],RX_STD_ID=[81,82,83,84],generic_RX_IDs=[81,82,83,84,85,86],state='data[0] high nibble',payload_id='data[0] low nibble',arrival_clock='HAL_GetTick uint32 ms',offline_after_ms=10),'existing bitfield decode and tagged motor storage','DLC/RTR/id agreement/finite/domain validation, sensor sample epoch vs arrival and same-packet aggregation; actual physical feedback torque calibration',['application/robot_cmd/motor.h:130-181','application/robot_cmd/CAN_receive.h:55-62','application/robot_cmd/CAN_receive.c:73-87,170-185,426-440'])
bind('joint_model_coordinates',dict(directions=[-1,-1,1,1],offsets_rad=['pi-.177','.177','pi+.177','-.177'],reduction_declared=1,map=['leg0.Phi1','leg0.Phi4','leg1.Phi1','leg1.Phi4'],position='wrap((raw_pos+offset)*direction, -pi,pi)',normal_T_limit_Nm=7),'explicit per-axis direction/zero separation from raw codec','not automatically MOD4 LH/LC/RH/RC or state14 delta; independently verify mechanics, zeros, output-shaft ratio and sign',['application/robot_param_balanced_infantry.h:44-83,119-120','application/chassis/chassis_balance.c:517-538,1269-1294','components/algorithm/user_lib.c:178-180'])
bind('wheel_LK_MF9025',dict(CAN=2,motor_ID=[1,2],RX_STD_ID=[321,322],TX_group_STD_ID=640,directions=[1,-1],normal_command_extra_sign=-1,command_formula='clamp_int16(tau/0.32*62.5,-2000,2000)',payload='four LE int16 currents',feedback_speed='signed degree/s * pi/180',feedback_current='iq*(16.5/2048) A'),'original LK protocol as reference only for the actual old wheels','MOD4 DM3519 requires its actual firmware protocol/range/current/gear proof; do not relabel LK frames as DM',['application/chassis/chassis_balance.c:162-163,1291-1294,1625-1656','application/robot_cmd/CAN_cmd_lingkong.c:22-26,161-178,246-292','application/robot_cmd/CAN_receive.c:111-119,448-460'])
bind('IMU_SPI_DMA',dict(sensor='BMI088 plus IST8310 init',SPI=1,SCK='PB3',MISO='PB4',MOSI='PA7',gyro_CS='PB0',accel_CS='PA4',gyro_DRDY='PC5/EXTI9_5',accel_DRDY='PC4/EXTI4',RX_DMA='DMA2_Stream2/channel3',TX_DMA='DMA2_Stream3/channel3',gyro_ODR_Hz=1000,accel_ODR_Hz=800,task_priority='Realtime',AHRS_dt_s=.001),'existing hardware drivers, DRDY→DMA→software EXTI0→task notification sequence','verify data-ready timing, loss/coalescing counters, per-sensor sample epochs and coherent queues; no 2kHz hardware proof',['application/IMU/IMU_task.c:224-333,627-774','components/devices/BMI088driver.c:66-115','Src/spi.c:91-145','Inc/main.h:87-98'])
bind('IMU_frame_units',dict(gyro_sensor_range_deg_s=2000,accel_sensor_range_g=3,gyro_scale_rad_s_per_count=.0010652644360316953,accel_scale_m_s2_per_count=.0008974358974,raw_to_board=['raw_y','-raw_x','raw_z'],Euler='yaw,pitch,roll rad',rates='body gyro XYZ rad/s, not general Euler derivatives'),'existing converted gyro/proper accel and quaternion pointer access as raw material','MOD4 board mounting/frame/quaternion convention/IMU lever/temperature+bias calibration and C3 canonical packet metadata',['components/devices/BMI088driver.h:24-46','application/IMU/IMU_task.c:45-49,388-437,564-609'])
bind('liveness_and_stop',dict(RC='direct DT7 receive_count>5 and age<100ms',motor_offline='10ms receive-age flag, no ScanOfflineMotor caller in selected application',IMU_exception='pointer NULL, not fresh-age',SAFE='joint zero-speed kd4 plus wheel-stop-PID torque',OFF='joint zero MIT plus wheel torque0'),'the explicit RC→error→SAFE caller chain and diagnostic states','new independent stale/motor-fault/clock/transport/expiry/latch/watchdog gates and validated brake/disable semantics; invalid zero is not a universal overspeed-safe command',['application/other/remote_control.c:573-588','application/chassis/chassis_balance.c:282-335,1195-1218,1504-1656','application/assist/detect_task.c:265-312'])
bind('transport_and_runtime_gates',dict(tx='20 mailbox polls then unconditional HAL_CAN_AddTxMessage; return ignored',AutoBusOff=False,AutoRetransmission=False,pacing='DM_DELAY250us and uninitialized local cnt modulo2',hardware_watchdog='no IWDG/WWDG in selected IOC/main initialization'),'low-level HAL access only, not end-to-end send qualification','single queue owner, bounded atomic frame capture, TTL/cancel/ACK/bus-fault recovery, validated 64-bit monotonic clock and last poll; no send permission from this audit',['bsp/boards/bsp_can.c:33-45','Src/can.c:34-45,56-67','application/chassis/chassis_balance.c:1481-1526','Src/main.c:225-231'])
save('CANDIDATE_BINDINGS.json',dict(kind='OLD_DEPLOYED_SOURCE_BINDING_CANDIDATES_NOT_MOD4_CALIBRATION',physical_MOD4_binding=False,flash_or_send_permission=False,rows=B,missing_selected_source_files=[],unresolved_actual_flashed_image_SHA=True,unresolved_physical_PCB_revision_serial_wiring_motor_firmware=True))
A='application/chassis/chassis_balance.c';D='application/robot_cmd/CAN_cmd_damiao.c';F='application/IMU/IMU_task.c';R='application/robot_cmd/CAN_receive.c';H='application/robot_cmd/motor.h';P='application/robot_param_balanced_infantry.h'
lines=['# 真实老机部署包：板/RTOS/IMU/CAN静态实链审计','',
'**结论：可复用既有F407/C板风格BSP、RTOS和DM/LK transport骨架；本工程是四DM8009关节＋两MF9025轮，尚非MOD4的DM8009P/DM3519物理绑定。没有构建/刷写/Zip代码运行。**','',
'## 1. 证据与选型',
'- 只读父已选391text；本次42个重点file正文/片段/内容检索＋selected application符号caller搜索。原包/.git/未选payload未打开、未wholehash；CRC/rawSHA/编码→UTF8链沿用父'+ '[selected manifest](<../DEPLOYED_BASELINE_AUDIT_V1/SELECTED_SOURCE_MANIFEST.json>)'+'，SHA33a79a69…。详见[SOURCE_SUBSET](<SOURCE_SUBSET.json>)。',
'- '+L('Keil唯一target',paths[0],10,21)+'为standard_robot、STM32F407IGHx/Cortex-M4，ARMCC5.06 update4(build422)、CM4F/STM32F407xx宏；'+L('IOC', 'standard_robot.ioc',140,172)+'为F407IGH6/UFBGA176。C_BOARD_BALANCE_CHASSIS=2只是软件角色，PCB/SN/实际已刷image SHA仍未知。',
'- '+L('robot_param.h','application/robot_param.h',25,36)+'直接include balanced_infantry；'+L('profile',P,10,25)+'定义CHASSIS_BALANCE，'+L('类型宏','application/typedef/robot_typedef.h',5,29)+'值4，其余gimbal/shoot/arm/custom按默认NONE。不是从一堆同名函数猜运行。',
'- '+L('clock','Src/main.c',172,215)+'与'+L('HAL HSE','Inc/stm32f4xx_hal_conf.h',95,97)+'：12MHz/6×168/2=168MHz，APB1/4=42MHz/APB2/2=84MHz；Keil CPU字段CLOCK25MHz与之不同，不把该字段当实际晶振测量。',
'- '+L('link配置',paths[0],360,370)+'自动target memory、未显式scatter；'+L('已有sct',paths[1],5,13)+'为FLASH08000000/1MiB、RW20000000/128KiB。Device列CCM64KiB不等于本scatter已分配。selected无CMake/GNU ld入口，本审计按Keil而非新造工程。','',
'## 2. main→实际RTOS→发送者',
'- '+L('main','Src/main.c',118,153)+'依次GPIO/DMA/CAN1/2/SPI等初始化→can_filter_init→delay_init→remote_control_init→MX_FREERTOS_Init→osKernelStart；startup表指向'+L('中断源','MDK-ARM/startup_stm32f407xx.s',75,156)+'，不是新BSP。',
'- '+L('线程条件','Src/freertos.c',198,239)+'创建AboveNormal chassis_task及Realtime IMU_task；FreeRTOS ARM_CM4F/CMSIS-RTOS v1、'+L('tick','Inc/FreeRTOSConfig.h',55,66)+'1kHz/heap24576。',
'- '+L('chassis_task','application/chassis/chassis_task.c',56,83)+'：Publish→延357tick→Init→Observer→HandleException→SetMode→Reference→Console→SendCmd→vTaskDelay(2)。这只是work/pacing之后相对延2tick，非严格2ms release/WCET、更非2kHz。',
'- '+L('balance guard',A,25,26)+'＋已列入target的chassis_balance.c提供strong Chassis*覆盖task.c weak默认；project也包含CAN_cmd_damiao/CAN_receive/motor/bsp_can。逐成员include检查保存在[SOURCE_SUBSET](<SOURCE_SUBSET.json>)，不证明当前板上二进制等于该source。',
'- '+L('Init',A,147,163)+'实际4关节CAN1 IDs1..4、DM_8009、ratio1、MIT0；2轮CAN2 IDs1/2、MF_9025。不是6轴全达妙。','',
'## 3. CAN物理配置与DM实际命令链',
'- '+L('CAN1','Src/can.c',31,106)+'PD0/RX PD1/TX AF9；'+L('CAN2','Src/can.c',53,137)+'PB5/RX PB6/TX AF9。均NORMAL、prescaler3、SJW1、BS1=10/BS2=3：按42MHz PCLK1为1Mbit/s；RX0 IRQ priority6，自动busoff/重发均DISABLE。',
'- '+L('filter','bsp/boards/bsp_can.c',3,23)+'IDMASK全0接收、bank0/14→FIFO0、Start/notify；'+L('IRQ','Src/stm32f4xx_it.c',225,275)+'→HAL_CAN_IRQHandler→'+L('callback',R,334,347)+'→DecodeStdIdData。filter返回/初始化错误恢复未形成校验闭环。',
'- '+L('SendCmd',A,1494,1558)+'→SendJointMotorCmd→DmMitCtrlTorque（普通运行）→'+L('MitCtrl',D,161,185)+'→CAN_SendTxMessage→HAL_CAN_AddTxMessage；StandUp实际切MIT位置，SAFE切MIT零速。行为/起立算法另由model代理审，不在此复制。',
'- '+L('DM commands',D,45,145)+'StdID=motor_id+mode：MIT=0/位置=0x100/速度=0x200；FF×7末字节FC enable/FD disable/FB clear/FE写零。当前motor初始化mode0，normal MIT并不走float位置/速度mode。',
'- '+L('MIT codec',H,134,158)+'P16bit±12.5rad/V12bit±30rad/s/Kp12bit0..500/Kd12bit0..5/T12bit±10名义Nm。'+L('normal clamp',A,1269,1294)+'active ±7Nm；jump ±20支路已注释。'+L('float_to_uint','components/algorithm/user_lib.c',194,217)+'仅线性映射，无finite/限幅检查；不要把编码域当自动限扭。',
'- '+L('feedback IDs','application/robot_cmd/CAN_receive.h',55,69)+'DM 0x51..0x56（本机用51..54），LK141..144（用141/142）；'+L('DM parse',R,73,87)+'state高4bit/id低4bit，P16/V12/T12/MOS&rotor温度，标记HAL_GetTick接收到达。RX注释±45/±18不是实际宏±30/±10。',
'- GetMotorMeasure'+L('实际读取',R,426,504)+'按can/id−1取cache、超过10ms标offline；fdb数值尚未乘direction或ratio。无DLC/RTR/payload-id一致性检查、sample epoch/序号/同帧保证；arrival tick不是电机采样时间，反馈tor只是该drive协议名义量。','',
'## 4. 方向、轮协议与零位边界',
'- '+L('profile方向零点',P,44,83)+'J=[−1,−1,+1,+1]；offset=[π−.177,.177,π+.177,−.177]rad；'+L('observer',A,517,538)+'Phi1/Phi4=wrap((raw+offset)×direction)、vel/tor×direction。它们是旧leg0/1的两个驱动，不自动等于MOD4 hip/crank或delta-state。',
'- '+L('轮命令',A,1291,1294)+'另有负号−(T×W_DIRECTION)，W=[+1,−1]，作者注释仍注明原因待排查；别仅凭direction宏做新板符号绑定。',
'- '+L('LK group','application/robot_cmd/CAN_cmd_lingkong.c',161,178)+'CAN2 STD0x280、4路LE int16；'+L('转换','application/robot_cmd/CAN_cmd_lingkong.c',246,291)+'iq≈tau/.32×62.5夹±2000。'+L('轮反馈',R,448,460)+'speed degree/s→rad/s、iq×16.5/2048 A。MF9025这一链不是DM3519 codec或其Kt校准。',
'- '+L('校准帧caller',A,1566,1581)+'四个CALIBRATE.reached同时满足才发FE写零；硬件持久零与软件offset/ratio须一起复核，当前没有执行校准/使能/通信或物理测试。','',
'## 5. IMU真实路径与时序',
'- '+L('IMU_task',F,224,266)+'先Publish数据再delay7→BMI088自检/init失败100ms重试→IST8310 init循环→一次read/AHRS_init→SPI1 DMA。磁读更新虽注释，初始化IST循环仍active，别按头注释判断可省。',
'- '+L('IMU IRQ',F,627,774)+'PC4 accel/PC5 gyro DRDY→imu_cmd_spi_dma，gyro优先→SPI1 RX DMA2_Stream2完成→SW EXTI0→vTaskNotifyGiveFromISR→任务ulTaskNotifyTake→read_over/LPF→AHRS_update→get_angle/UpdateImuData。',
'- '+L('SPI1','Src/spi.c',91,145)+'PB3 SCK/PB4 MISO/PA7 MOSI，CS gyroPB0/accPA4；DMA2 RX S2/TX S3 channel3。'+L('DMA IRQ','Src/dma.c',53,58)+'priority5、EXTI4/9_5 priority5/EXTI0=6，按FreeRTOS syscall ceiling5配置。',
'- '+L('BMI配置','components/devices/BMI088driver.c',66,115)+'gyro2000°/s, ODR1kHz/116Hz带宽，accel3g/800Hz；'+L('AHRS dt',F,268,332)+'固定.001s，由gyro通知驱动、accel异步held，不是原生2kHz相干20样本包；二值flag/通知合并无公开drop/overrun/mean计数。',
'- '+L('frame',F,45,49)+'sensor→board=[raw_y,−raw_x,raw_z]，'+L('量纲','components/devices/BMI088driver.h',24,46)+'gyro系数.0010652644rad/s/count、accel.0008974359m/s²/count。'+L('public fields',F,388,437)+'Euler(rad)与body gyroXYZ、proper accel；pitch_vel=gyroY，不是任意roll下Euler导数。',
'- Quaternion/rawgyro/acc指针可读，但该public更新路径未赋epoch/seq/quality；AHRS_update实际来自已列AHRS.lib（本次不读/运行binary），IMU_solve.c虽编入且有EKF函数，selected application无其init/update caller，别宣称当前EKF活跃。',
'- 原C3输入需新的有界coherent packet/真实sample+arrival+aperture/age/overflow/installed-frame/lever/calibration绑定，不能用这些异步全局指针或1ms tick冒充已绑定100Hz/2kHz采样。当前仅识别可复用底层。','',
'## 6. 失联→动作：可达与缺口',
'- '+L('RC watchdog','application/other/remote_control.c',573,588)+'direct DT7需receive_count>5且age<100ms；离线→'+L('异常/模式',A,282,335)+'DBUS_ERROR→CHASSIS_SAFE。IMU仅判指针NULL，提前Publish不等于初始化/新鲜度已通过。',
'- '+L('SAFE控制',A,1195,1218)+'joint设vel0；'+L('SAFE send',A,1609,1656)+'MIT Kp0/Kd4（不是失能）、轮stop-PID值按torque发送。OFF才joint全0 MIT＋轮torque0，'+L('DmMitStop',D,332,337)+'仍不是FD停使能/硬件断电。',
'- DmDisable/DmClearErr/ScanOfflineMotor在selected application检索仅定义；motor.offline和DM fault nibble未接ChassisHandleException；'+L('detect defaults','application/assist/detect_task.c',265,312)+'gyro2ms/accel5ms等诊断不等于控制停机，lost callback默认NULL（仅OLED例外）。',
'- Joint错误比较|feedback tor|>25，而实际合法12bit解码域±10，因此不把这一判断当有效过扭保护。DM本机超时/故障停止行为及电机固件参数未知，不能从0xD枚举推已执行停机。',
'- '+L('transport','bsp/boards/bsp_can.c',33,45)+'最多20次mailbox poll后无条件AddTx，忽略HAL返回、没有完成ACK/expiry/atomic6轴owner；'+L('pacing',A,1504,1526)+'局部uint8_t cnt未初始化即%2，250us busywait依赖'+L('SysTick','bsp/boards/bsp_delay.c',7,43)+'。这是静态待复核点，不是已观测故障复现。',
'- '+L('Error_Handler','Src/main.c',225,231)+'为空；selected IOC/main没有IWDG/WWDG配置。未得到独立硬件watchdog/总线断线/调度冻结时完整停机证明；32bit HAL tick也不是新核心要求的64bit monotonic ns deadline provider。','',
'## 7. 复用交付与下一绑定',
'- [CANDIDATE_BINDINGS](<CANDIDATE_BINDINGS.json>)给12项：MCU/RTOS/CAN1/CAN2/DM发送/反馈/坐标/LK轮/IMU DMA/frame/失联/transport。均是source候选，不授予MOD4发送、contact、校准或时间资格。',
'- 先保留原BSP启动/RTOS/中断/HAL CAN与BMI088驱动，另审typed packet、单一发送owner、finite/域/反馈检查、失联锁存、时钟与driver limits；四DM旧机方案不替代MOD4具体DM8009P/DM3519型号/固件/ID/符号实测。',
'- 无新增控制器/BSP/参数/刷写/PHY/FK/test/build/Zip脚本执行，未改selected/oldcore/原包；本审计缺选文件0。一次路径猜测application/robot_typedef.h不存在，已按include path定位application/typedef/robot_typedef.h，不是原包缺失。',
'- 代码静态call/compile配置证据与物理板/实际image事实分层；模型代理另负责摊卧起立行为，本报告不抢该任务或改旧行为。small [RECEIPT](<RECEIPT.json>)保存实际source SHA/未执行边界。']
report='\n'.join(lines)+'\n';assert len(report.splitlines())<=100
with(O/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write(report)
# Verify every actual source-line citation stays in the selected subset and valid file line range.
import re
links=re.findall(r'\]\(<([^>]+)>\)',report);line_links=0
for x in links:
 xp=x.split('#',1)[0];p=(O/xp).resolve();assert p.exists()or p==O/'RECEIPT.json'
 if '#L'in x:
  frag=x.split('#L',1)[1].split('-L');a=int(frag[0]);b=int(frag[-1]);assert 1<=a<=b<=len(p.read_text(encoding='utf-8').splitlines());line_links+=1
# No mutation: recheck precisely the reviewed subset, not 391 files or original archive.
for r in verified:assert sha((S/r['readable_relative']).read_bytes())==r['readable_SHA']
assert rec(M)['SHA']=='33a79a69e5ebd1be437b05c75de378359d969f63d0761aa9303e79ce2a47a98d'
save('RECEIPT.json',dict(status='SEALED_STATIC_OLD_DEPLOYED_SOURCE_CHAIN_AND_CANDIDATE_BINDINGS_NOT_MOD4_HW_OR_FIRMWARE_QUALIFICATION',report=rec(O/'REPORT.md'),report_lines=len(report.splitlines()),source_line_links=line_links,binding_table=rec(O/'CANDIDATE_BINDINGS.json'),source_subset=rec(O/'SOURCE_SUBSET.json'),manifest=rec(M),reviewed_subset_count=len(verified),subset_final_SHA_unchanged=True,required_compiled_source_members=required,target='standard_robot',archive_opened=False,git_or_unselected_payload_read=False,source_code_executed=False,builds=0,flashes=0,hardware_IO=0,new_PHY=0,FK=0,new_agents=0,old_sources_edited=False,actual_flashed_image_SHA='UNKNOWN',physical_MOD4_binding=False,source_path_lookup_note='application/robot_typedef.h not found; resolved selected application/typedef/robot_typedef.h',missing_selected_source_requests=[]))
print(json.dumps(dict(status='PASS_STATIC_AUDIT_CLOSED',report=rec(O/'REPORT.md'),report_lines=len(report.splitlines()),source_line_links=line_links,bindings=rec(O/'CANDIDATE_BINDINGS.json'),receipt=rec(O/'RECEIPT.json'),reviewed_files=len(verified),project_members=len(buildfiles),source_bytes=sum(r['bytes']for r in verified)),indent=2))
