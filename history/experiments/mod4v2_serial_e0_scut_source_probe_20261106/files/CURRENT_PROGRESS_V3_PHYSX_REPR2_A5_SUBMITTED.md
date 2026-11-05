# MOD4v2共享原生机械止挡修复：新表示包已构建，A5仅提交待真实验收

当前Goal664 rev1 active；9正式专家含H1，非86两卡原单writer/budget/资源合同，旧母版及Registry不变。全部实际PPO仍0、无新learner成功、无技能毕业。不是重启旧E3/Fudan/SM路线。

## 真实阻点和修复范围

[A4真实20k SDK限位读回](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/ADMISSION4_NATIVE_LIMIT_FAILURE_SUMMARY.json>)证明左右共10被动CAD有限端在native全部为±FLT_MAX；主动/跟随无限表示与双有限gas行程另存原数据。不是1e-6误差，未放宽检查。共享gate只启动H1，PT前止步，另8不GO；controller1676829/owner1676836/worker1676962全实际close/wait/costsettle/释放；A3资源timeout/只读release也保留，不延长旧1800窗。详见[机械阻点](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/NATIVE_ADMISSION4_MECHANICAL_BLOCKER_V1.md>)。

新包 `F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60_PHYSX_REPR_V2/package`，原HW300N60包/spec/失败不覆盖：

- USD **47be6619a1ec78e7c1514aab673996f545feedb24fda05da3f359d69f4a4be7f**；contract **5cf79932fb1f11edebcfa7e35ff63ed658bbfdf1dd56706ad201b3c4fd3141a1**；adapter **405391d463980c1628532274709ea0e64c8a220a7de718b2ba6b860cfa3990dd**。
- 仅10个原None被动反向端用±π（USD±180°）backend representation；所有CAD有限端原数值/原USD属性保持，8主动+跟随仍无限、双有限gas原140–200mm/300N/k2000d3/target.170639441不动，几何/质量/COM/惯量/闭链/传动/277mesh不变。新contract明确hardware_one_sided_limits/native_impl_limits，adapter只接受明确原硬件+精确表示端+新包SHA绑定，未简单删保护。
- 证明范围仅旧neutral-signed branch canonical passive q∈[-π,π)被[-π,π]包含，C∩H∩R=C∩H；common active turn不改变局部passive。不是新硬件止挡、任意passive展开绕圈或3D全域碰撞证明，没有伪称−π严格内点裕量。
- [一次实际pxr构建收据](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/PHYSX_REPR2_BUILD_RECEIPT.json>)中完整USD撤销仅10端点/声明metadata后文本等于旧层；MJCF仅10range改变，其余结构一致。7文件新绑定与模型参数/kinematics/277mesh字节证明在收据。未运行物理仿真/训练。
- [一次local24检查](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/PHYSX_REPR2_LOCAL_VALIDATION.json>)：实际新adapter prepare与MuJoCo编译/20轴SI范围/31robotbody+nq37nv36nu6neq10/mass14.29414通过；simulation_steps0、native_PhysX_verifiedFalse/100HzFalse。local PASS不是原生PASS。

## 新worker与A5

[worker v3](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/worker_mod4v2_expert_migration_v3.py>)基于已执行v2，仅readback分开hardware_expected与native expected；把gas drive getter核验放到同一次原zero env.step之后。源实际gas_spring_preload是mode=step，原Mod4Env在super.step前应用并写contract target；零步前读target不能证明已执行preload。没有额外physics/obs/RNG、没有奖励/DR/网络/学习率改变，仍原1zero=8physics/2feedback与1e-6限位门限；CAD和新增表示端的含义分别以硬件/实现contract为准，不能把CAD端也称新增非硬件端。

新owner仅替换asset/contract PIN，全部函数AST与已运行H1-gate owner一致（gpu/account/authority/原actualwait/close/预算/生命周期不动）。初始只H1，真实新20k限位/gas/闭链/8physics2feedback/PT0 receipt通过才放另8进入双slot。兼容learner全actor/critic/STD/normalizer/17Adam/LR/iter一次继承，旧env/DR/history/queues/RNG仅CPU历史，新v2唯一fresh reset；首20更新不当技能通过。

A5 root `MOD4V2_NINE_FULL_LEARNER_MIGRATION_ADMISSION5_20261105_230103_1793890863774950400` stage295共享非PT文件/九完整runtime+lib+staticNPZ、Linuxowner import-only rc0、SDK/PT/GPU/GO/C0；已一次dispatch1793891034.6345866/controller1678722。唯一observer **pwsh-ebd6ddb3912e4e1d**，首metadata1793891039全部GO/native/learner null，仅原门控资源等待/初始化，不声称新asset已解决native或PPO。

冻结eval worker仅source已备，actual training全cohort关SDK/actualwait/cost结清/释放后才独立eval准入，原N80/各scope/seed20260928/fullDR不改；E0/S50完整grader仍null，所有专家毕业必须actual而非rc0/加载/20次更新。

本actualA3timeout+readonly release/A4native错误、builder子任务初失败后续完成、真实构建/local24、新worker与A5submission、全部D文本及新包adapter/contract/requirements源码，已feature-only唯一annotated一次归档并真实远端核验：**9c2dcd2e3a06ffc03105fed9329d758700b2938e**，tag **trial-20261105-mod4v2-physx-stop-representation-repair**，annotated对象 **f7ea113aff63547fabcf4b2796d95c2f8b3adc70**，107索引条目/clean/remote branch-tag-peeled一致；当前main只读 **f3ebf3c4977f7609252a5fcc4a62f58e21b5da2f**，未push/reset。原recorder validation/redaction/hashes与exact stagedset保留，没有为Git/状态读weights/旧raw/largeUSDmesh或重放旧once/physical。archive jobd7e08676c7b44d01 completed0/fulloutput collected；本推送后核验补记下一meaningful阶段捕获，不造验证文件链。A5 observer ebd6ddb3912e4e1d仍running，尚未收见GO/native/learner/PPO新阶段；提交和local24不是native成功。
