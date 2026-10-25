# 提速实施包交接：V2候选已准备，未安装

最终采用本目录 `payloads/` 的四个源文件；不要采用上层V1 cache。当前68源码、进程、预算与原writer均未触碰。root计划在68正常own full-save、SDK close、child wait、原费用结清边界之后，将提速候选放入新69根再接续；本包不创建新owner、不kill、不复制ledger、不热补68。

## 可复制文件与接口

| 本目录文件 | 目标（相对对应payload根B） | SHA256 |
|---|---|---|
| `payloads/h1/h1_production_control_prefix_trace_v1.py` | H1 `h1_production_control_prefix_trace_v1.py` | `a24011df3a43e580fa15037791c30e9f8dacdaf4d0f6b9dd62b00276798414bd` |
| `payloads/h1/sampling_trace_npz_lossless_v1.py` | H1 `sampling_trace_npz_lossless_v1.py` | `ce2335df8ac300fb52659d69fd41df82dd8a58964adc990448709cd332d8057f` |
| `payloads/recovery/job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py` | E3 `job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py` | `7e1d28e8ef1622f7923c00358f2683ea8682cf4553f0e1aacf40e68446b2ae2d` |
| `payloads/recovery/job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py` | E3同runtime目录 `e3_reset_bank_cache_v1.py` | `ba4f5cd584f911a9313de2f60f6465b1114f645a47c1ffcda5fcc9930dd8109a` |

installed CPU checker为 `verification/sampling_acceleration_installed_CPU_v2.py`，SHA `256f803270d8ec6702e0d120670d57bf79c9145c169a71bc4742dad7ac0dcf15`。它独立可复制到两个B根的CPU检查模块路径，不依赖本地verification子目录。

API是 `check(B, key)`，key为`h1`或`recovery`。返回`passed/status/key/base/expected_base_SHA/candidate_SHA/exact_source_allowlist`；E3另有bank SHA、一次读取计数、normal/inference构造+选择case等。异常直接抛出，不能改成通过。CLI可用`--root B --key recovery --report 新唯一JSON路径`。root只在新root执行一次相应检查；E3 fresh CPU将新payload的32MB bank读一次，随后所有构造均复用这份内存字节。不要在guard和target重复调用消耗同一新检查。

H1 checker本地API/CLI已通过；E3分支只完成代码/编译准备，没有在本机再次读原32MB bank执行。它面向新69根的fresh CPU验证，不是重跑旧bank once。

## 精确allowlist

原H1 trace SHA `d14f69cd14a1297f558ea7f7df83f17f735cec2f99da037f3b2d623a2f590dd6`。仅新增helper import、`H`改bounded-buffer full SHA、persist中的NPZ写入调用改为逐字段stack+DEFLATE1。所有其他AST（包括preupdate save、row capture、原子rename、producer SHA/index、rows清理、原异常路径及retention挂接）不变。retention源码和政策不变。

原E3 runtime SHA `0f8fd2c24b25a4a80f18bb4c3aae016acfa6873b418d6e2e32a3f72ff6199fbd`。仅新增cache import、构造时一次cache初始化、place_declared_fall的bank/几何准备块和等值source SHA表达式。SDK root/joint setter、recovery.reset、publish的调用AST与顺序、0.0001m margin、root_xy/零速度、receipt其他所有字段以及其余类/module AST不变。

V2相对V1 cache只新增构造器 `@torch.inference_mode(False)` 和 `@torch.no_grad()`，令缓存拥有version counters，外层RSL inference模式下也能校验缓存不变。逐reset仍检查文件realpath/dev/inode/size/mtime/ctime、joint order、cached tensor identity/shape/dtype/device/stride/version；变化抛错，不静默reload。返回的selected张量是新对象，SDK调用不能修改缓存。source_sha属性只读，实际调用先通过selected_geometry的validate，再读取pick/source_sha；没有删除任何SDK getter/health审计。

V2包装复制时将runtime源CRLF规范化为LF，因此是AST完全相同而非字节相同；上表和manifest记录最终真实字节SHA。H1 helper只修正说明为candidate implementation，未冒称已安装。

## 已完成的CPU证据与保留失败

上层 `reports/INTEGRATED_H1_E3_REAL_BANK_CPU_V1_ACTUAL.json`：已授权的真实bank只物理读一次，大小32,022,178B、SHA `78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83`。执行原函数AST与候选比较，bank序/反序、全部13recipe、非连续selected、520selected及20k启动selected，共7case；plant/phase、setter序列及张量、receipt、margin、selected/unselected和RNG均一致。20k原函数CPU49.19s与候选0.0129s仅是CPU函数计时，不是现场GPU/整训收益。

同一报告的H1实际persist/原retention CPU fixture通过：27字段dtype/shape/tobytes一致，first1/latest2、incomplete、current failure、unpaired保护相同；所有已发布文件SHA/bytes真实；注入写失败保留partial/rows及原错误。preupdate fixture明确是合成标记字节，不冒充真实模型；真实preupdate回调由未改AST证明保留。

本目录 `reports/V2_CONTEXT_AST_SYNTHETIC_CPU_READERFIX3_ACTUAL.json`：不二读真实bank。严格AST证明只增加context decorators；synthetic fixture同时覆盖normal/inference构造与inference选择，输出相同、缓存有version counters、selected无alias、缓存inplace修改仍拒绝、全局CPU RNG不变。V1在inference构造的真实RuntimeError完整保留在该报告，不把V1 normal通过扩大成inference通过。

V2原读者失败也保留：第一版误将CRLF规范化后的runtime当作字节相同；第二版导入原permutation的文件名缺少模块加载。修复只改checker，最终candidate源码未为读者失败改动。上层初版builder误用分号AST索引的失败同样保留。

## joint order与剩余实证

`verification/robot_joint_names_evidence.json`提取N68实际H1 SDK stdout中0..29完整关节顺序。它不是bank序，对应原permutation为 `[0,7,9,10,11,18,20,21,22,23,24,25,26,27,28,29,1,3,5,8,12,14,16,19,2,4,6,13,15,17]`。已保存N68 H1/E3计划asset manifest具有相同USD SHA `694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87`；E3新root实际SDK顺序仍需在原安装/启动回执中记录。候选始终调用原joint_permutation并绑定真实r.joint_names，不假定bank顺序。

剩余由root处理：新69 installed CPU源码/新bank fresh检查、原admission guard精确新target/hash绑定、实际SDK启动及正常selected reset回执、完整save/exit/original writer边界和真实吞吐测量。本子代理没有使用SSH/GPU/SDK scene/actor inference/physics/GUI/signal/Git，也没有二读原bank。没有新增数值/FP64/native/query门槛，不重跑既有16万查询。

继续保留FP32生产、17Adam、全部状态字段、2.5ms/TGS32/4、H1×4/E3×8、全部health/hardware/finite/成功条件、原25GiB admission与8GiB saved-stop。加速的真实cycle收益待新root实际测量；CPU比率不冒整训提升。

## 本轮结束后的协作约束

人类新约束：**这一轮过后暂时禁止使用子代理**。本轮既有implementation验证收尾后，不自动续task，不再spawn；root后续直接处理。本代理本轮也没有再派代理。

所有新增source、报告、读者错误和合成fixture索引均pending root统一Git归档；旧V1/V2错误及原分类保留，不能把本地准备称为已入Git。
