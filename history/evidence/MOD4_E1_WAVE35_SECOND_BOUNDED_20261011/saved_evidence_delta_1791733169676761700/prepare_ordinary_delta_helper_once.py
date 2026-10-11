from second_io import *
p=D/'archive_second_saved_delta_actual.py';assert not p.exists()
s=(PRIOR/'archive_wave_saved_delta_actual.py').read_text(encoding='utf8').replace('from wave_io import *','from second_io import *').replace('Append Wave1800s actual startup and saved Git receipt evidence','Append Wave35 second-block actual saved evidence and Git receipts')
compile(s,p.name,'exec');p.write_text(s,encoding='utf8')
print(json.dumps(dict(prepared=str(p),only_ordinary_supplement_no_new_trial=True)))
