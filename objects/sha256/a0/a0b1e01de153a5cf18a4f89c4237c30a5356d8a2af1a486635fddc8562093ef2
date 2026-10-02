"""Build a private cached USD display, then exec the pose viewer (one child PID)."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys

from playback_ipc import read_json

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--bundle', type=Path, required=True)
parser.add_argument('--command-file', type=Path, required=True)
parser.add_argument('--telemetry', type=Path, required=True)
parser.add_argument('--session-id', required=True)
args = parser.parse_args()
usd = args.bundle / 'src_snapshot/robot.usd'
fingerprint = hashlib.sha256(usd.read_bytes()).hexdigest()
display = ROOT / '.playback/display' / fingerprint
if not (display / 'live_display.xml').is_file() or read_json(display / 'DISPLAY_SOURCE_AUDIT.json').get('source_usd_sha256') != fingerprint:
    subprocess.run([sys.executable, str(ROOT / 'build_usd_display.py'), '--usd', str(usd),
                    '--output-dir', str(display)], check=True)
if not read_json(args.command_file).get('quit'):
    os.execv(sys.executable, [sys.executable, str(ROOT / 'view_live_isaac.py'), '--model', str(display / 'live_display.xml'),
                             '--command-file', str(args.command_file), '--telemetry', str(args.telemetry),
                             '--session-id', args.session_id])
