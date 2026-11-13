"""Apply the concrete RL/USB/CAN/INS/Keil integration to the extracted old ZIP.

Only run once. Every old file must match the expected source anchor before edit.
"""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "firmware"
changes = []


def edit(rel, replacements):
    path = FW / rel
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    for before, after in replacements:
        assert text.count(before) == 1, (rel, before, text.count(before))
        text = text.replace(before, after)
    # Preserve original CRLF convention; Path.read_text is intentionally unused.
    output = text.encode("utf-8")
    path.write_bytes(output)
    changes.append(dict(path=rel, original_SHA256=hashlib.sha256(raw).hexdigest(), modified_SHA256=hashlib.sha256(output).hexdigest()))


if __name__ == "__main__":
    assert not (ROOT / "FIRMWARE_PATCHES.json").exists()
    edit("application/robot_param.h", [("#include \"robot_typedef.h\"", "#include \"robot_typedef.h\"\r\n#include \"mod4_options.h\"")])
    edit("application/chassis/chassis_balance.c", [("#if (CHASSIS_TYPE == CHASSIS_BALANCE)", "#if (CHASSIS_TYPE == CHASSIS_BALANCE) && !MOD4_RL_ENABLE")])
    edit("Src/freertos.c", [
        ("osThreadDef(ChassisTask, chassis_task, osPriorityAboveNormal, 0, 512);", "osThreadDef(ChassisTask, chassis_task, osPriorityAboveNormal, 0, 2048);"),
        ("    osThreadDef(USB_Task, usb_task, osPriorityNormal, 0, 128);\r\n    usb_task_handle = osThreadCreate(osThread(USB_Task), NULL);",
         "#if !MOD4_RL_ENABLE\r\n    osThreadDef(USB_Task, usb_task, osPriorityNormal, 0, 128);\r\n    usb_task_handle = osThreadCreate(osThread(USB_Task), NULL);\r\n#endif")])
    edit("Src/usbd_cdc_if.c", [
        ("#include \"usbd_cdc_if.h\"", "#include \"usbd_cdc_if.h\"\r\n#include \"mod4_options.h\"\r\n#include \"mod4_board.h\""),
        ("  /* USER CODE BEGIN 6 */", "  /* USER CODE BEGIN 6 */\r\n#if MOD4_RL_ENABLE\r\n  mod4_board_usb_rx(Buf, *Len);\r\n#endif")])
    edit("application/robot_cmd/CAN_receive.c", [
        ("#include \"CAN_receive.h\"", "#include \"CAN_receive.h\"\r\n#include \"mod4_options.h\"\r\n#include \"mod4_board.h\""),
        ("    HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &rx_header, rx_data);", "    HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &rx_header, rx_data);\r\n#if MOD4_RL_ENABLE\r\n    if (rx_header.IDE == CAN_ID_STD && rx_header.DLC == 8 &&\r\n        mod4_board_can_rx(hcan == &hcan1 ? 1 : 2, (uint16_t)rx_header.StdId, rx_data)) return;\r\n#endif")])
    edit("application/IMU/IMU_task.c", [
        ("#include \"IMU_task.h\"", "#include \"IMU_task.h\"\r\n#include \"mod4_options.h\"\r\n#include \"mod4_board.h\""),
        ("    IMU_DATA.z_accel = INS_accel[INS_ACCEL_Z_ADDRESS_OFFSET];", "    IMU_DATA.z_accel = INS_accel[INS_ACCEL_Z_ADDRESS_OFFSET];\r\n#if MOD4_RL_ENABLE\r\n    mod4_board_imu_updated(HAL_GetTick());\r\n#endif")])
    path = FW / "MDK-ARM/standard_robot.uvprojx"
    raw = path.read_bytes()
    root = ET.fromstring(raw)
    target = root.find("./Targets/Target")
    includes = target.find("./TargetOption/TargetArmAds/Cads/VariousControls/IncludePath")
    includes.text += ";../application/mod4_rl"
    group = ET.SubElement(target.find("Groups"), "Group")
    ET.SubElement(group, "GroupName").text = "MOD4v3 R1 policy + DM3519"
    files = ET.SubElement(group, "Files")
    for name in ("mod4_board.c", "mod4_controller.c", "mod4_runtime.c", "dm_protocol.c", "mod4_wire.c"):
        entry = ET.SubElement(files, "File")
        ET.SubElement(entry, "FileName").text = name
        ET.SubElement(entry, "FileType").text = "1"
        ET.SubElement(entry, "FilePath").text = "..\\application\\mod4_rl\\" + name
    ET.indent(root, space="  ")
    path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))
    changes.append(dict(path=str(path.relative_to(FW)), original_SHA256=hashlib.sha256(raw).hexdigest(), modified_SHA256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (ROOT / "FIRMWARE_PATCHES.json").write_text(json.dumps(changes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"patched_original_files": len(changes), "new_source_group": 5}))
