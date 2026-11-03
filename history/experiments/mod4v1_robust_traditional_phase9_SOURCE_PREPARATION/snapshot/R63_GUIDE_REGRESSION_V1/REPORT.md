# R63 seed4610：原pass→新guide3，single-TRAIN只读事实审计

- 原R60 smallresult local=True guide/hard=0/0；新local=False guide/hard=3/0，complete800/16000，endstable=4.559999999999947。旧raw未读，score不改。
- push/decision：{'command_time_s': 2.0100000000000002, 'sensor_time_s': 2.0099999999998386, 'sensor_age_s': 0.0, 'root_post_time_s': 2.019999999999842, 'phase': 'timed_push', 'landing_capture_started_s': None, 'landing_transition_weight': 0.0, 'landing_position_ref4': [0.45417412979711813, -0.041509868072373446, 0.45417412979711813, -0.041509868072373446], 'legacy_target_q4_NOT_current_capture_ref': [0.45417412979711813, -0.041509868072373446, 0.45417412979711813, -0.041509868072373446], 'observer_disabled': False, 'spring_release_applied': True, 'requested_tau6': [-13.971652388068662, 7.398806283733988, 0.13751944976397204, -13.327533083263527, 11.394719742383637, 0.13989779827605917], 'forward_command_m_s': 0.9, 'position_decision_time_s': 2.0, 'position_latched_push_time_s': 2.0100000000000002}。
- operational air onset=2.124999999999877，确认POST=2.1449999999998837；mainrear-firstflight原result=2.4559999999999875只join原row，不冒whole-robot净跨。
- 事件表：stage | positive接触/朝机器人normal描述 | same-PRE pose | adjacent100Hz实际状态
- landing：2.495000000 | right_tire→ground/top_up:7421.33N | z=0.303081395,pitch/roll=[-13.541701073701963, 2.8025514678109977] | phase=timed_capture,w=0.35200000000000053,obsDisabled=True
- guide tick1：2.513500000 | right_tire→ground/top_up:582.264N; guide_wheel_07→rm_bar_011/top_up:7674.26N | z=0.270362472,pitch/roll=[-13.062666182475485, 2.5270683879372244] | phase=timed_capture,w=0.5000000000000007,obsDisabled=True
- guide tick2：2.514000000 | guide_wheel_07→rm_bar_011/top_up:1252.54N | z=0.269700605,pitch/roll=[-12.929049314617037, 2.469652904318936] | phase=timed_capture,w=0.5000000000000007,obsDisabled=True
- guide tick3：2.514500000 | left_tire→ground/top_up:1584.1N; guide_wheel_07→rm_bar_011/top_up:473.486N | z=0.269063418,pitch/roll=[-12.779012778902505, 2.4038087711189533] | phase=timed_capture,w=0.5000000000000007,obsDisabled=True
- capture实际首control=2.41，首正K/ff/ref weight=2.42，observer实际恢复=2.66；brake配置=2.5/首control=2.5。
- 各guide control bracket的实际landing_position_ref4/weight/requestedτ6、same-stage driveτ6/velocity6以及command/sensor→drive时间差见EVENTS；legacytarget另标，不当当前capture参考。
- 2k根PRE旋转/XYZ与force同stage，rootPOST另时刻；2k实际各腿q未知，不从有D1D2 encoder推导。3ticks不是3contact points，positive点即使<1N也完整保存。
- 单案只给landing/支撑域/phase仲裁事实；先后不证明capture/observer/brake或弹簧FF为唯一原因，不选新target/gain，不添资格门或自动PHY。
- 仅2new raw各1open/总16800行<=17600；小源先后SHA核对；producerSHA引用未重hash；no旧raw/其他seed/H5/ZIP/mesh/新PHY/FK/模型/QA/Git/agent。PH9pending。

证据：[EVENTS](<EVENTS.json>) · [预声明](<METHOD_PREDECLARED.md>) · [SOURCE_PREEXEC](<SOURCE_PREEXEC.json>) · [RECEIPT](<RECEIPT.json>)
