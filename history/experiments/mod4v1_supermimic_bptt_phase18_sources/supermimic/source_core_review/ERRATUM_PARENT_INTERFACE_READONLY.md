# 封版后只读接口复核

核心封版 SHA256：`2603308f1adfe65f576eaf2aa3e0275d8465f110e6edd6e3db38304bf3e72039`，35812 bytes。封版后不再改核心；任何后续修订仅通过新erratum提议给父。

## 父显式授权只读的两份源码

- [native_supermimic_bridge.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py>)
- [worker_supermimic_bptt.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/worker_supermimic_bptt.py>)

没有修改父目录，没有运行、导入或实例化其代码。复核时的源码副本另存 evidence，避免父之后更新时混淆证据。

## 接口结论

本次静态复核未见必需方法/参数的确定性崩溃点：

- parent MDP的obs为 `invariant_features + previous_action + xi`，teacher offset=S+6正确，raw35没有再次tanh或RunningNorm。
- goal用xi的前3维，即原actor35 command3；context-aware签名与core一致。
- state/transition字段、pre-reset物理s1与done xi1_validFalse对齐；stateinfo的下一episode自成新history边界。
- exact=False环境snapshot经safe转换后为weights-only可读的primitive/tensor结构；明确freshEpisode恢复，不冒充PhysX/contact warmstart。
- teacher wrapper仅代理obs_norm/goal_norm，在当前core实际使用路径足够；enc/dec/hist只在vendor policy建造时使用，不在包装后访问。
- core probe并非固定first parameter：从opt_pi中requires_grad且本次grad非None且abs.max()>0的参数中选取，zero输出层首步encoder梯度0时可选decoder，后续不会因此永久0计数。

## 后续runtime需明确的非阻断项

1. parent valid-start当前全True且无imagination_timeout。若已知episode/命令剩余时长，建议父加入硬cap或valid-start约束；学习done概率不是精确时间边界证明。
2. core next-xi默认学习全部维。父可实现project_predicted_context固定episode常量DR、维持onehot/phase范围、精确last_action槽与可知queue shift；否则明确为可学习上下文近似，监测漂移。
3. parent teacher.assert_frozen检查的是bootstrap CPU root的identity/version，不是独立验证GPU actor参数hash。teacher.requires_grad=False和学生optimizer过滤可阻止已见更新路径，但runtime receipt应额外检查实际actor权重未变和teacher obs梯度非零。
4. raw actor35中原last_action槽和outside previous_action必须同义；bridge保存的是送入原action pipeline的clipped raw command，不是PD torque或延迟输出。
5. 核心的跨时receipt同时要求future->a0与future->s1->a0 WM VJP，0敏感性/完全饱和阶段即便pi optimizer运行也只记unverified，不满足3000目标。不要退化回method调用数计数。
6. 只有AST/stdlib结果，不是当前SDK runtime成功保证；本机Torch未安装，没有替父执行模型/SDK/GPU动作。
