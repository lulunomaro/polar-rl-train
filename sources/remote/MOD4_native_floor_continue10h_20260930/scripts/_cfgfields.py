import dataclasses
from mjlab.utils.spec_config import CollisionCfg
for f in dataclasses.fields(CollisionCfg):
    d = f.default if f.default is not dataclasses.MISSING else "<req>"
    print("  ", f.name, "=", d)
