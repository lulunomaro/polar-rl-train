# 单侧界语法探针的范围说明

`probe_mujoco_one_sided_limit_once.py` 已且仅执行一次：MuJoCo3.14支持hinge `limited=true range="finite inf"`，上界保持正无穷。小型XML未显式设置compiler角单位，因此默认degree，输入−.7828277184955518被读为−.01366292116362269rad；这份原receipt保留，不当MOD4v2实际弧度边界验证、不重跑该once。

真实MOD4v2从已明确compiler `angle="radian"` 的31体source生成，父级将直接compile完整新模型并逐joint对单一SI spec核对。能力探针只说明语法可用；不是P0机械/动力学/PhysX或实物认证。
