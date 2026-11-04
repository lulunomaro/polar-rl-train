# V10：仅新有界HOST容量reader study

- 当前catalog仅Office/ACL，无robotics/ELF匹配skill；用文件工具/Python3.14 stdlib，不运行ARM工具。遵守父PARENT_SCOPE.json；所有旧目录只读，PH10 cutoff外。
- 父选择独立新结构预算16×：MAX_OBJECT 65536→1048576，MAX_SECTIONS 256→4096，条件SYMTAB entry cap1024→16384。这不是V9最小304提案的应用，不是ABI容差。
- 新文件从sealed V7 reader仅上述3个常量literal派生；字节inverse及AST inverse必须精确恢复原件。其余常量、每个范围/ULEB/截断/extended/冲突/UNKNOWN/nodefaults/FILE/SECTION/SYMBOL语义零改动。
- 在任何parse前冻结新reader、generator/runner/source/6个新blob大小SHA与期望。每cap一正一负：object长度1048576/1048577，普通section数4096/4097，实际SYMTAB entries（含NULL）16384/16385。六个fixture有完整合法backing headers/payload bounds，后两项显式public SYMBOL scope激活条件symbol路径；每blob仅一次新parse。负边界期望有界ParseError，其他错误皆实际first-stop，不修不重跑。
- 每parse前后先落最小JSON，保已过prefix/失败/未开始；只有6fixture全PASS才一次打开既有TU40物件58720B（V8 producer SHA8e01341b4c39ce543c2c114a1bddcba11371731ec87bcb4865f6285263a0e1a0），调用新reader一次完整scope parse。
- semantic gate复用sealed V8纯gate函数的独立AST definition（不import executor、不执行native）并保持原expected：ELF1/1/1/40，FILE6=13/7=77/9=2/10=6/27=1/28=1/20∈[1,2]；EXEC及public SYMBOL tags18=2或规范UNUSED0、26=1或规范UNUSED0；UNKNOWN/冲突/格式/cap均STOP，无fallback。
- 新完整scope含raw blocks、FILE/SECTION/SYMBOL provenance及每code/type结果。不读取38accepted或main，不复跑V7旧19/64QA，不解释code/data内容。TU40仅一次opaque取数与新metadata parse；source小文件SHA before/after，物件post取同owned snapshot再hash+file size/mtime，不冒充第二次file-side hash。
- 最小parse/gate JSON先于≤30行报告；fixture/实际对象只允许这一次study，任何首错保存原件，不静默修改。ARM/compile/ASM/fromelf/version/probe/link/UV/hooks/IO/flash/oldQA/FK/PHY/Git/agent/root-goal动作全部0；122C+ASM1仍未启动，父再读后另批。
