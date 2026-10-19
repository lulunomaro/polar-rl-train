from pathlib import Path
B=Path(__file__).resolve().parent
s=(B/'launch_requested_latest_player_once.ps1').read_text('utf8')
s=s.replace('REQUESTED_PLAYER_LAUNCH_AND_CURRENT_ACTUAL.json','REQUESTED_PLAYER_V3_LAUNCH_AND_CURRENT_ACTUAL.json')
s=s.replace('reports/PLAYER_','reports/PLAYER_V3_')
s=s.replace('($result | Select-Object','([pscustomobject]$result | Select-Object')
with (B/'launch_status_and_camera_fixed_player_V3_once.ps1').open('x',encoding='utf8') as f:f.write(s)
s=(B/'verify_restarted_player_status_finite_once.py').read_text('utf8')
s=s.replace('REQUESTED_PLAYER_V2_LAUNCH_AND_CURRENT_ACTUAL.json','REQUESTED_PLAYER_V3_LAUNCH_AND_CURRENT_ACTUAL.json')
s=s.replace('FIXED_PLAYER_BOUNDED_STATUS_OBSERVATION_ACTUAL.json','FIXED_PLAYER_V3_BOUNDED_STATUS_OBSERVATION_ACTUAL.json')
s=s.replace('FIXED_PLAYER_OBSERVATION_ORIGINAL_ERROR_','FIXED_PLAYER_V3_OBSERVATION_ORIGINAL_ERROR_')
with (B/'verify_fixed_player_V3_status_finite_once.py').open('x',encoding='utf8') as f:f.write(s)
