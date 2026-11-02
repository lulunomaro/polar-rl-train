# ARM compile-only — 全部尝试/错误记录

- [armclang_version_01.log](<armclang_version_01.log>)：现有明确路径的MDK Plus5.26 / ARM Compiler6.10.1 / tool5d143200，exit0。
- [fromelf_help_01.log](<fromelf_help_01.log>)：现有同bin路径fromelf5d142900，help exit0；按实际help选择--text -v，不调用binary转换。
- [arm_build_attempt_01.log](<arm_build_attempt_01.log>)：脚本exit0；2个target宏预处理、6个-c object编译、6个fromelf头检查均exit0，failed_command_events=0。
- [BUILD_RECEIPT.json](<BUILD_RECEIPT.json>)：全部原exe/argv/log/exit与source/object bytes/SHA。每个target子目录保留全部stdout+stderr原文；没有抑制warning、复制host SSE参数或修订封存源。
- [object_inspection_01.log](<object_inspection_01.log>)：只读小ELF QA，6个ELF32 little-endian ET_REL EM_ARM、CPU/FPABI属性与宏一致，0失败。
- 本轮没有编译/license/工具失败，也没有换工具规避授权或静默重试；armcc.exe、armlink、BSP链接、BIN转换、仿真/HIL/flash均未调用。
- M7 fromelf Tag_FP_arch8的旧工具人类标签原样保留，并与CPU_arch v7E-M和single-use分别解释，不把它当CPU v8-A。
- 对象是compile-only证据；ARM数值/库链接/FPSCR/RTOS上下文/WCET/实板部署仍未测试，没有因compile0退出就宣称机器人资格。

[INDEX.json](<INDEX.json>)与[VALIDATION.json](<VALIDATION.json>)列出raw logs、对象/头/源哈希及旧封存物不变复核。
