# R56 launcher补充审查（仅静态）

PASS：显式runner须在sourcefiles锁内；preparer支持独立或同pathSHA；protocol max_workers传递；R56传--review时核ready和checked_sources，RM前再核。freshbatch拒绝旧结果/批次，软件非零rc停止余波。

Flat/RM完整control profile仅去scene/terrain/case_id/cohort标签后匹配；只有实际flat gateTrue才准入对应RM，不是zero-step803/1809代替物理通过。

relative_V3/phase_durations_unchanged只指原公式/配置时长，非任意trigger浮点100Hz边界bit/tick完全一致。旧V1 since减法和prepare绝对和可差1tick；以运行phase/flags/clock日志为准，不引入integer-phase修复或新门槛。

本补充未执行launcher/旧QA/boot/physics或改core/protocol；两个machine reviews均有ready_for_physics和绝对path/SHA，父可用本launcherreview覆盖其本身source锁。
