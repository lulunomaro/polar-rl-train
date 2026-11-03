# 阶段1首个真实接口窗口：pre-SDK 导入失败，完整闭合，尚无采样结果

## 已发生的事实

| 项目 | 实际结果 |
|---|---|
| 最终source payload | 276个文本文件／3,306,783B；包含259项完整引用镜像 |
| 真实静态输入preflight／stage | 通过；3675个实际stream-hash文件、3592个完整原static文件，3处同名原bytes另存保全 |
| 原资源准入 | 2026-11-03 20:24:29；GPU0 4090／24203MiB空闲；privateGPU EX＋finite EX，canonical ownerNone／仅读 |
| 场景目的 | E3-only／N80／64-control／syntheticzero6，非策略评测或训练 |
| 实际启动 | controller1541919、原parent1541926、仅worker1541935 |
| 首个错误 | worker第35行 `ModuleNotFoundError: No module named 'launch_storage_contract'` |
| 控制采样 | 原READY、共同GO和FINAL均缺失；controls/callback/optimizer等producer计数保持null |
| 结束与释放 | 原childwait RC1；外层实际parent Popen.wait RC1、controller无错误；privateGPU EX及finite EX已释放 |
| 接口／阶段2 | Gate1 UNKNOWN；capture_interface_passed、exact、stage2_GO均false |

此次错误发生在torch导入、runpy环境构造之前。由执行位置推断SDK constructor未到达；这与producer实际发布的计数区分，不将缺失计数编造成零或技能0%。

## 原因与修复边界

实际installed inventory与[原helper取证](<reports/PHASE1_CAPTURE_V1_PRE_SDK_IMPORT_FAILURE_SOURCE_EVIDENCE_V1.json>)确认：两个完整原文件一直存在于 `worker_sources/parent/`，不是复制漏件。

- [storage helper](<discovery/phase1_first_startup_failure_v1/worker_sources/parent/launch_storage_contract.py>)：117B、`e40b51db…`。
- [capacity helper](<discovery/phase1_first_startup_failure_v1/worker_sources/parent/n80_gpu_capacity.py>)：653B、`ab26d1b2…`。

V1入口在首次裸import前遗漏该目录的bootstrap；之前metadata CPU验证只走顶层module import，覆盖不到main里的此路径。NEW V2将由main与metadata使用同一个 `bootstrap_original_helpers(group)`，校验完整模块origin、bytes/SHA与module cache，保留原函数和原parent资源逻辑。

源码复核另发现两条此次尚未执行到的close问题：nonfast validator漏helper实参；binding文件自动增加epoch而intent/returned嵌入原dict，严格相等检查可能失败。它们在NEW V2做独立修复及真实临时文件roundtrip测试，不冒充此次MissingModule的历史原因，不通过collector剥字段弱化验收。

## 回执与状态

- [真实stage回执](<reports/PHASE1_E3_CAPTURE_V1_ACTUAL_STAGE.json>)。
- [首准入／错误／实际wait快照](<reports/PHASE1_E3_CAPTURE_V1_FIRST_ACTUAL_ADMISSION_SNAPSHOT.json>)。
- [完整闭合metadata结果](<reports/PHASE1_E3_CAPTURE_V1_ACTUAL_CLOSED_20261103_204735/CLOSED_RESULT.json>)：`FAIL_CLOSED_CAPTURE_EXECUTION`，collector退出码1忠实保留原失败；source闭包与plan检查通过。

结果里的成功执行检查要求RC0，因此相关`checks=false`不等于没有发生wait或没有释放；实际RC1 wait及EX释放原件单独保留。旧root、旧13封件和失败证据保持原样，没有重放。

H1、所有母本/Registryv12、原物理/DR/速度/接受标准均未改变。当前没有自己的native任务；下一步先封存和审核V2，再以全新root做原资源门下的最小接口验证。阶段2训练尚未放行。此报告在阶段31提交后生成，待阶段32追加归档。
