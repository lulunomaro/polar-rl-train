# 串行E0阶段：已准备记录的跨午夜日期门错误及同一trial续完

2026-11-06 +08:00，新record_serial_e0_scut_phase_once.py已完成原record_experiment的note/所有归档文本脱敏、路径/大小/每文件hash/空staging校验，并写出唯一prepared record `20261106-mod4v2-serial-e0-scut-source-probe.json`，在git-add adapter错误地要求旧`20261105`前缀处AssertionError。HEAD仍9c2dcd2e3a06ffc03105fed9329d758700b2938e，无暂存/commit/tag/push，仅prepared目录与record两个untracked范围。不是实际凭据拒检，也不是GPU失败。

保留失败入口与现有prepared source/INDEX/record；不重跑recorder、stage、权重读取、物理或旧once。同一trial continuation将使用已写record的实际id/tag，而非当前日期猜测；复核原所有archive bytes/SHA/原redact idempotency，追加本失败说明、finisher源码和已真实闭合probe的own JSON，更新INDEX与record hashes后，执行相同原commit/annotated tag流程及两个短精确scope staged-set equality，再atomic feature+tag push/remote head-tag-peel校验。原validation/redaction/hash与main只读保持。

同时该probe已经独立收口：MOD4V2_E0_SCUT_PROBE_FULL_LEARNER_MIGRATION_20261106_043618_1793910978054991000，controller1693216/owner1693224，actual outerwait1793911530.0575306 rc0/reaped、innerwait/费用结算/授权释放true。reward_v2.bind→_RewardState._inputs在`joint_acc`类型或shape合取门失败。该文案未打印实际type/shape，不能据此断言shape错。native-before-PT、learner loaded和initial acceptance均未发布，新增PPO0；RC0未被当作执行通过。原closed metadata保留，未自动重试/改公式/放宽门/开hour。后续仅查明当前SDK实际tensor包装ABI，非零值fallback。

本报告与同trial追加内容先脱敏再入Git，workspace原源保留；后续远端核验以工具输出为依据，不造无限验证文件链。
