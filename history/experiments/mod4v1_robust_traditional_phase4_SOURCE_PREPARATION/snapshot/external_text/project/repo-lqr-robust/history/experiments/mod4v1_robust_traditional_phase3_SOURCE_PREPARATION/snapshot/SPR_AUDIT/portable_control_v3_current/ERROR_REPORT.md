# V3-current — 全部错误、尝试与保留记录

1. [freeze_attempt_01.log](<freeze_attempt_01.log>)成功：14个当前来源、221个旧封存文件和6个固定TRAIN引用锁定；没有import plant或新physics。
2. [edit_attempt_01.txt](<edit_attempt_01.txt>)保留一次literal replacement不匹配：只因目标前导空格与同一行实际文本不同，工具未改文件；read后精确替换成功。不是C数值失败。
3. [host_objects_build_01.log](<host_objects_build_01.log>)首次strict GCC exit1，`saved_binding`条件初始化被-Werror=maybe-uninitialized指出；[首次源](<revisions/build_attempt_01/pc3_dispatch.c>)与已产生的两个partial host对象均保留。
4. 显式zero-init局部binding，并增加输入/状态alias检查；没有降warning或绕过检查。[host_objects_build_02.log](<host_objects_build_02.log>)exit0。后续把deadline/age元数据在callback前快照，旧draft对象/source保存在[attempt02目录代表源](<revisions/build_attempt_02/pc3_dispatch.c>)；最终[host_objects_build_03.log](<host_objects_build_03.log>)重编最终源exit0，根目录对象不遗留stale版本。
5. [unit_run_01.log](<unit_run_01.log>)4241/0；[unit_run_02.log](<unit_run_02.log>)6040/0；补显式not-initialized/not-armed边界后的[unit_run_03.log](<unit_run_03.log>)最终6509/0。每版unit源和build日志分别保留，不抹前版。
6. [reference_generation_01.log](<reference_generation_01.log>)成功，原Python64在两个TRAIN上对logged estimated14最大差均0。源码只有pure sensor/controller math imports，-B，mujoco_loaded=False；不是重跑机器人。
7. [replay_run_01.log](<replay_run_01.log>)3200行全部est/P25/isolated statusOK；[comparison_run_01.log](<comparison_run_01.log>)预先声明的数值budget零超限。[原C JSONL](<C_REPLAY_01.jsonl>)与[原参考CSV](<REFERENCE_VECTORS.csv>)完整，未删困难点或调整参数过线。
8. [cpp_run_01.log](<cpp_run_01.log>)独立C99对象+C++11 extern-C smoke通过，全部编译log留存。
9. [arm_build_attempt_01.log](<arm_build_attempt_01.log>)是**新V3-current源**的6/6 M4/M7 object，不是旧once/旧C1重放。2宏probe、6fromelf头均exit0；[原命令与对象SHA](<BUILD_RECEIPT.json>)、[检查日志](<object_inspection_01.log>)保留，无license绕行。

本轮唯一compiler失败是第3项，修正前源/partial objects未覆盖。初始化与mean/age/fault新增严化差异均在[README](<README.md>)列明：supported-upright显式声明、static坏gravity硬错、changed-payload重复包硬错、positive vector innovation gate及固定100Hz pacing。

阶段3 H2反馈仍未移植；数值proxy不是独立侧滑/世界位置。没有BSP/未知DM3519 CAN、BIN、板、ARM运行/WCET、Git、新agent、工具安装、holdout case选择或新physics。后续host resident adapter应单独开目录。
