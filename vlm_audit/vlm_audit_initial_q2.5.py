"""
================================================================================
🌱 MODULE        : vlm_audit_initial.py
🚀 DESCRIPTION   : Memory-Harden VLM Engine - Conditional Downscaling Edition.
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 1.1.8
📅 UPDATED       : 2026-03-10
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
================================================================================

[Summary]
Executes high-fidelity inference for Qwen2.5-VL. Version 1.1.8 implements
conditional image resizing: if the source image is already below 896px,
it bypasses the resampling logic to conserve CPU/RAM.

[Workflow Pipeline Description]
1. Dependency Validation: Verifies presence of torch and transformers.
2. Pointer Resolution: Identifies the latest granule for the target county.
3. Resolution Check: Compares image dimensions against memory safety gate (896px).
4. Model Hydration: Loads weights into RAM with low_cpu_mem_usage=True.
5. Tensor Processing: Encodes image/text via Qwen2_5_VLProcessor.
================================================================================
"""

import os
import sys
import argparse
import traceback
import gc
from pathlib import Path
from PIL import Image

# --- 🛠️ DEPENDENCY CHECK ---
try:
    import torch
    from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor

    print("✅ ML Stack Verified: Qwen2.5-VL Specialized Loader active.")
except ImportError as e:
    print(f"🚨 ERR_DEP_001: Missing ML dependencies.")
    sys.exit(1)

# --- 🛠️ DYNAMIC PATH RESOLUTION ---
project_root = "/home/reza/PycharmProjects/noaa"
utilities_path = os.path.join(project_root, "utilities")
if utilities_path not in sys.path:
    sys.path.insert(0, utilities_path)

try:
    from core_service import get_config, TerminalColor
except ImportError:
    print("🚨 ERR_PATH_001: core_service.py not found.")
    sys.exit(1)

TC = TerminalColor()


def find_latest_image(location):
    """The 'Pointer Method' - Automatically finds the latest JPG for a county."""
    config = get_config()
    terran_cfg = config.get('terran', {})
    base_dir = Path(terran_cfg.get('images_dir', '/home/reza/Videos/satellite/terran/images'))
    layer = "MODIS_Terra_CorrectedReflectance_TrueColor"
    target_path = base_dir / location / layer / "images"
    if not target_path.exists(): return None
    files = sorted(target_path.glob("*.jpg"), key=os.path.getmtime, reverse=True)
    return files[0] if files else None


def run_inference(image_path, model_id, prompt):
    """Loads model dynamically and runs CPU-based inference with memory gates."""
    print(f"{TC.OKBLUE}🤖 Initializing Engine: {model_id}{TC.ENDC}")
    print(f"{TC.WARNING}⏳ CPU mode active. Note: Heavy processing initiated...{TC.ENDC}")

    try:
        # 1. Load Processor
        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True, use_fast=False)

        # 2. Image Handling with Memory Gate (896px)
        limit = 896
        with Image.open(image_path) as raw_img:
            width, height = raw_img.size

            if width > limit or height > limit:
                print(f"{TC.WARNING}📉 Resolution ({width}x{height}) exceeds safety limit. Downscaling...{TC.ENDC}")
                raw_img.thumbnail((limit, limit), Image.Resampling.LANCZOS)
                image = raw_img.convert("RGB")
            else:
                print(f"{TC.OKGREEN}📏 Resolution ({width}x{height}) is safe. Bypassing resize.{TC.ENDC}")
                image = raw_img.convert("RGB")

        # 3. Model Hydration
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_id,
            device_map="cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            dtype=torch.float32
        )

        # 4. Prepare inputs
        messages = [{"role": "user", "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": prompt},
        ]}]

        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[image], padding=True, return_tensors="pt").to("cpu")

        # 5. Clear Memory before Crunching
        del image
        gc.collect()

        print(f"{TC.OKCYAN}🧠 Processing Tensors (Memory Guard Active)...{TC.ENDC}")

        with torch.no_grad():
            generated_ids = model.generate(**inputs, max_new_tokens=128)

        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]

        return processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]

    except Exception:
        return f"🚨 INFERENCE_ERROR:\n{traceback.format_exc()}"


def main():
    config = get_config()
    terran_cfg = config.get('terran', {})

    parser = argparse.ArgumentParser(description="BeUlta VLM Inference Engine")
    parser.add_argument("--loc", type=str, help="County pointer")
    parser.add_argument("--image", type=str, help="Manual image path")
    args = parser.parse_args()

    img_path = args.image if args.image else find_latest_image(args.loc) if args.loc else None
    if not img_path:
        print(f"{TC.WARNING}💡 Usage: --loc [county]{TC.ENDC}")
        return

    model_id = terran_cfg.get('model_id', "Qwen/Qwen2.5-VL-3B-Instruct")
    prompt = terran_cfg.get('default_prompt', "Describe the land use in this image.")

    print(f"{TC.HEADER}{TC.BOLD}🛰️  VLM AUDIT START: {Path(img_path).name}{TC.ENDC}")
    result = run_inference(img_path, model_id, prompt)

    print(f"\n{TC.OKGREEN}📝 ANALYSIS RESULT:{TC.ENDC}")
    print("-" * 60)
    print(result)
    print("-" * 60)


if __name__ == "__main__":
    main()
