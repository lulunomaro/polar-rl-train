"""Software retry only:001 stopped BEFORE compile on wrong pack key K.
Preserved original in revisions/verify_component_before_pack_key001.py.
Only K_6x14 lookup fixed; same predeclared tolerances/input recipe/protocol.
Separate002 output and exist_ok=False prevent replacing/rerunning001.
"""
import verify_component as check
if __name__=='__main__':
    check.OUT=check.HERE/'validation002'
    check.main()
