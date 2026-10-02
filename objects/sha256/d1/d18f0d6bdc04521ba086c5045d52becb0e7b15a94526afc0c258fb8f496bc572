"""Local command/telemetry protocol; no network or training-process controls."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import tempfile
import time


def atomic_json(path, value):
    """Return False on a locked destination; never leave a partial JSON packet."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, allow_nan=False)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', suffix='.partial', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(payload)
        for _ in range(20):
            try:
                os.replace(name, path)
                return True
            except PermissionError:
                time.sleep(.002)
        return False
    finally:
        if os.path.exists(name):
            os.unlink(name)


def read_json(path):
    try:
        value = json.loads(Path(path).read_text(encoding='utf-8'))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def initial_command(session_id):
    return dict(session_id=session_id, vx=0., wz=0., height=.34,
                paused=False, reset_id=0, quit=False, updated_epoch=time.time())


class CommandReader:
    """Reject foreign/malformed packets; stale panel commands ramp to zero."""
    def __init__(self, path, session_id, timeout=2., yaw_limit=5.):
        self.path, self.session_id, self.timeout = Path(path), session_id, timeout
        if not math.isfinite(yaw_limit) or not 0 <= yaw_limit <= 4 * math.pi:
            raise ValueError('Invalid playback yaw limit')
        self.yaw_limit = yaw_limit
        self.last = initial_command(session_id)
        self.last['updated_epoch'] = 0.  # accept a fresh packet written before worker startup

    def read(self, now=None):
        now = time.time() if now is None else now
        packet = read_json(self.path)
        try:
            if packet.get('session_id') != self.session_id:
                raise ValueError('foreign session')
            for key in ('vx', 'wz', 'height', 'updated_epoch'):
                if isinstance(packet[key], bool) or not math.isfinite(float(packet[key])):
                    raise ValueError('non-finite command')
            if any(type(packet[key]) is not bool for key in ('paused', 'quit')):
                raise ValueError('invalid flag')
            if type(packet['reset_id']) is not int or packet['reset_id'] < self.last['reset_id']:
                raise ValueError('invalid reset generation')
            if packet['updated_epoch'] > now + 5 or packet['updated_epoch'] < self.last['updated_epoch']:
                raise ValueError('out-of-order timestamp')
            self.last = dict(packet, vx=max(-1.5, min(1.5, float(packet['vx']))),
                             wz=max(-self.yaw_limit, min(self.yaw_limit, float(packet['wz']))),
                             height=max(.178, min(.34, float(packet['height']))))
        except (KeyError, TypeError, ValueError):
            pass
        result = self.last.copy()
        result['stale'] = now - result['updated_epoch'] > self.timeout
        if result['stale']:
            result['vx'] = result['wz'] = 0.
        return result


def slew(current, target, dt, acceleration=.6):
    return current + max(-acceleration * dt, min(acceleration * dt, target - current))


class SessionLock:
    """One operator panel per checkout; released by the OS on process death."""
    def __init__(self, path):
        self.stream = Path(path).open('a+b')
        if self.stream.tell() == 0:
            self.stream.write(b'1')
            self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            raise RuntimeError('驾驶控制窗已在运行，请使用现有窗口。') from None

    def close(self):
        self.stream.close()
