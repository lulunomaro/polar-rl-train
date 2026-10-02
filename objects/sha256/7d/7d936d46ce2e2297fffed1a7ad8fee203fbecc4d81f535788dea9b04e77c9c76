"""Protocol failure modes and independent USD-pose rendering contract."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import mujoco
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playback_ipc import CommandReader, SessionLock, atomic_json, initial_command, read_json, slew
from play_onnx_panel import load_runtime
from view_live_isaac import body_mapping, update_pose
from control_panel import Control
from types import SimpleNamespace
from unittest.mock import Mock


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'command.json'
        self.reader = CommandReader(self.path, 'test')
        self.packet = initial_command('test')
        self.now = self.packet['updated_epoch'] + .01

    def test_command_pause_reset_quit_and_stale_stop(self):
        self.packet.update(vx=.6, paused=True, reset_id=2)
        atomic_json(self.path, self.packet)
        self.assertEqual(self.reader.read(self.now)['reset_id'], 2)
        self.assertTrue(self.reader.read(self.now)['paused'])
        stale = self.reader.read(self.now + 3)
        self.assertEqual(stale['vx'], 0)
        self.assertEqual(stale['reset_id'], 2)  # do not spuriously reset on panel death
        self.assertTrue(stale['paused'])
        self.packet.update(quit=True, updated_epoch=self.now + 4)
        atomic_json(self.path, self.packet)
        self.assertTrue(self.reader.read(self.now + 4)['quit'])

    def test_foreign_partial_and_nonfinite_packets_cannot_drive(self):
        for change in ({'session_id': 'other'}, {'vx': 'NaN'}, {'paused': 'false'}):
            self.path.write_text(json.dumps(dict(self.packet, vx=1., **change)) if 'vx' not in change
                                 else json.dumps(dict(self.packet, **change)), encoding='utf8')
            self.assertEqual(self.reader.read(self.now)['vx'], 0)
        self.path.write_text('{"vx":', encoding='utf8')
        self.assertEqual(self.reader.read(self.now + 3)['vx'], 0)

    def test_atomic_publish_recovers_from_windows_reader_lock(self):
        import os
        replace = os.replace
        calls = 0
        def locked_once(source, destination):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise PermissionError('reader holds destination')
            return replace(source, destination)
        with patch('playback_ipc.os.replace', side_effect=locked_once):
            self.assertTrue(atomic_json(self.path, self.packet))
        self.assertEqual(read_json(self.path)['session_id'], 'test')
        self.assertEqual(list(self.path.parent.glob('*.partial')), [])

    def test_session_lock_and_acceleration(self):
        lock = SessionLock(self.path)
        try:
            with self.assertRaises(RuntimeError):
                SessionLock(self.path)
        finally:
            lock.close()
        lock = SessionLock(self.path)
        lock.close()
        value = 0.
        for _ in range(100):
            value = slew(value, 1.5, .01)
        self.assertAlmostEqual(value, .6)
        self.assertAlmostEqual(slew(.01, 0, .1), 0)

    def test_yaw_cap_and_stale_yaw_stop(self):
        reader = CommandReader(self.path, 'test', yaw_limit=4.)
        for requested, expected in ((12.566, 4.), (-12.566, -4.), (2., 2.)):
            atomic_json(self.path, dict(self.packet, wz=requested))
            self.assertEqual(reader.read(self.now)['wz'], expected)
        self.assertEqual(reader.read(self.now + 3)['wz'], 0.)
        reader = CommandReader(self.path, 'test', yaw_limit=0.)
        self.assertEqual(reader.read(self.now)['wz'], 0.)
        for invalid in (-1., float('nan'), float('inf'), 13.):
            with self.assertRaises(ValueError):
                CommandReader(self.path, 'test', yaw_limit=invalid)

    def test_runtime_rejects_wrong_or_nonfinite_fields(self):
        for value in ({'unknown_gain': 1}, {'leg_kp': 'NaN'}, {'policy_hz': 0}, {'diff_min': 2, 'diff_max': 1}):
            self.path.write_text(json.dumps(value), encoding='utf8')
            with self.assertRaises(ValueError):
                load_runtime(self.path)
        self.assertEqual(load_runtime(None).yaw_assist_gain, 0)


class PoseTests(unittest.TestCase):
    def test_body_names_quaternions_and_exact_world_positions(self):
        model = mujoco.MjModel.from_xml_string('<mujoco><worldbody><body name="chassis" mocap="true">'
                                              '<geom type="box" size=".1 .1 .1"/></body></worldbody></mujoco>')
        data = mujoco.MjData(model)
        mapping = body_mapping(model)
        packet = dict(sim_time_s=2., body_world_poses={'chassis': [1, 2, .25, 1, 0, 0, 0]})
        self.assertEqual(update_pose(model, data, mapping, packet), 0)
        np.testing.assert_allclose(data.xpos[1], [1, 2, .25])
        with self.assertRaises(ValueError):
            update_pose(model, data, mapping, dict(packet, body_world_poses={'wrong': [1, 2, 3, 1, 0, 0, 0]}))
        with self.assertRaises(ValueError):
            update_pose(model, data, mapping, dict(packet, body_world_poses={'chassis': [1, 2, 3, 0, 0, 0, 0]}))
        np.testing.assert_allclose(data.xpos[1], [1, 2, .25])  # reject atomically


class DriverModeTests(unittest.TestCase):
    def test_straight_and_spin_modes_release_without_mixing(self):
        panel = Control.__new__(Control)
        panel.args = SimpleNamespace(engine='isaac-live', yaw_limit=4.)
        panel.command = initial_command('test')
        panel.speed = Mock(get=Mock(return_value=.6))
        panel.spin_speed = Mock(get=Mock(return_value=2.))
        panel.pause_button = panel.motion = Mock()
        panel.persist = Mock()
        panel.held, panel.releases = {'w'}, {}
        panel.spin(1)
        self.assertEqual((panel.command['vx'], panel.command['wz']), (0., 2.))
        panel.release('w')  # releasing the previous mode must not stop spin
        self.assertEqual(panel.command['wz'], 2.)
        panel.held = {'a'}
        panel.drive(-1)
        self.assertEqual((panel.command['vx'], panel.command['wz']), (-.6, 0.))
        panel.release('a')
        self.assertEqual(panel.command['vx'], -.6)
        panel.stop()
        self.assertEqual((panel.command['vx'], panel.command['wz']), (0., 0.))


if __name__ == '__main__':
    unittest.main()
