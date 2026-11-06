# 中断前R31实际结果保留：E1冻结回归，不重跑

[COLLECTION001](<COLLECTION001/RESULT.json>)已消费、三个新原生case均已完成，各1200控制/24000物理/fresh模型DR1；总3600控制/72000物理。无旧case/raw/QA重放。

- seed520210 E1名义站立原15门与100Hz scope均true；左右100/100%、whole/guide/hard0，XY漂.0108078m、站立vx RMS.000923586、末段.000229297m/s。
- 依预声明，名义过后才执行新seed520211原版/E1配对；初始DR收据/qpos/K相同。实际两者D3=10ms，不是按结果挑选。
- 原版→E1：roll RMS.03034445→.02453212，停车RMS.02939354→.02811876；但whole4→14更差。两原screen均false、仅whole0原门未过；scope均true/XY超量0。
- 该pair仅1份独立DR设置，E1仍未切默认，不称鲁棒通过/95%可靠性。E1公式未改、旧控制力矩3/3与旧暂停seed不动。

相关job pwsh-1b9be0948a144c1e、pwsh-9e0485b6ebe641d1、pwsh-d0d799e2a25e4227此前均已收0，不重收通知。此结果在用户14:18指出推进偏差后补写入小记录，并随新[实际LQR调参](<../DIRECT_LQR_TUNING_V1/README.md>)一并归档；不再把继续旁路/重gravity审计当作调参成果。全部9大raw仍只producer流式收据，未额外读/hash。
