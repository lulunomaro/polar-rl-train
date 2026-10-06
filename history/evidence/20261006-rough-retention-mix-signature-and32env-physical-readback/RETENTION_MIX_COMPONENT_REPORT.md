# 浅地形旧技能保留修复：独立混合组件实际读回通过，尚未修复PPO

2026-10-06T09:09:51.312285+00:00实际T=/home/egde/rl_candidates/MOD4_ROUGH_RETENTION_MIX_RUNTIME_20261006.phase retention_mixed_component_review_ready。新signature-review父549138/start43286968及孩子549175/start43287034均完成退出，无trainer/active，同canonical锁已释放。当前只是可读取的组件边界，不是地形/旧技能修复完成或预算结束。

新隔离候选按env_id模4固定75%平地旧技能/25%gentle低速地形。原S182源码、F167与P逐字哈希证明保留，新实际188源。原train_mod4_ppo.py仍是旧纯低速rough dispatch，不可把这个复制训练入口当作已部署混合学习执行器。当前任务组件未改变35actor/38critic/6action、PPO、white_v3、原硬件包络、PD/COM/弹簧、终止或奖励公式/权重；恢复原flat loaded_rolling_v1代理只在明确平地pure组启用，地形yaw/vy始终0。

几何为原gentle生成算法/范围/分块与单独声明的有限平地Mesh两面，平地中心X768m、半宽384m、Z0。无隐藏Plane/底层地面回退、无粗糙几何简化；平地与rough区域分离，平地48m/rough2m显式边界截断分列。flat材质声明static/dynamic.9、rough1/multiply，与原各场景配置分别对应；声明配置不冒称已独立读回USD实际材质绑定。实际32env种子20261006生成rough13037624面，加flat2面共13037626面/523collider，实际USD浮点三角面序列与生成/精确分块SHA一致。不同种子生成几何不假称与旧训练run完全相同。

实际32env300控制步3s全部32/32存活，其中24平地、8浅地形；真实taskreset0、truncation0、非有限false、无引擎错误。closure最大0.316363934mm、mimic0.001691455836rad，6001真实.5ms接触回调。ground/高度奖励/actor和critic命令读回误差0，30q完整写回误差0，独立实际resetXY误差1.19209289551e-07m。平地沿用原完整可行pose库，rough复用30q/qd/root及25200足迹采样；不把离散采样说成连续实体无穿透证明。white_v3实际机器人参数初末读回通过。

初态真实自动命令读回后，冻结manual协议覆盖平地站/±1.5直线/左右4π/世界yaw±2及rough交替±.3。八个rough在first-to-last采样2.8s窗口请求方向与净进度符号全部相符，速度范围-0.311955至0.294692m/s。该窗口不是完整3s终点或地形能力毕业；当前没有完整世界圈/长期正反跟踪成熟性或新权重修复效果证明。

最初SDK组件在RewardManager建表时拒绝mixed_rolling的**kwargs签名，尚未进入动态控制步；原error/state/log和188之前freeze完整保留。仅将适配函数显式列出speed_scale=.15/yaw_min=3.5/support_weight=.25，传给原函数相同参数；其余函数AST exact。没有改变奖励值/权重/公式、质量门槛或模型。新的唯一supervise_retention_mix_signature_review_once已执行并完成，原main/path-review/staging/旧入口都不得重复。首次CPU路径读者错误已另行唯一归档，不作为生产模型故障。

来源明确23509 SHA2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a完整actor/critic/optimizer/std/iter KEEP_STD1、CPU68有限；23624地形候选和全部raw继续保留。旧23624六world16/64及高速前进退化不因为组件pass改写，23509旧18份严格world64/64基准保留。遗忘由狭窄任务引起仍是合理假设，不宣称隔离因果。

本轮PPO0、预算交易0、canonical整字节SHA0189f0d870587b8f0012ad569954f7d6277ea7b1f41f4c0be9a77c00262c1193不变，总468000秒130h和五扩展各一次，剩169695.673236370秒约47h8m。下一步补实际混合train adapter/manifest、独立材质读回、完整圈与分段rough进度/命令重采样生命周期、必要新任务128+20k完整PPO与丢弃预检权重，再同canonical安全边界新唯一45min修复接管。当前不热开新增DR、更难地形或新奖励，不称混训已经开始。SCUTv4有限性能诊断与真实任务/模型/闭链/数据/硬件合同继续。

每2h巡检与原Rich本地5s保持。组件review_ready/旧技能修复准备均不删monitor或加时。权重和大raw仅SHA索引，凭据不归档；本轮真实签名修复和实际组件验证唯一trial推送验证，不重复旧trial。
