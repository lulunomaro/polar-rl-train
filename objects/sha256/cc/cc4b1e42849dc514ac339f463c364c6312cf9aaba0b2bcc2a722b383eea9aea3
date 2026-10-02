import io
p = r"D:/claude2/fangzhen/robot/vehicle.spec.yaml"
t = io.open(p, encoding="utf-8").read()
t = t.replace("range: [-6.2832, 6.2832], effort: 24.0, class: leg",
              "range: [-6.2832, 6.2832], effort: 24.0, class: leg")
t = t.replace("range: [-2.2, 2.2], effort: 13.0, class: leg",
              "range: [-2.2, 2.2], effort: 30.0, class: leg")
t = t.replace("effort: 6.0, class: wheel", "effort: 10.0, class: wheel")
t = t.replace("""#   * knee effort = 0.54 x hip effort, because the similar-linkage ratio
#     0.1134/0.21 = 0.54 multiplies crank speed and divides knee torque""",
"""#   * torque budget: the similar-linkage ratio is 0.1134/0.21 = 0.54, and the doc
#     (2.1.1 item 4) wants the *motor* to swing through as large an angle as possible,
#     i.e. the hip-mounted crank turns 1/0.54 = 1.85x the knee angle -> the linkage
#     multiplies knee torque.  A DM8009P16 gives ~24 Nm, so the knee is budgeted at
#     30 Nm (not the full 44 Nm, on purpose).  Static check: holding the folded CAD
#     pose needs m*g/2 * d(knee->wheel) = 98 N * 0.20 m = 20 Nm at each knee, so 13 Nm
#     (a naive "derate") cannot even stand up - that was the bug this note records.
#   * wheel effort 10 Nm matches the wheelbipe deployment limit (+-9.99 Nm).""")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("torque budget corrected")
