"""One fresh resource explanation of the current A5 wait; no locks or actor/SDK access."""
from pathlib import Path
D=Path(__file__).resolve().parent;s=(D/'inspect_two_gpus_once.py').read_text(encoding='utf8');a="out=D/'RESOURCE_72_TWO_GPU_SNAPSHOT.json'";assert s.count(a)==1;s=s.replace(a,"out=D/'RESOURCE_ADMISSION5_WAIT_SNAPSHOT.json'");exec(compile(s,str(Path(__file__)),'exec'),{'__name__':'__main__','__file__':str(Path(__file__))})
