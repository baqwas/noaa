#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : gen_video.py
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 1.2.1
📅 LAST UPDATE  : 2026-03-10
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
===============================================================================

📑 VERSION HISTORY:
    - 1.0.0: Initial FFmpeg Orchestrator (Subprocess implementation).
    - 1.2.0: Integrated MQTT status publishing via CoreService class.
    - 1.2.1: Handshake 2.4.0 Migration. Updated to functional imports and
             PycharmProjects pathing to resolve [CRITICAL] path errors.

📝 DESCRIPTION:
    Stitches daily satellite JPEGs into MP4 time-lapse sequences using FFmpeg.
    Optimized for H.264/yuv420p for compatibility with SOHO media players.

🛠️ PREREQUISITES:
    - FFmpeg installed (`sudo apt install ffmpeg`)
    - core_service.py v2.4.0 in ~/PycharmProjects/noaa/utilities

[Workflow Pipeline Description]
1. Environment Setup: Injects Pycharm project paths into sys.path.
2. Ingestion: Locates the satellite instrument root via get_config().
3. FFmpeg Processing: Runs a glob-based pattern match for all JPEGs in a subdir.
4. Encoding: Renders to MP4 with a Constant Rate Factor (CRF) of 23.
5. Telemetry: Reports completion status per-layer to MQTT.
===============================================================================
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# --- 🛠️ PRIORITY PATH INJECTION ---
project_root = "/home/reza/PycharmProjects/noaa"
util_path = os.path.join(project_root, "utilities")

if util_path not in sys.path:
    sys.path.insert(0, util_path)

try:
    from core_service import get_config, init_mqtt, TerminalColor
except ImportError:
    print(f"❌ [CRITICAL] ERR_PATH_001: Could not find core_service.py in: {util_path}")
    sys.exit(1)

# --- ⚙️ INITIALIZATION ---
TC = TerminalColor()
config = get_config()


class VideoGenerator:
    def __init__(self):
        self.gibs_cfg = config.get('gibs', {})
        self.instr_root = Path(self.gibs_cfg.get('images_dir', '/home/reza/Videos/satellite/gibs'))
        self.video_out = self.instr_root / "videos"
        self.video_out.mkdir(parents=True, exist_ok=True)

        self.mqtt_client = init_mqtt()
        self.clr = TerminalColor()

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("BeUlta.Video")

    def mqtt_publish(self, topic, payload):
        if self.mqtt_client:
            self.mqtt_client.publish(topic, payload, retain=True)

    def generate_timelapse(self, subdir_name, output_filename):
        """Orchestrates FFmpeg to stitch JPEGs into H.264 MP4."""
        source_dir = self.instr_root / subdir_name / "images"
        final_video = self.video_out / f"{output_filename}.mp4"

        if not source_dir.exists() or not list(source_dir.glob("*.jpg")):
            self.logger.warning(f"⚠️  Skipping {subdir_name}: No source images found.")
            return

        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-framerate", "2",
            "-pattern_type", "glob",
            "-i", f"{source_dir}/*.jpg",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "23",
            str(final_video)
        ]

        self.logger.info(f"{self.clr.BOLD}🎞️  Generating: {output_filename}.mp4{self.clr.ENDC}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"{self.clr.OKGREEN}✅ Video Success: {final_video.name}{self.clr.ENDC}")
                self.mqtt_publish(f"beulta/video/{subdir_name}/status", "CREATED")
            else:
                self.logger.error(f"🚨 FFmpeg Error: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Execution Error: {e}")

    def run_all(self):
        targets = [
            ("viirs_true_color", "BeUlta_TrueColor_Weekly"),
            ("night_lights", "BeUlta_NightLights_Weekly"),
            ("precipitable_water", "BeUlta_Precip_Weekly")
        ]
        for subdir, label in targets:
            self.generate_timelapse(subdir, label)


if __name__ == "__main__":
    vg = VideoGenerator()
    vg.run_all()
