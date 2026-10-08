# MOD4 本地 MuJoCo 试驾

双击 `START_WASD.bat`。本包固定使用下载时4090实际trainer自己完整保存的 `model_30900`，不是目录最高编号猜测，也不是预检权重。它来自S2 E0 D5第二块，尚未正式行为审查。

点击驾驶面板或MuJoCo窗口后，按住W/S前后走、A/D左右转，松手停车。空格/X停车、R复位、F切换起点、P暂停；1/2/3分别选平地、绿色小起伏路、蓝色缓坡。鼠标拖动观察，滚轮缩放。初始速度0.6m/s，面板可调0.1–1.5m/s。窗口失去焦点时归零，关闭任一窗口退出本次试玩。

绿色起伏路高度0–2.5cm；蓝色缓坡高度0–8cm。初始平地区面朝绿色路入口，可直走过去。模型保留31个机器人body、6个闭链和4个mimic约束、8个自由导轮；从本次训练冻结import_contract恢复质量、惯量、关节限位、armature、被动阻尼及名义气弹簧参数。六动作/35维观察/PD/力矩速度限制与当前部署合同一致，无航向或扶正辅助。策略只使用actor，不输入critic特权信息。

本地MuJoCo用0.5ms Newton物理步和100Hz策略；不是远端2.5ms PhysX TGS的等价重现。试玩采用名义无噪声、无反馈和动作延迟条件，没有开启随机DR。策略本身来自D1–D5训练。平地和小起伏短程smoke见 `SMOKE_REVIEW.json`，不是正式Isaac技能毕业/实车认证。原USD和MJCF项目均未覆盖，远端训练和3060评测未暂停。

权重/来源校验见 `DOWNLOAD_RECEIPT.json`；导出和场地来源见 `BUILD_RECEIPT.json`。运行数据为 `INTERACTIVE_CURRENT.json`，出错现场为 `INTERACTIVE_ERROR.txt`。
