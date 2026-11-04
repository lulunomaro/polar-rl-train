# V16：旧BSP/Stage1首次诊断链接
- 实际LINK调用1，rc=0，输出存在=True；完整stdout/stderr保留。
- 输入163独立obj＋两opaque库在本次firstlink前各核当前SHA一次匹配producer；用途为真实link完整性，非归档重复hash。poststat及小pins前后相同。
- reviewed expanded argv直接传入，仅新output字符串替换；原order/flags/scatter/cwd/defaultRT未改。无VIA执行、重编译、抑制diagnostic、ABI/region覆盖或CCM搬移。
- Flash1MiB/SRAM128KiB来自源项目显式选择，非physicalboard绑定。旧V6/V8历史gate/cap记录保持原状；不是单次cleanbuild。
- 新映像若成功仅基本ELF/LOADsegments/vector元数据观察，文件大小不是ROM/RAM占用；map/runtime/IRQ覆盖/库成员/semihosting/完整ABI/FPSCR/RTOS/WCET/实机需分项核。
- 保留旧机mechanicalcontrol/MF9025接口，MOD4绑定默认UNBOUND；这不是C3＋新startup技能一体化镜像或可刷机资格。映像未启动，库算法未调用，无flash/realIO/PHY/旧QA/Git。
- 提取的link diagnostic行数=0；源日志优先，不自动link重试；全部PH11pending。
