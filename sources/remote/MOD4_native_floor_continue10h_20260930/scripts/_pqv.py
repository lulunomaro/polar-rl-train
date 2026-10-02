import io
p=r"D:/claude2/fangzhen/docs/PLAN.md"
t=io.open(p,encoding="utf-8").read()
t=t.replace("| M8 | Isaac Lab 路径 | 文档化可复现命令 + 在当前硬件的降级/替代方案 | 🟡 文档完成，未在本机实跑 |",
"""| M8 | Isaac Lab 路径 | 文档化可复现命令 + 在当前硬件的降级/替代方案 | 🟡 文档完成，未在本机实跑 |
| M9 | **对照上交串联腿开源文档校验 link/joint 关系** | B-rep 圆柱面轴线 + 连杆长度 + 电机位置三重核对；4 处修正 | ✅ 见 `docs/SJTU_LEG_COMPARE.md` |""")
t=t.replace("- 2026-09-04 全流程跑通；refs 用 codeload tarball 获取（git clone 被墙）",
"""- 2026-09-04 全流程跑通；refs 用 codeload tarball 获取（git clone 被墙）
- 2026-09-04 用上交《RM2025 串联腿平衡步兵机械开源》PDF 反向校验：
  大腿 0.2100 / 小腿 0.2500 与文档手写图 0.21/0.25 完全一致；髋/膝/轮三处轴向
  |axis·Y| = 1.000（488/181/660 个圆柱面统计）；据此修正髋 360°、整机 20 kg、
  轮组转子质量归属、关节力矩预算（膝 13→30 N·m，13 N·m 连站立都不够）""")
io.open(p,"w",encoding="utf-8",newline="\n").write(t)
print("PLAN updated")
