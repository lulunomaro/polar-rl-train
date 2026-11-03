# MOD4部署派生第一阶段源码包

- 实际Keil入口：derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx；target/output均标STAGE1_UNBOUND，自动flash-before-debug与TargetDll flash选项已关。不开启/运行旧脚本、hooks、debug或flash。
- 文件级来源：391原text＋父批准32依赖，共423继承payload；其中2个窄patch、421个原bytes不变；新增2C/2header，derived共427文件。原2文件before在before/，PATCH_RECEIPT含可逆proof。
- 原165 target member＋4个新member现皆有文件；BUILD_CLOSURE_FINAL保留Windows大小写alias与未求值条件include。2个opaque库只复制，未ABI检查/执行；库存在≠可以link或上机。
- new_code是两组新runtime C/header镜像，与derived/application/mod4_port逐byte一致。仅旧target中的application/mod4_port路径加入工程；host recipe只编译new_code与host_smoke，不把镜像同时编两次。
- HOST_BUILD_01与smoke stdout是首次40 CHECK/0fail新C99候选事实，未重复。不含host.exe/target.bin/hex/axf，不含原ZIP或.git。任何后续重现另在新工作副本，先审工具/库/条件依赖；当前没有父批准的完整target build/执行/刷写。
- default provider/config/arm均未绑定；旧chassis motor入口不发FC/position/torque。NONE不证明旧硬件已停，STOP/DISABLE只是不同请求。实际MOD4 wheel型号/gear/ID/方向/codec/电流扭矩、clock/packet/ACK/stop与driver envelope仍待绑定。
- NEXT_TARGET_BUILD_PLAN列下一审批，当前不执行。workspace的README、VALIDATION和外置RECEIPT与此包配套；RECEIPT包含本ZIP SHA所以留在ZIP外避免自引用。
