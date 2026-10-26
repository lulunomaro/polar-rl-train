from pathlib import Path
J=Path(__file__).resolve().parent;B=J.parent/'H1_STEP270_REWARD_PATH_V1_20261022';s=(B/'same_authorized_session_compressed_transport_v140.py').read_text('utf8');needle='    assert target.name in {';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        '+repr('prepare72_and_capture_pinned_Fudan_jump_reference_CPU_finite_unused_once.py')+',',1)
with (B/'same_authorized_session_compressed_transport_v141.py').open('x',encoding='utf8') as f:f.write(s)
print('Prepared141 exact CPU foreign-reference entry only; no credentials or other transport changes')
