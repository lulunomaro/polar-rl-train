"""Small ONNX runtime wrapper shared by the viewer and robustness runner."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort


class OnnxPolicy:
    def __init__(self, path: str | Path):
        self.path = Path(path).resolve()
        self.session = ort.InferenceSession(str(self.path), providers=["CPUExecutionProvider"])
        inp = self.session.get_inputs()[0]
        out = self.session.get_outputs()[0]
        self.input_name = inp.name
        self.output_name = out.name
        self.input_width = int(inp.shape[-1])
        self.output_width = int(out.shape[-1])
        expected_names = {
            35: ("observation", "action"),
            175: ("obs_history", "actions"),
        }
        if self.input_width not in expected_names:
            raise ValueError(f"unexpected ONNX shapes: {inp.shape}, {out.shape}")
        if (self.input_name, self.output_name) != expected_names[self.input_width]:
            raise ValueError(f"unexpected ONNX names: {inp.name!r}, {out.name!r}")
        if self.output_width != 6:
            raise ValueError(f"unexpected ONNX shapes: {inp.shape}, {out.shape}")

    def __call__(self, observation: np.ndarray) -> np.ndarray:
        x = np.asarray(observation, dtype=np.float32).reshape(-1, self.input_width)
        y = self.session.run([self.output_name], {self.input_name: x})[0]
        action = np.asarray(y[0], dtype=np.float64)
        if action.shape != (6,) or not np.isfinite(action).all():
            raise FloatingPointError('ONNX action must contain six finite values')
        return action
