"""Interactive, grounded inspection of the MOD4v4 MJCF using its original coordinates."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import mujoco as mj
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import kinematics

TITLE = 'MOD4v4 · MuJoCo 关节查看 · 导轮贴地'
SIDES = ('left', 'right')
SIDE_ZH = {'left': '左', 'right': '右'}
HIP = {s: (s + '_front1_joint', s + '_rear1_joint') for s in SIDES}
HIP_SIDE = {j: (s, i) for s in SIDES for i, j in enumerate(HIP[s])}
TOUCH = 1e-8  # 10 nm below geometric tangency so MuJoCo emits an actual contact.


class GroundedPose:
    def __init__(self):
        self.model = m = mj.MjModel.from_xml_path(str(ROOT / 'mjcf' / 'scene.xml'))
        self.data = mj.MjData(m)
        self.addr = {m.joint(i).name: int(m.jnt_qposadr[i]) for i in range(m.njnt)}
        self.upper_guards = []
        for i in range(m.ntendon):
            if not m.tendon(i).name.startswith('gimbal_'):
                continue
            start = int(m.tendon_adr[i])
            end = start + int(m.tendon_num[i])
            weights = {m.joint(int(m.wrap_objid[k])).name: float(m.wrap_prm[k]) for k in range(start, end)}
            self.upper_guards.append((m.tendon_range[i].copy(), weights))
        self.fold_followers = {}
        for i in range(m.neq):
            if m.eq_type[i] != mj.mjtEq.mjEQ_JOINT or m.eq_obj2id[i] < 0:
                continue
            ref = m.joint(int(m.eq_obj2id[i])).name
            if ref == 'gimbal_fold_joint':
                name = m.joint(int(m.eq_obj1id[i])).name
                self.fold_followers[name] = float(m.eq_data[i, 1])
        self.stow_key = m.key('guide_ground_stow').id
        self.ground = g = m.geom('ground').id
        self.tires = [m.geom(s + '_tire').id for s in SIDES]
        self.can_touch = [i for i in range(m.ngeom) if i != g and m.geom_bodyid[i] != 0
                          and (m.geom_conaffinity[i] & m.geom_contype[g]
                               or m.geom_contype[i] & m.geom_conaffinity[g])]
        self.bounds = {s: kinematics.mechanical_delta_bounds(s) for s in SIDES}
        self.reset()

    def reset(self):
        mj.mj_resetData(self.model, self.data)
        self.base_pitch = 0.
        self.update_legs(self.hips())
        self.place_on_ground()

    def angle(self, name):
        return float(self.data.qpos[self.addr[name]])

    def hips(self):
        return {s: [self.angle(j) for j in HIP[s]] for s in SIDES}

    def update_legs(self, hips):
        kinematics.set_configuration(self.model, self.data, **hips)

    def interval(self, joint, both, common):
        """Legal absolute slider interval, or None for a continuous coordinate."""
        if joint not in HIP_SIDE:
            i = self.model.joint(joint).id
            if not self.model.jnt_limited[i]:
                return None
            lo, hi = self.model.jnt_range[i]
            for (stop_lo, stop_hi), weights in self.upper_guards:
                if joint not in weights:
                    continue
                other = sum(weight * self.angle(name) for name, weight in weights.items() if name != joint)
                low, high = sorted(((stop_lo - other) / weights[joint], (stop_hi - other) / weights[joint]))
                lo, hi = max(lo, low), min(hi, high)
            return float(lo), float(hi)
        if common:
            return None
        side, index = HIP_SIDE[joint]
        old = self.angle(joint)
        minima, maxima = [], []
        for s in (SIDES if both else (side,)):
            first, last = self.bounds[s]
            diff = self.angle(HIP[s][0]) - self.angle(HIP[s][1])
            lo, hi = (first - diff, last - diff) if index == 0 else (diff - last, diff - first)
            minima.append(lo)
            maxima.append(hi)
        return old + max(minima), old + min(maxima)

    def set_angle(self, joint, angle, both=False, common=False):
        limits = self.interval(joint, both, common)
        if limits is not None:
            angle = max(limits[0], min(limits[1], angle))
        if joint in HIP_SIDE:
            side, index = HIP_SIDE[joint]
            self.base_pitch = 0.  # The pitch is specific to the symmetric guide-ground preset.
            delta = angle - self.angle(joint)
            hips = self.hips()
            for s in (SIDES if both else (side,)):
                for i in ((0, 1) if common else (index,)):
                    hips[s][i] += delta
            self.update_legs(hips)
        else:
            self.data.qpos[self.addr[joint]] = angle
            self.sync_fold_followers()
            mj.mj_forward(self.model, self.data)
        self.place_on_ground()

    def sync_fold_followers(self):
        fold = self.angle('gimbal_fold_joint')
        for name, ratio in self.fold_followers.items():
            self.data.qpos[self.addr[name]] = ratio * fold

    def stow_upper(self):
        mj.mj_resetDataKeyframe(self.model, self.data, self.stow_key)
        root = self.addr['root_joint']
        w, _, y, _ = self.data.qpos[root + 3:root + 7]
        self.base_pitch = 2. * math.atan2(y, w)
        mj.mj_forward(self.model, self.data)
        self.place_on_ground()

    def place_on_ground(self):
        m, d = self.model, self.data
        # Both tire cylinders have the same radius and parallel axles. Level their
        # centers by rolling about chassis X, then let the lowest enabled shape land.
        base = d.xmat[m.body('base_link').id].reshape(3, 3)
        left, right = (d.geom_xpos[i] for i in self.tires)
        _, dy, dz = base.T @ (left - right)
        self.roll = math.atan2(-dz, dy)
        root = self.addr['root_joint']
        cos_roll, sin_roll = math.cos(self.roll / 2), math.sin(self.roll / 2)
        cos_pitch, sin_pitch = math.cos(self.base_pitch / 2), math.sin(self.base_pitch / 2)
        d.qpos[root + 3:root + 7] = (cos_pitch * cos_roll, cos_pitch * sin_roll,
                                    sin_pitch * cos_roll, -sin_pitch * sin_roll)
        mj.mj_forward(m, d)
        gap = min(mj.mj_geomDistance(m, d, self.ground, i, 4., None) for i in self.can_touch)
        d.qpos[root + 2] -= gap + TOUCH
        mj.mj_forward(m, d)
        self.support = set()
        for contact in d.contact:
            a, b = map(int, contact.geom)
            if self.ground in (a, b):
                self.support.add(b if a == self.ground else a)

    def spring_mm(self, side):
        mount = self.data.site(side + '_gas_mount').xpos
        pivot = self.data.xanchor[self.model.joint(side + '_spring1_joint').id]
        return float(np.linalg.norm(mount - pivot) * 1000)


class Viewport(QtWidgets.QWidget):
    def __init__(self, pose):
        super().__init__()
        self.pose = pose
        self.renderer = mj.Renderer(pose.model, height=660, width=880)
        self.options = mj.MjvOption()
        self.options.geomgroup[:] = [1, 0, 1, 0, 0, 0]
        self.options.sitegroup[:] = 0
        self.camera = mj.MjvCamera()
        self.frame = QtGui.QImage()
        self.last_pos = None
        self.setMinimumSize(290, 250)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
        self.repaint_timer = QtCore.QTimer(self, singleShot=True, interval=10)
        self.repaint_timer.timeout.connect(self.draw_scene)
        self.grid = []
        for p in np.linspace(-1.2, 1.2, 25):
            self.grid.extend([([p, -1.2, .00006], [p, 1.2, .00006]),
                              ([-1.2, p, .00006], [1.2, p, .00006])])
        self.reset_camera()

    def reset_camera(self):
        self.camera.type = mj.mjtCamera.mjCAMERA_FREE
        self.camera.lookat[:] = (0, 0, .253)
        self.camera.azimuth = 46
        self.camera.elevation = -12
        self.camera.distance = 1.13
        self.invalidate()

    def invalidate(self):
        if not self.repaint_timer.isActive():
            self.repaint_timer.start()

    def draw_scene(self):
        renderer = self.renderer
        renderer.update_scene(self.pose.data, self.camera, scene_option=self.options)
        scene = renderer.scene
        for a, b in self.grid:
            geom = scene.geoms[scene.ngeom]
            mj.mjv_initGeom(geom, mj.mjtGeom.mjGEOM_LINE, np.zeros(3), np.zeros(3),
                            np.eye(3).ravel(), np.array([.41, .49, .52, .55], dtype=np.float32))
            mj.mjv_connector(geom, mj.mjtGeom.mjGEOM_LINE, 1., a, b)
            scene.ngeom += 1
        pixels = renderer.render()
        h, w, _ = pixels.shape
        self.frame = QtGui.QImage(pixels.data, w, h, pixels.strides[0], QtGui.QImage.Format.Format_RGB888).copy()
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor('#202a30'))
        if not self.frame.isNull():
            size = self.frame.size().scaled(self.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            target = QtCore.QRect(QtCore.QPoint(), size)
            target.moveCenter(self.rect().center())
            painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
            painter.drawImage(target, self.frame)

    def mousePressEvent(self, event):
        self.last_pos = event.position()
        self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        self.last_pos = None
        self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)

    def mouseMoveEvent(self, event):
        if self.last_pos is None:
            return
        movement = (event.position() - self.last_pos) / max(1, self.height())
        self.last_pos = event.position()
        rotate = event.buttons() & QtCore.Qt.MouseButton.LeftButton
        action = mj.mjtMouse.mjMOUSE_ROTATE_V if rotate else mj.mjtMouse.mjMOUSE_MOVE_V
        mj.mjv_moveCamera(self.pose.model, action, movement.x(), movement.y(), self.camera)
        self.invalidate()

    def wheelEvent(self, event):
        self.camera.distance = max(.18, min(3.5, self.camera.distance * .86 ** (event.angleDelta().y() / 120)))
        self.invalidate()
        event.accept()


class AngleRow:
    STEPS = 2000

    def __init__(self, joint, label, layout, editor, *, whole_leg=False):
        self.joint, self.editor = joint, editor
        self.whole_leg = whole_leg
        self.center = editor.pose.angle(joint)
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel(label)
        tooltip = '同侧双髋一起转，前后髋角差保持不变。' if whole_leg else joint
        title.setToolTip(tooltip)
        self.label = QtWidgets.QLabel()
        self.label.setObjectName('angle')
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.label)
        layout.addLayout(header)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setRange(0, self.STEPS)
        self.slider.setAccessibleName(label)
        self.slider.setToolTip(tooltip)
        layout.addWidget(self.slider)
        self.slider.valueChanged.connect(self.edit)
        self.slider.sliderReleased.connect(self.finish)

    def sync(self, recenter=False):
        value = self.editor.pose.angle(self.joint)
        limits = self.editor.pose.interval(self.joint, self.editor.both.isChecked(), self.whole_leg)
        if limits is None:
            if recenter or abs(value - self.center) > math.pi + 1e-9:
                self.center = value
            self.lo, self.hi = self.center - math.pi, self.center + math.pi
        else:
            self.lo, self.hi = limits
        self.label.setText(f'{math.degrees(value):+.1f}°')
        span = self.hi - self.lo
        self.slider.setEnabled(span > 1e-10)
        with QtCore.QSignalBlocker(self.slider):
            self.slider.setValue(round(self.STEPS * (value - self.lo) / span) if span > 1e-10 else 0)

    def edit(self, tick):
        self.editor.edit(self.joint, self.lo + (self.hi - self.lo) * tick / self.STEPS, self.whole_leg)
        if tick in (0, self.STEPS) and not self.slider.isSliderDown():
            self.sync(recenter=True)

    def finish(self):
        if self.slider.value() <= 1 or self.slider.value() >= self.STEPS - 1:
            self.sync(recenter=True)


class Editor(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.pose = GroundedPose()
        self.setWindowTitle(TITLE)
        self.view = Viewport(self.pose)
        self.rows = []
        self.both = QtWidgets.QCheckBox('左右腿同调')
        root = QtWidgets.QHBoxLayout(self)
        root.setContentsMargins(10, 10, 12, 10)
        root.setSpacing(14)
        left = QtWidgets.QVBoxLayout()
        root.addLayout(left, 3)
        left.addWidget(self.view, 1)
        left.addWidget(QtWidgets.QLabel('画面内左键旋转视角　·　右键平移　·　滚轮缩放'))
        self.tabs = QtWidgets.QTabWidget()
        panel = QtWidgets.QVBoxLayout()
        root.addLayout(panel, 1)
        panel.addWidget(self.tabs, 1)
        legs = self.tab('轮腿')
        legs.addWidget(self.both)
        for side in SIDES:
            self.add_row(legs, HIP[side][1], SIDE_ZH[side] + '整腿转角', whole_leg=True)
        leg_note = QtWidgets.QLabel('整腿转角连续。单独拖前髋或后髋会改变连杆开合。')
        leg_note.setWordWrap(True)
        legs.addWidget(leg_note)
        for s, part in ((s, part) for part in ('front1', 'rear1', 'wheel') for s in SIDES):
            label = SIDE_ZH[s] + {'front1': '前髋', 'rear1': '后髋', 'wheel': '主轮'}[part]
            self.add_row(legs, f'{s}_{part}_joint', label)
        legs.addStretch()
        guides = self.tab('导轮')
        for s in SIDES:
            for part, label in [('front', '前支撑导轮'), ('rear', '后支撑导轮'),
                                ('bottom2', '侧前导轮'), ('bottom3', '侧后导轮')]:
                self.add_row(guides, f'{s}_{part}_guide_joint', SIDE_ZH[s] + label)
        guides.addStretch()
        upper = self.tab('上装')
        for part, label in [('yaw', '大 Yaw'), ('fold', '折叠'), ('pitch', 'Pitch')]:
            self.add_row(upper, f'gimbal_{part}_joint', label)
        note = QtWidgets.QLabel('大 Yaw 可连续转动。折叠和 Pitch 的可拖范围会随另一轴的位置变化。')
        note.setWordWrap(True)
        upper.addWidget(note)
        stow = QtWidgets.QPushButton('收纳姿态 · 导轮贴地')
        stow.clicked.connect(self.stow_upper)
        upper.addWidget(stow)
        upper.addStretch()
        self.status = QtWidgets.QLabel()
        self.status.setObjectName('status')
        self.status.setWordWrap(True)
        panel.addWidget(self.status)
        actions = QtWidgets.QHBoxLayout()
        reset = QtWidgets.QPushButton('复位姿态  R')
        reset.setShortcut(QtGui.QKeySequence('R'))
        reset.clicked.connect(self.reset_pose)
        camera = QtWidgets.QPushButton('复位视角')
        camera.clicked.connect(self.view.reset_camera)
        actions.addWidget(reset)
        actions.addWidget(camera)
        panel.addLayout(actions)
        self.both.toggled.connect(self.sync)
        self.sync()

    def tab(self, text):
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(content)
        layout.setSpacing(5)
        scroll.setWidget(content)
        self.tabs.addTab(scroll, text)
        self.tabs.setMinimumWidth(247)
        return layout

    def add_row(self, layout, joint, label, *, whole_leg=False):
        self.rows.append(AngleRow(joint, label, layout, self, whole_leg=whole_leg))

    def edit(self, joint, angle, whole_leg=False):
        self.pose.set_angle(joint, angle, self.both.isChecked(), whole_leg)
        self.sync()

    def stow_upper(self):
        self.pose.stow_upper()
        self.sync()

    def reset_pose(self):
        self.pose.reset()
        for row in self.rows:
            row.center = self.pose.angle(row.joint)
        self.sync()

    def sync(self, *_):
        for row in self.rows:
            row.sync()
        pose = self.pose
        labels = {pose.tires[0]: '左主轮', pose.tires[1]: '右主轮'}
        for side in SIDES:
            for role, label in (('front', '前导轮'), ('rear', '后导轮'),
                                ('side_front', '侧前导轮'), ('side_rear', '侧后导轮')):
                labels[pose.model.geom(f'v4_{side}_{role}_roller').id] = SIDE_ZH[side] + label
        support = '、'.join(labels.get(i, pose.model.geom(i).name) for i in sorted(pose.support)) or '无'
        self.status.setText(f'着地　{support}\n气弹簧　左 {pose.spring_mm("left"):.1f}  /  右 {pose.spring_mm("right"):.1f} mm\n车身侧倾　{math.degrees(pose.roll):+.1f}°')
        self.view.invalidate()

    def closeEvent(self, event):
        self.view.repaint_timer.stop()
        self.view.renderer.close()
        super().closeEvent(event)


STYLE = '''
QWidget {font-family: "Microsoft YaHei UI"; font-size: 13px; color: #253943; background: #f4f6f6;}
QTabWidget::pane {border: 1px solid #c9d5d8; border-radius: 5px;}
QTabBar::tab {padding: 6px 13px; color: #475c65;}
QTabBar::tab:selected {font-weight: bold; color: #065e63; border-bottom: 2px solid #007d81;}
QSlider::groove:horizontal {height: 4px; background: #ced9dc; border-radius: 2px;}
QSlider::sub-page:horizontal {background: #218286; border-radius: 2px;}
QSlider::handle:horizontal {background: #096c72; width: 15px; margin: -6px 0; border-radius: 7px;}
QSlider {min-height: 21px;}
QLabel#angle {font-family: "Consolas"; color: #00656a;}
QLabel#status {background: #e5eeee; padding: 8px; border-radius: 4px;}
QPushButton {padding: 6px; background: #fff; border: 1px solid #afc1c5; border-radius: 4px;}
QPushButton:hover {background: #dbeaea;}
'''


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(STYLE)
    window = Editor()
    screen = app.primaryScreen().availableGeometry()
    window.resize(min(1230, int(screen.width() * .94)), min(790, int(screen.height() * .90)))
    window.move(screen.center() - window.rect().center())
    window.show()
    window.raise_()
    window.activateWindow()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
