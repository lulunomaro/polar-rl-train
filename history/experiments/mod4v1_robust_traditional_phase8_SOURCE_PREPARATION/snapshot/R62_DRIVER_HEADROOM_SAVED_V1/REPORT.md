# R62 driver headroom：仅saved两hard tick

**结论：两轮保存的同stage速度在相邻hard tick均跨负向no-load，box由含零转成只许正τ的mandatory-brake；这是模型允许box/输出一致性，不是clip事件归因。**

- Catalog仅Office/ACL，无robotics匹配；仅saved [EXTRACTED](<../R62_AIRREF_RESPONSE_CAUSAL_V1/EXTRACTED.json>)/[FACTS](<../R62_AIRREF_RESPONSE_CAUSAL_V1/FACTS.json>)七PRE小窗及必要原driver小源/producer metadata，0原raw reopen/driver调用/controller/model/PHY/QA/Git/agent。
- [capture:43–60](<../MINIHOP_AUDIT_V2/contact_grade_v2.py#L43-L60>)直接存actual_dq和bounded；[实际driver:12–15](<../MINIHOP_AUDIT_V2/physics_bridge_minihop_rm_v2.py#L12-L15>)的actual_dq=d.qvel[self.vids]。不是packet速度，更未从τ反解ω。
- [RM构造:26](<../physics_bridge_rm_grid_v1.py#L26>)按[ORDER:14](<../../traditional_control_20261101/control_core.py#L14>)映射signed6=LH LC LW RH RC RW；wheel索引2/5。常量来自此实际RM构造、匹配producer SHA；DR未重设该box三常量。
- [原clip:127–130](<../../traditional_control_20261101/control_core.py#L127-L130>)：v=clip(ω,±N(1+P/S)); lo=max(-P,S(-1-v/N)); hi=min(P,S(1-v/N))。N=55.3557rad/s，S=28.18532894736838Nm，P=5.775909774436091Nm。
- 预声明[代数门](<METHOD.json>)1e-9Nm：直接源表达式与重排仿射式比较，并检查已保存输出对box的重投影残差；没有执行原函数或改任何物理gate。

|PRE s|wheel|ω rad/s|ω/N|lo / hi Nm|saved applied Nm|applied-lo Nm|hi-applied Nm|mandatory brake|
|---:|---|---:|---:|---:|---:|---:|---:|---|
|2.3335|L|-53.689959212|-0.969908414|-0.848141240 / 5.775909774|-0.798005168|0.050136072|6.573914943|False|
|2.3335|R|-53.808716324|-0.972053760|-0.787673966 / 5.775909774|-0.787673966|0.000000000|6.563583741|False|
|2.3340|L|-56.779766928|-1.025725751|0.725088741 / 5.775909774|0.725088741|0.000000000|5.050821034|True|
|2.3340|R|-56.220409527|-1.015620966|0.440282075 / 5.775909774|0.466640386|0.026358311|5.309269389|True|

- 全4条scalar algebra最大差4.44e-15Nm，输出重投影残差最大0Nm；速度guard active条数=0。
- 首tick各box含零=True；两轮跨负向no-load=True；次tick两轮mandatory-brake=True。这些是直接signed ω/box判断，不证明某个单独clip stage触发或该机制是闭环失败唯一原因。
- 表中余量/on-bound是相对于同PRE允许box；actual_tau为最终bounded d.ctrl模型命令，非独立测得电机力矩。原链仍有D4/PD/inner clip/gain/outer clip，raw-PD和clipmask未记录，不补值；电流/母线再生/实机资格不在本证明中。
- 原R62 1/4、002 sealed/default-off、所有旧报告/源保持不变，不拟合gain/第三h。PH8 pending；[RESULTS](<RESULTS.json>)保留全精度，[SOURCE_LOCK](<SOURCE_LOCK.json>)与[receipt](<RECEIPT.json>)保留选定小源SHA。
