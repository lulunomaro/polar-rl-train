from pathlib import Path
J=Path(__file__).resolve().parent;B=J.parent/'H1_STEP270_REWARD_PATH_V1_20261022';s=(B/'same_authorized_session_compressed_transport_v141.py').read_text('utf8');needle='    assert target.name in {';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        '+repr('resume_missing_Fudan_reference_assets_raw_transport_and_CPU_v2_unused_once.py')+',',1)
with (B/'same_authorized_session_compressed_transport_v142.py').open('x',encoding='utf8') as f:f.write(s)
print('Prepared142 exact missing-only reference entry')
