# V9：一次既有TU40结构header诊断，不解属性

- catalog仍只有Office/ACL，无本ELF任务匹配skill；用文件/Python标准库。先完成并只读封存V8，再执行本父scope。仅新V9写入，0 ARM/compile/ASM/fromelf/version/probe/link/PHY/oldQA/Git/agent/root-goal。
- 输入严格为V8现有TU40物件58720B/SHA8e01341b4c39ce543c2c114a1bddcba11371731ec87bcb4865f6285263a0e1a0、V7 sealed reader源码（仅hash/AST读取常量不import）、V8小stop/FACTS/receipt与父scope。38个已认可物件一律不读。
- 本次对象payload只open/read一次；先以producer pin比该唯一owned snapshot SHA，再解52B ELF header与40B section header table。header诊断后再算同一owned snapshot SHA并核文件size/mtime；明确不是第二次独立file-side hash。小source/metadata文件做实际before/after SHA。JSON准确分列这些证据强度，避免为了post-hash暗中重复object读取。
- 记录class/data/type/machine/size、e_shnum/e_shoff/e_shentsize/e_shstrndx/table_end。区分e_shnum=0或e_shstrndx=0xffff的extended encoding与普通正数；如需extended，只读section0的header字段，不猜值。
- 只有已验证table范围完全落在58720B内才遍历headers，循环上限由文件长度/40推导（不创建新属性parser）；逐header核非NOBITS payload边界，核shstr index/type，定位SHT_SYMTAB/DYNSYM的header计数/entrysize整除、SHT_ARM_ATTRIBUTES的header size。只解释这些header；整个物件仅作为opaque snapshot取数/hash，绝不遍历或解释symbol entries、string table内容、attribute/code/data payload。
- 先独占写最小HEADER_DIAG_01.json（含实际计数/边界/读次数），再<=20行报告和capacity proposal。最小可提案section cap以该实际有效table的count为准，不取无限上限；symbol/attribute payload仍未解释，其他caps与semantic gates全保。
- 旧V8仍39 compile successes/38 scope认可/TU40容量停、122C+ASM1未启动。任何读/结构错误保持最小JSON中的真实错误，不修旧reader、不补物件、不重编或转fromelf。新的reader study和后缀compile都待父另批；全部V9在PH10 cutoff外。
