import io
F=r"D:\claude2\fangzhen\scripts\export_sim2sim_cc.py"
src=io.open(F,encoding="utf-8").read()
anchor = "# ------------------------------------------------------------------ 2. MJCF edits"
assert src.count(anchor)==1
new = ('# ------------------------------------------------------------------ 2. MJCF edits\n'
       '# Solver regime.  The task was trained with mjlab SimulationCfg(timestep=0.002,\n'
       '# iterations=10, ls_iterations=10, impratio=50, cone="elliptic") while the MJCF ships\n'
       '# iterations=100 / ls_iterations=50 / impratio=1 / pyramidal.  With six <connect>\n'
       '# equalities the closed chain is enforced *softly* during training and *stiffly* in the\n'
       '# deployment, which is a materially different plant - the deployed policy balances but\n'
       '# refuses to execute the jump.  Replicate the training regime here.\n'
       'import os as _os\n'
       'SOLVE_TRAIN = _os.environ.get("RM_DEPLOY_TRAIN_SOLVER", "1") == "1"\n'
       'if SOLVE_TRAIN:\n'
       '    xml = re.sub(r\'<option ([^>]*?)/>\',\n'
       '                 r\'<option \\1 iterations="10" ls_iterations="10" impratio="50" \'\n'
       '                 r\'cone="elliptic"/>\', xml, count=1)\n'
       '    xml = re.sub(r\' iterations="100" ls_iterations="50"\', \'\', xml, count=1)\n'
       '    print("deployment solver -> training regime (iter 10, ls 10, impratio 50, elliptic)")\n'
       '\n')
io.open(F,"w",encoding="utf-8").write(src.replace(anchor,new))
print("export patched")