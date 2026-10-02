import os
if os.environ.get('RM_SPIN_STAGE') == 'directional_spin_v1':
    from directional_spin_sdk_v2 import configure, audit
else:
    from spin_commands_preserved import configure, audit
