"""Python64 -> one resident MinGW32 PE32 sealed ASQP worker, local stdio only.
No ctypes, numpy requirement, implicit warm, restart, physics or actuation.
Only CONVERGED/valid1 is a numerical result; parent cycle deadline is separate.
"""
from pathlib import Path
import json
import math
import numbers
import queue
import re
import struct
import subprocess
import threading
from time import perf_counter_ns

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / 'PROTOCOL_SCHEMA.json').read_text(encoding='utf-8'))
U64_MAX = (1 << 64) - 1
FATAL_SOLVER = set(SCHEMA['fatal_solver_statuses'])
INTEGER = re.compile(r'(?:0|[1-9][0-9]*)\Z')
DECIMAL = re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z')

class ProtocolError(RuntimeError):
    pass

class HostQPFault(RuntimeError):
    def __init__(self, reply):
        self.reply = reply
        super().__init__(f"resident QP fatal status={reply['status']} sequence={reply['sequence']}; worker stopped")

def integer(value, bits=64):
    if isinstance(value, bool) or not isinstance(value, numbers.Integral):
        raise ValueError(f'uint{bits} requires an integer, not bool/float')
    value = int(value)
    if not 0 <= value < (1 << bits):
        raise ValueError(f'uint{bits} range')
    return value

def f32(value):
    if isinstance(value, (str, bytes, bool)):
        raise ValueError('numeric finite float32 required')
    try:
        value = float(value)
        if not math.isfinite(value):
            raise ValueError('finite float32 required')
        value = struct.unpack('<f', struct.pack('<f', value))[0]
    except (OverflowError, TypeError, struct.error) as error:
        raise ValueError('finite float32 range') from error
    if not math.isfinite(value):
        raise ValueError('finite float32 required')
    return value

def _uint_token(token, bits=64):
    if len(token) > 20 or not INTEGER.fullmatch(token):
        raise ProtocolError('noncanonical unsigned integer')
    try:
        return integer(int(token), bits)
    except ValueError as error:
        raise ProtocolError(str(error)) from error

def _float_token(token):
    if len(token) > 64 or not DECIMAL.fullmatch(token):
        raise ProtocolError('bad finite decimal token')
    try:
        return f32(float(token))
    except ValueError as error:
        raise ProtocolError(str(error)) from error

def _header(line, operation, sequence):
    if not isinstance(line, str) or not line.endswith('\n') or len(line) > SCHEMA['max_frame_bytes']:
        raise ProtocolError('truncated/oversized response line')
    if any(ord(c) > 127 or (ord(c) < 32 and c not in '\r\n\t') for c in line):
        raise ProtocolError('non-ASCII response')
    fields = line.split()
    if len(fields) < 5 or fields[:2] != ['ABQPIO', '1'] or fields[2] not in operation:
        raise ProtocolError('response magic/version/operation')
    if _uint_token(fields[3]) != sequence or _uint_token(fields[4], 32) != len(fields) - 5:
        raise ProtocolError('response sequence/count')
    return fields[2], fields[5:]

def decode_boot(line):
    _, fields = _header(line, {'B'}, 0)
    if len(fields) != 8 or fields[:4] != ['16', '32', '64', '24']:
        raise ProtocolError('worker n/bitness/float model')
    if fields[4:6] != ['QPC', 'RN_NO_FTZ_DAZ']:
        raise ProtocolError('production requires real QPC and RN/no-FTZ/DAZ; test harness is separate')
    if fields[6:] != [SCHEMA['core_sha256'], SCHEMA['header_sha256']]:
        raise ProtocolError('worker sealed-source identity')
    return dict(zip(SCHEMA['boot_fields'], fields))

def decode_reply(line, expected_sequence):
    operation, fields = _header(line, {'R', 'E'}, expected_sequence)
    specs = SCHEMA['reply_fields']
    if len(fields) != len(specs):
        raise ProtocolError('reply payload field count')
    values = {}
    for token, spec in zip(fields, specs):
        values[spec['name']] = _float_token(token) if spec['type'] == 'f32' else _uint_token(token, 32 if spec['type'] == 'u32' else 64)
    code = values['status']
    names = SCHEMA['status_names']
    if code >= len(names) and str(code) not in SCHEMA['protocol_status']:
        raise ProtocolError('unknown status')
    if any(values[k] not in (0, 1) for k in ['valid', 'fatal', 'warm_present', 'clock_failed', 'diagnostic_valid']):
        raise ProtocolError('nonboolean flags')
    if values['request_n'] > 16 or values['result_n'] > 16 or values['last_phase'] > 8 or values['abort_phase'] > 8:
        raise ProtocolError('reply shape/phase')
    if operation == 'E':
        if code < 1000 or values['fatal'] != 1:
            raise ProtocolError('protocol-error header/status')
    elif code >= 1000:
        raise ProtocolError('solver reply with protocol status')
    if values['fatal'] != int(code in FATAL_SOLVER or code >= 1000):
        raise ProtocolError('fatal/status mismatch')
    if values['valid'] != int(code == 0):
        raise ProtocolError('CONVERGED/valid mismatch')
    if values['clock_failed'] and code != 3:
        raise ProtocolError('clock failure accepted as another status')
    z16 = [values.pop('z' + str(i)) for i in range(16)]
    if code != 0:
        if values['result_n'] != 0 or any(z16) or any(values[k] != 0 for k in ['cost', 'kkt_estimate', 'kkt_upper', 'maximum_gradient_roundoff_bound']):
            raise ProtocolError('nonzero accepted payload on failure')
    elif not values['request_n'] or values['result_n'] != values['request_n'] or any(z16[values['result_n']:]):
        raise ProtocolError('converged shape/trailing vector')
    if values['kkt_estimate'] < 0 or values['kkt_upper'] < values['kkt_estimate'] or values['maximum_gradient_roundoff_bound'] < 0:
        raise ProtocolError('invalid accepted KKT interval')
    if values['diagnostic_kkt_estimate'] < 0 or values['diagnostic_kkt_upper'] < values['diagnostic_kkt_estimate']:
        raise ProtocolError('invalid diagnostic KKT interval')
    if not values['diagnostic_valid'] and (values['diagnostic_kkt_estimate'] or values['diagnostic_kkt_upper']):
        raise ProtocolError('invalid diagnostic flag')
    if code == 0 and (not values['diagnostic_valid'] or values['diagnostic_kkt_upper'] != values['kkt_upper']):
        raise ProtocolError('converged diagnostic mismatch')
    if values['last_us'] < values['start_us'] or values['elapsed_us'] != values['last_us'] - values['start_us']:
        raise ProtocolError('clock-stat interval')
    stat_names = ['pivots', 'factorizations', 'factor_cells', 'releases', 'bound_hits', 'gradient_evaluations', 'clock_polls', 'last_phase', 'abort_phase', 'start_us', 'last_us', 'elapsed_us']
    stats = {k: values.pop(k) for k in stat_names}
    values.update(sequence=expected_sequence, status_name=names[code] if code < len(names) else SCHEMA['protocol_status'][str(code)], stats=stats, z=z16[:values['request_n']], z16=z16, solver_accepted=bool(values['valid']), cycle_deadline_checked=False)
    values['valid'] = bool(values['valid'])
    values['fatal'] = bool(values['fatal'])
    return values

def encode_problem(H, f, lo, hi, warm, max_pivots, tolerance, budget_us):
    n = len(H)
    if isinstance(H, (str, bytes)) or not 1 <= n <= 16:
        raise ValueError('H requires n-by-n, 1<=n<=16')
    matrix = []
    for i in range(n):
        if isinstance(H[i], (str, bytes)) or len(H[i]) != n:
            raise ValueError('H exact square shape')
        matrix.extend(f32(H[i][j]) for j in range(n))
    vectors = []
    for vector in [f, lo, hi] + ([] if warm is None else [warm]):
        if isinstance(vector, (str, bytes)) or len(vector) != n:
            raise ValueError('vector exact n shape')
        vectors.append([f32(vector[i]) for i in range(n)])
    cap = integer(max_pivots, 32)
    budget = integer(budget_us)
    tol = f32(tolerance)
    if tol <= 0:
        raise ValueError('positive finite float32 tolerance')
    payload = [str(n), str(cap), format(tol, '.9g'), str(budget), str(int(warm is not None)), str(n*n), str(n)]
    payload.extend(format(x, '.9g') for x in matrix)
    for vector in vectors:
        payload.extend(format(x, '.9g') for x in vector)
    assert len(payload) == 7 + n*n + 3*n + (n if warm is not None else 0)
    return payload, {'n': n, 'max_pivots': cap, 'tolerance': tol, 'budget_us': budget, 'warm_present': int(warm is not None), 'lo': vectors[1], 'hi': vectors[2]}

def _check_pe32(path):
    with path.open('rb') as stream:
        dos = stream.read(64)
        if len(dos) != 64 or dos[:2] != b'MZ':
            raise ProtocolError('worker is not PE32')
        stream.seek(struct.unpack_from('<I', dos, 60)[0])
        header = stream.read(26)
    if len(header) < 26 or header[:4] != b'PE\0\0' or struct.unpack_from('<H', header, 4)[0] != 0x14c or struct.unpack_from('<H', header, 24)[0] != 0x10b:
        raise ProtocolError('worker requires x86 PE32, not ctypes/DLL or PE32+')

class ActiveQPLocal:
    def __init__(self, executable=None, *, timeout_s=5.0, first_sequence=1, stderr_path=None):
        self.timeout = float(timeout_s)
        if not math.isfinite(self.timeout) or self.timeout <= 0:
            raise ValueError('positive finite timeout')
        self._next_sequence = integer(first_sequence)
        if not self._next_sequence:
            raise ValueError('first sequence must be positive')
        path = Path(executable or HERE / 'active_qp_host.exe').resolve()
        _check_pe32(path)
        self.closed = False
        self.sequence = None
        self._lock = threading.Lock()
        self._responses = queue.Queue()
        self._writes = queue.Queue()
        self._requests = queue.Queue(maxsize=1)
        self._stderr = open(stderr_path, 'a', encoding='utf-8') if stderr_path else None
        try:
            self.process = subprocess.Popen([str(path)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self._stderr if self._stderr else subprocess.DEVNULL, text=True, encoding='ascii', errors='strict', bufsize=1)
        except Exception:
            if self._stderr:
                self._stderr.close()
            raise
        self._reader = threading.Thread(target=self._read_loop, name='ASQP-stdio-reader', daemon=True)
        self._writer = threading.Thread(target=self._write_loop, name='ASQP-stdio-writer', daemon=True)
        self._reader.start()
        self._writer.start()
        try:
            self.banner = decode_boot(self._wait(self._responses, perf_counter_ns() + int(self.timeout*1e9)))
        except Exception:
            self._abort()
            raise

    def _read_loop(self):
        try:
            while not self.closed:
                line = self.process.stdout.readline(SCHEMA['max_frame_bytes'] + 1)
                if not line:
                    self._responses.put(EOFError('worker EOF'))
                    return
                if len(line) > SCHEMA['max_frame_bytes'] or self._responses.qsize() >= 2:
                    raise ProtocolError('oversized/unsolicited worker output')
                self._responses.put(line)
        except Exception as error:
            self._responses.put(error)

    def _write_loop(self):
        while not self.closed:
            try:
                line = self._requests.get(timeout=.1)
            except queue.Empty:
                continue
            try:
                self.process.stdin.write(line)
                self.process.stdin.flush()
                self._writes.put(True)
            except Exception as error:
                self._writes.put(error)
                return

    def _wait(self, channel, end_ns):
        remaining = (end_ns - perf_counter_ns()) / 1e9
        if remaining <= 0:
            raise TimeoutError('worker I/O timeout')
        try:
            item = channel.get(timeout=remaining)
        except queue.Empty as error:
            raise TimeoutError('worker I/O timeout') from error
        if isinstance(item, Exception):
            raise item
        return item

    def _exchange(self, operation, payload, end_ns):
        if self.closed:
            raise ProtocolError('worker closed; no implicit restart')
        if self._next_sequence > U64_MAX:
            raise ProtocolError('uint64 sequence exhausted; no wrap')
        sequence = self._next_sequence
        line = f'ABQPIO 1 {operation} {sequence} {len(payload)}' + (' ' + ' '.join(payload) if payload else '') + '\n'
        if len(line) > SCHEMA['max_frame_bytes']:
            raise ProtocolError('request frame too large')
        self._requests.put_nowait(line)
        self._wait(self._writes, end_ns)
        answer = self._wait(self._responses, end_ns)
        if operation == 'Q':
            _, fields = _header(answer, {'A'}, sequence)
            if fields:
                raise ProtocolError('quit payload')
            result = None
        else:
            result = decode_reply(answer, sequence)
        self.sequence = sequence
        self._next_sequence += 1
        return result

    def solve(self, H, f, lo, hi, warm=None, *, max_pivots=64, tolerance=.002, budget_us=0):
        start = perf_counter_ns()
        with self._lock:
            try:
                payload, expected = encode_problem(H, f, lo, hi, warm, max_pivots, tolerance, budget_us)
                result = self._exchange('S', payload, start + int(self.timeout*1e9))
                if result['request_n'] != expected['n'] or result['warm_present'] != expected['warm_present'] or result['stats']['pivots'] > expected['max_pivots']:
                    raise ProtocolError('reply request/pivot identity')
                if result['valid']:
                    if result['kkt_upper'] > expected['tolerance'] or any(not expected['lo'][i] <= result['z'][i] <= expected['hi'][i] for i in range(expected['n'])):
                        raise ProtocolError('accepted result outside declared box/KKT')
                if result['fatal']:
                    self._abort()
                completed = perf_counter_ns()
                result.update(roundtrip_wall_ns=completed-start, completed_monotonic_ns=completed, clock_source='QPC', worker_pid=self.process.pid, worker_closed=self.closed)
                if result['fatal']:
                    raise HostQPFault(result)
                return result
            except HostQPFault:
                raise
            except Exception:
                self._abort()
                raise

    def _abort(self):
        if self.closed:
            return
        self.closed = True
        if self.process.poll() is None:
            self.process.terminate()
        try:
            self.process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=1.0)
        for thread in [self._writer, self._reader]:
            if thread is not threading.current_thread():
                thread.join(timeout=1.0)
        for stream in [self.process.stdin, self.process.stdout]:
            try:
                stream.close()
            except (OSError, ValueError):
                pass
        if self._stderr:
            self._stderr.close()

    def terminate(self):
        with self._lock:
            self._abort()

    def close(self):
        with self._lock:
            if self.closed:
                return
            try:
                if self._next_sequence <= U64_MAX:
                    self._exchange('Q', [], perf_counter_ns() + int(self.timeout*1e9))
                self.process.stdin.close()
                self.process.wait(timeout=self.timeout)
            except Exception:
                self._abort()
                return
            self.closed = True
            self._writer.join(timeout=1.0)
            self._reader.join(timeout=1.0)
            self.process.stdout.close()
            if self._stderr:
                self._stderr.close()

    def __enter__(self):
        return self

    def __exit__(self, *unused):
        self.close()
