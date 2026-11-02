"""Pure stdlib arithmetic vectors mirroring READ SPR source; no source execution,
firmware build, device I/O, simulation, training or third-party imports.
Python uses float64: representative exact fractions here are not a full float32
ABI/rounding equivalence proof. These ranges are SPR J8009, NOT target bindings.
"""
from pathlib import Path
import hashlib, json, math, traceback
ROOT = Path(__file__).resolve().parent


def encode_torque(torque):
    # CAN_receive.c:175-195,211-222: clipping, truncation, zero Kp/Kd, last 12 bits.
    bounded = min(54.0, max(-54.0, torque))
    raw = int((bounded + 54.0) / 108.0 * 4095.0)
    return raw, bytes([0, 0, 0, 0, 0, 0, raw >> 8, raw & 255])


def decode(raw, lo, hi, bits):
    return raw * (hi - lo) / ((1 << bits) - 1) + lo


def feedback(data):
    # CAN_receive.c:60-109; deliberately no hardware/transport interpretation.
    p = (data[1] << 8) | data[2]
    v = (data[3] << 4) | (data[4] >> 4)
    t = ((data[4] & 15) << 8) | data[5]
    return {"status": (data[0] >> 4) & 15,
            "position_rad": decode(p, -3.14, 3.14, 16),
            "speed_rad_s": decode(v, -45.0, 45.0, 12),
            "torque_nm": decode(t, -54.0, 54.0, 12)}


def main():
    checks, vectors = [], []
    for torque, expected in [(-108, 0), (-54, 0), (-27, 1023),
                             (0, 2047), (27, 3071), (54, 4095), (108, 4095)]:
        raw, frame = encode_torque(torque)
        assert raw == expected
        assert len(frame) == 8 and frame[:6] == b"\x00" * 6
        assert frame[6] < 16
        vectors.append({"input_nm": torque, "encoded_uint12": raw,
                        "payload_hex": frame.hex(" "),
                        "decoded_nm": decode(raw, -54, 54, 12)})
        checks.append("torque_" + str(torque))
    for label, data in [("minimum", bytes([0x11, 0, 0, 0, 0, 0, 0, 0])),
                        ("maximum", bytes([0x11, 255, 255, 255, 255, 255, 0, 0])),
                        ("near_zero", bytes([0x11, 127, 255, 127, 247, 255, 0, 0]))]:
        result = feedback(data)
        assert result["status"] == 1
        vectors.append({"feedback_case": label, "payload_hex": data.hex(" "), "decoded": result})
        checks.append("feedback_" + label)
    assert feedback(bytes([0x11, 255, 255, 255, 255, 255, 0, 0]))["torque_nm"] == 54
    checks.append("feedback_full_scale")
    zero_quantization = decode(2047, -54, 54, 12)
    assert -0.014 < zero_quantization < -0.013
    checks.append("symmetric_12bit_zero_quantization")
    # Mirror defects without executing the source; expected/observed both saved.
    hi, lo = 0x12, 0x34
    spr_power_u16 = (hi >> 8) | lo
    correct_u16 = (hi << 8) | lo
    assert spr_power_u16 == 0x34 and correct_u16 == 0x1234
    checks.append("power_high_byte_shift_defect")
    gear_observed, gear_real = 268 // 17, 268 / 17
    assert gear_observed == 15 and gear_real > 15.76
    checks.append("integer_division_gear_defect")
    inverse_max_length = 0.21 * (0.1138 + 0.135) / 0.1138
    c = 0.5 / 0.21 * 0.1138
    acos_argument_at_macro_max = (0.1138**2 + c*c - 0.135**2) / (2 * 0.1138 * c)
    assert inverse_max_length < 0.46 and acos_argument_at_macro_max > 1
    checks.append("ik_050m_outside_domain")
    result = {"mode": "ARITHMETIC_ONLY_NOT_FIRMWARE", "checks_passed": len(checks),
              "checks_failed": 0, "checks": checks, "vectors": vectors,
              "observations": {"power_u16_source": spr_power_u16,
                "power_u16_expected_if_big_endian": correct_u16,
                "source_268_div_17_C_integer": gear_observed,
                "real_268_div_17": gear_real,
                "factor_relative_error": gear_observed / gear_real - 1,
                "ik_max_reachable_m_from_source_constants": inverse_max_length,
                "ik_acos_argument_at_header_max_050m": acos_argument_at_macro_max},
              "source_citations": [
                "reference_selected/chassis/chassis/application/CAN_receive.c#L175-L222",
                "reference_selected/chassis/chassis/application/CAN_receive.c#L60-L109",
                "reference_selected/chassis/chassis/application/CAN_receive.c#L123-L130",
                "reference_selected/chassis/chassis/Task/chassis_task.c#L655-L656",
                "reference_selected/chassis/chassis/algorithm/leg_position.c#L138-L150",
                "reference_selected/chassis/chassis/application/chassis_behaviour.h#L16-L19"]}
    result["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (ROOT / "codec_vectors_spr.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"mode": result["mode"], "checks_passed": len(checks), "checks_failed": 0,
                      "observations": result["observations"]}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        text = traceback.format_exc()
        (ROOT / "codec_vectors_error.txt").write_text(text, encoding="utf-8")
        raise
