"""Original E3 recovery labels. No SDK, action, phase or reward mutation."""
PROFILE_LABELS=tuple('fall_recipe'+str(r).zfill(2)+'_'+phase for r in range(12) for phase in ('request_first3s','post_request'))+('recipe12_normal_zero_command_baseline',)
def upcoming_request(torch,recipe,age_before):
 assert bool(((recipe>=0)&(recipe<=12)).all()) and bool((age_before>=0).all())
 return (recipe!=12)&(age_before<300)
def profile_key(torch,recipe,age_before):
 request=upcoming_request(torch,recipe,age_before)
 return torch.where(recipe==12,torch.full_like(recipe,24),recipe*2+(~request).long())
def new_original_credit(torch,before,terminal,episode_before,episode_terminal):
 assert bool((episode_before==episode_terminal).all()),'Use original terminal-before-reset endpoints only'
 return terminal&~before
