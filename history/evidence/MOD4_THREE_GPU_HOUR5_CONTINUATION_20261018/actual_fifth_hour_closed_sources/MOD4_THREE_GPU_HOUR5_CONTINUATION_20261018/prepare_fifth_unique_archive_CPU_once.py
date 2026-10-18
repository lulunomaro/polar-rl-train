from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;F=B.parent/'MOD4_THREE_GPU_HOUR4_CONTINUATION_20261018'
s=(F/'archive_fourth_hour_three_closed_sources_unique_once.py').read_text('utf-8')
s=s.replace("U=W/'MOD4_THREE_GPU_HOUR3_CONTINUATION_20261018'","U=W/'MOD4_THREE_GPU_HOUR4_CONTINUATION_20261018'")
s=s.replace("BASE='ce0a2b4cb0b3a3d7c3938f733b123f0cd3ffa90b'","BASE='f1c8b881064f30cf75ef91744692c224888532b2'")
s=s.replace('three-gpu-fourth-hour-closed-source-continuation','three-gpu-fifth-hour-closed-source-continuation')
s=s.replace("TITLE='Continue all three experts from complete third-hour checkpoints'","TITLE='Continue all three experts from complete fourth-hour checkpoints'")
s=s.replace("/actual_fourth_hour_closed_sources", "/actual_fifth_hour_closed_sources") if False else s
s=s.replace("B.name/'actual_fourth_hour_closed_sources'","B.name/'actual_fifth_hour_closed_sources'")
s=s.replace("U.name/'actual_third_hour_closed_sources'","U.name/'actual_fourth_hour_closed_sources'")
s=s.replace('FOURTH_HOUR_CLOSED_SOURCES','FIFTH_HOUR_CLOSED_SOURCES')
s=s.replace('len(tags)==1381','len(tags)==1383').replace('all1381oldtags','all1383oldtags').replace('len(rawgit(\'tag\',\'--list\').splitlines())==1382','len(rawgit(\'tag\',\'--list\').splitlines())==1384').replace('total_tags1382=True','total_tags1384=True')
s=s.replace('The third three-GPU hour fully closed.','The fourth three-GPU hour fully closed.').replace('The fourth original expert hour continues','The fifth original expert hour continues').replace('Thirdhourall3fullmodelCPU','Fourthhourall3fullmodelCPU')
ast.parse(s)
with (B/'archive_fifth_hour_three_closed_sources_unique_once.py').open('x',encoding='utf-8') as f:f.write(s)
print('Fifth stage archive prepared; actual HEAD guard f1c8b881, all1383 old tags preserved')
