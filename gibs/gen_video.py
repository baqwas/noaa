#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : gen_video.py
👤 AUTHOR       : Matha Goram
🔖 VERSION      : 1.2.0
📅 LAST UPDATE  : 2026-03-07
⚖️ COPYRIGHT    : (c) 2026 ParkCircus Productions
📜 LICENSE      : MIT License
===============================================================================

📑 VERSION HISTORY:
    - 1.0.0: Initial FFmpeg Orchestrator (Subprocess implementation).
    - 1.1.0: Added H.264/yuv420p standardization for SOHO web-viewers.
    - 1.2.0: Integrated MQTT status publishing via CoreService.

📝 DESCRIPTION:
    Stitches daily satellite JPEGs into MP4 time-lapse sequences.
    Utilizes FFmpeg with H.264 encoding for SOHO compatibility.

🛠️ PREREQUISITES:
    - FFmpeg installed (`sudo apt install ffmpeg`)
===============================================================================
"""

import os
import sys
import subprocess
from pathlib import Path

# --- 🛠️ PRIORITY PATH INJECTION ---
util_path = os.path.expanduser("~/noaa/utilities")
if util_path not in sys.path:
    sys.path.insert(0, util_path)

try:
    from core_service import CoreService, load_safe_config, TerminalColor
except ImportError:
    print(f"❌ [CRITICAL] Could not find core_service.py in: {util_path}")
    sys.exit(1)


class VideoGenerator(CoreService):
    """
    Orchestrates FFmpeg to generate time-lapse videos from satellite subdirs.
    """

    def __init__(self):
        super().__init__("VIDEO_GEN")
        gibs_cfg = self.config.get("gibs", {})
        self.instr_root = Path(gibs_cfg.get("instrument_root"))
        self.video_out = self.instr_root / "time_lapses"
        self.video_out.mkdir(parents=True, exist_ok=True)

        # Load the config
        self.full_config = load_safe_config(str(cfg_file))
        gibs_cfg = self.full_config.get("gibs", {})

        # Define the new log path
        log_base = Path(gibs_cfg.get("log_dir", "/tmp"))
        log_base.mkdir(parents=True, exist_ok=True)
        log_file = log_base / "satellite_health.log"

    def generate_timelapse(self, subdir_name: str, output_filename: str):
        """
        Gathers all JPEGs in a subdir and encodes them into a video.
        """
        source_dir = self.instr_root / subdir_name
        final_video = self.video_out / f"{output_filename}.mp4"

        if not source_dir.exists():
            self.logger.warning(f"Source directory {source_dir} does not exist.")
            return

        # FFmpeg command: 2 frames per second, glob patterns for input
        # Using libx264 for universal compatibility
        cmd = [
            "ffmpeg", "-y",  # Overwrite output
            "-framerate", "2",  # Speed of the time-lapse
            "-pattern_type", "glob",
            "-i", f"{source_dir}/*.jpg",  # Input sequence
            "-c:v", "libx264",  # Video codec
            "-pix_fmt", "yuv420p",  # Standard pixel format for players
            "-crf", "23",  # Constant Rate Factor (High Quality)
            str(final_video)
        ]

        self.logger.info(f"{self.clr.BOLD}🎞️  Generating: {output_filename}.mp4{self.clr.ENDC}")

        try:
            # We use subprocess.run to capture errors
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info(f"{self.clr.OKGREEN}✅ Success: {final_video}{self.clr.ENDC}")
                self.mqtt_publish(f"beulta/video/{subdir_name}/status", "CREATED")
            else:
                self.logger.error(f"FFmpeg failed: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Execution error: {e}")

    def run_suite(self):
        """Processes the primary visualization subdirs."""
        targets = [
            ("true_color", "BeUlta_TrueColor_Weekly"),
            ("night_lights", "BeUlta_NightLights_Weekly"),
            ("precipitation", "BeUlta_Precip_Weekly")
        ]

        for subdir, label in targets:
            self.generate_timelapse(subdir, label)


if __name__ == "__main__":
    print(f"{TerminalColor.BOLD}🚀 BeUlta Video Generation Suite{TerminalColor.ENDC}")
    print("-" * 60)
    gen = VideoGenerator()
    gen.run_suite()
