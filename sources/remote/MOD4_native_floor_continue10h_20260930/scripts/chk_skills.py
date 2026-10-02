import os, sys
sys.path.insert(0, r"train/rmvehicle/src")
from rmvehicle.mdp import skills
print("P_JUMP =", skills.P_JUMP, " RISE_M =", skills.RISE_M)