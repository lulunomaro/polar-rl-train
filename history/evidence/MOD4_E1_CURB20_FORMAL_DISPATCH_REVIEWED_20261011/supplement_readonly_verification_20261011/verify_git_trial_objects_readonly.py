"""Read-only remote main, exact annotated tag objects and peeled commits."""
from pathlib import Path
import subprocess,json
REPO=Path(__file__).resolve().parent.parent/'polar-rl-train'
def g(*a):
 p=subprocess.run(['git','-C',str(REPO),*a],capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;return p.stdout.strip()
local={x.split()[2]:(x.split()[0],x.split()[1]) for x in g('for-each-ref','--format=%(objectname) %(objecttype) %(refname)','refs/tags').splitlines()}
remote={x.split()[1]:x.split()[0] for x in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
assert g('rev-parse','HEAD')==remote['refs/heads/main']
expected=['29ffc8098987661f02a93043b97c77a416b13c25','c583da18a2b95ea53d94c5bb47816b537dfd9534','94eeab83ec069802f8bc60742c593c9d8a6ddb06','5c80c9a353276f9d8f9a0dc96e2112cbcb8b71fe','a5965345b34416f7981ded0acdbfc61cdb5774de','76669fb91d68789406f4b13cc2e289d98686d6a8','1926640c87e19d3f4418fb1b4f7ddebf2367d3b7']
verified=[]
for sha in expected:
 keys=[k for k,v in local.items() if v==(sha,'tag')];assert len(keys)==1;key=keys[0]
 assert remote[key]==sha and remote[key+'^{}']==g('rev-parse',key+'^{}');verified.append(key)
assert not g('status','--porcelain')
print(json.dumps(dict(remote_main=remote['refs/heads/main'],annotated_trial_objects_and_peeled_verified=len(verified),two_new_stage_and_five_old_trial_objects_unchanged=True,working_tree_clean=True,push_pending=False)))
