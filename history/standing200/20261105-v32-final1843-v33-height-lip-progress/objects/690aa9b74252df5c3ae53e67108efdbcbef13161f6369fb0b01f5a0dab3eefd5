# V32 final1843实际复盘与V33定向修复

V32完整保存并安全退出，run MOD4_STANDING200_SUPPORTED_V32_1793822795305806500，final1843/new134PPO/25728本窗physics。9491221B SHA b12097283cde938ca4dedd97899c0d54fe71ec659f0a6959a167264a5b23a8c4。原OWNER_EXIT1793826888.5454502/errornull/allownwaited/costsettled/leasesreleased。closed唯一回传26files与V18已有轨迹render/video已完成，0NN/0新physics。当前模型view_image看四例八side/top、400Hzsupport、hiptargetactual。

独立80仍strict0/whole0/bothtop0/maxwheel-topforce0。0terminated/80timeout，全部499controls9.98s，不能称满500controls10s；closure/mimic/numerical/rollpitch0，contactreset均disabled。actual400Hz319360active记录/39920activecontrols。初始前20msall80无support。

阶段进展：80/80在约1-2s接近x=.8台沿，实际upperedge接触中位8.5275s；80有某次body-top力，73有某次chassis-top力，但连续support中位仅.03875s（max1.0375s），不是全部稳定挂台。四例到沿后停留，轮仍地面，无抬轮上台。落地1s后rootz中位.348678m，全部峰值<=.370091m，0达到.39。finalx中位.717869m。实际yaw多数较小；yaw对齐轮距约.43759-.44057在容差内，所以轮距负分0正常；前后错轮中位.05962m。右hiptarget100%+.5，左.8442%，actual多低于target，不归为唯一失败原因。

奖励诊断：V32原蹭沿每episode平均+4.1183，站高/height约+7.6329/+6.4831，idle-3.2617但hang只有-.026；连续support_ticks因实际接触闪断经常复位。该证据支持定向消除停在台沿获取持续正分的问题。

V33仅新小overlay，完整源V32final1843接续；增强USD/PD_DC/fullD0D7/CAD/2.5msTGS32/4/closure.01/mimic.01/targetcrank[-1.2,.9]hip[-.5,.5]/rawGaussian/wheelpath/原PPO保持。保持独立站高正奖励无前进门控；新增高度短缺平方负分；上沿发现每episode一次；supportcredit按累计50controls而非闪断复位；台沿静止计时跨接触空隙保留；最多100ms最近真实topcontact连续性供奖励，不改变400Hz验收；支撑后新抬轮高度增量正分。底盘导轮contactreset无条件关闭/无undesiredcost、yaw/轮距/错轮保留。

10项本地CPU/源转换/合成边界与保存80轨迹39920端点回算通过，0PT/SDK/新physics，不是V33行为证明。旧停沿轨迹回算中edge均分约.0075、hang-18.3979、高度短缺-14.6818；只说明新记分降低停沿收益，不能证明新policy已学会。

07:05freshLOCAL：E3交接controller39096/parent22492，solecollector13600/parent39096（本地published新训练worker1639602/GPU16828）；只本地metadata，没开第二SSH。SCUT33四卡/launch/FIRST均unused，PLAN/FROZEN尚未生成。释放后dispatch.py gpu唯一实查四卡，prepare.py一次冻结并选实际兼容空闲72卡，再原canonicalNone/privateGPU/finite准入和真实restore/FIRST。其它主机不能绕原账本。17Adam预期每组36860/common44232须实际restore验收，LR不能用旧snapshot替代。

每窗fullsave安全close后立即独立80/400Hz/bodyposes和当前模型原生审图，无阶段进展不盲续同失败小时；允许底盘导轮支撑但最终仍双轮整footprint实际台顶稳.5s/vxyvz<=.03/rp10deg/yaw.2/no return/unsupported<=.10s。V32 closed/eval/render/native和旧once禁止重放。

本阶段为V33新独立record_experiment唯一trial；V32旧trial与全部历史false/tags/peels不改，后续ordinarysupplement。PT/NPZ/USD/media仅publishedpathbytesSHA，不为Git开模或验phys。保持同chat/automation，健康等待静默。
