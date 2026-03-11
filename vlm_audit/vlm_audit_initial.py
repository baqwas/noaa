"""
================================================================================
🌱 MODULE        : vlm_audit_initial.py
🚀 DESCRIPTION   : Qwen3 Native Loader with Integrated Cloud Auditing.
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 1.3.0
📅 UPDATED       : 2026-03-10
================================================================================
"""

import os
import sys
import argparse
import traceback
import gc
from pathlib import Path
from PIL import Image

# --- 🛠️ DYNAMIC PATH RESOLUTION ---
project_root = "/home/reza/PycharmProjects/noaa"
# Add current directory to path to find spatial_auditor.py
if project_root not in sys.path:
    sys.path.insert(0, project_root)

utilities_path = os.path.join(project_root, "utilities")
if utilities_path not in sys.path:
    sys.path.insert(0, utilities_path)

try:
    from core_service import get_config, TerminalColor
    from spatial_auditor import audit_cloud_cover
except ImportError as e:
    print(f"🚨 ERR_PATH_001: Missing local modules. {e}")
    sys.exit(1)

# --- 🛠️ DEPENDENCY CHECK & CLASS DISCOVERY ---
try:
    import torch
    import transformers

    # Attempt to load the native Qwen3 class if available in your build
    if hasattr(transformers, "Qwen3VLForConditionalGeneration"):
        from transformers import Qwen3VLForConditionalGeneration as QwenLoader

        print("✅ ML Stack Verified: Native Qwen3 Loader detected.")
    else:
        # Fallback to AutoModel if the specific class isn't in the namespace yet
        from transformers import AutoModelForVision2Seq as QwenLoader

        print("⚠️  Warning: Native Qwen3 class not found. Using AutoModel fallback.")
except ImportError:
    print(f"🚨 ERR_DEP_001: Missing transformers/torch.")
    sys.exit(1)

TC = TerminalColor()


def run_inference(image_path, model_id, prompt):
    print(f"{TC.OKBLUE}🤖 Initializing Native Engine: {model_id}{TC.ENDC}")

    try:
        # Load Processor and Model
        from transformers import AutoProcessor
        processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

        # Load with strict native class to avoid the "UNEXPECTED" key errors
        model = QwenLoader.from_pretrained(
            model_id,
            device_map="cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            torch_dtype=torch.float32
        )

        # 896px Memory Gate
        with Image.open(image_path) as raw_img:
            raw_img.thumbnail((896, 896), Image.Resampling.LANCZOS)
            image = raw_img.convert("RGB")

        messages = [{"role": "user", "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": prompt},
        ]}]

        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[image], padding=True, return_tensors="pt").to("cpu")

        del image
        gc.collect()

        print(f"{TC.OKCYAN}🧠 Processing Tensors...{TC.ENDC}")
        with torch.no_grad():
            generated_ids = model.generate(**inputs, max_new_tokens=256)

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

    parser = argparse.ArgumentParser()
    parser.add_argument("--loc", type=str)
    args = parser.parse_args()

    # resolve image path logic here...
    img_path = "/home/reza/Videos/satellite/terran/images/collin/MODIS_Terra_CorrectedReflectance_TrueColor/images/collin_MODIS_Terra_CorrectedReflectance_TrueColor_20260306.jpg"

    # --- ☁️ SPATIAL QUALITY GATE ---
    # Audit image before firing up the heavy VLM
    is_usable, cloud_pct = audit_cloud_cover(img_path, threshold_percent=50.0)

    if not is_usable:
        print(f"{TC.WARNING}🛑 AUDIT REJECTED: Cloud cover ({cloud_pct:.2f}%) is too high for VLM analysis.{TC.ENDC}")
        return

    model_id = "Qwen/Qwen3-VL-2B-Instruct"
    prompt = "Describe the ground features clearly visible in this satellite view."

    print(f"{TC.HEADER}{TC.BOLD}🛰️  VLM AUDIT START: {Path(img_path).name}{TC.ENDC}")
    result = run_inference(img_path, model_id, prompt)
    print(f"\n{TC.OKGREEN}📝 ANALYSIS RESULT:{TC.ENDC}\n{result}")


if __name__ == "__main__":
    main()
