import base64
import json
import requests
from PyQt6.QtCore import QThread, pyqtSignal
import cv2
import numpy as np

API_KEY = "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"
VISION_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
CHAT_MODEL = "inclusionai/ring-2.6-1t:free"

# --- NEW: Advanced Tool Definitions for Agentic System ---
# This dictionary defines all available tools (sliders, AI actions, etc.)
# It will be passed to the LLM as part of the system prompt for better tool use.
AVAILABLE_TOOLS = {
    "adjust_exposure": {"description": "Adjusts the overall brightness of the image. Range: -100 to 100.", "type": "slider", "min": -100, "max": 100},
    "adjust_contrast": {"description": "Adjusts the difference between light and dark areas. Range: -100 to 100.", "type": "slider", "min": -100, "max": 100},
    "adjust_saturation": {"description": "Adjusts the intensity of colors. Range: -100 to 100.", "type": "slider", "min": -100, "max": 100},
    "adjust_temperature": {"description": "Adjusts the color temperature (warmth/coolness). Range: -100 to 100.", "type": "slider", "min": -100, "max": 100},
    "adjust_highlights": {"description": "Adjusts the brightness of bright areas. Range: -100 to 100.", "type": "slider", "min": -100, "max": 100},
    "adjust_shadows": {"description": "Adjusts the brightness of dark areas. Range: -100 to 100.", "type": "slider", "min": -100, "max": 100},
    "adjust_whites": {"description": "Adjusts the white clipping point. Range: -100 to 100.", "type": "slider", "min": -100, "max": 100},
    "adjust_blacks": {"description": "Adjusts the black clipping point. Range: -100 to 100.", "type": "slider", "min": -100, "max": 100},
    "adjust_clarity": {"description": "Adjusts midtone local contrast for sharpness. Range: -100 to 100.", "type": "slider", "min": -100, "max": 100},
    "adjust_dehaze": {"description": "Removes or adds haze. Range: 0 to 100.", "type": "slider", "min": 0, "max": 100},
    "adjust_sharpen": {"description": "Sharpens image details. Range: 0 to 100.", "type": "slider", "min": 0, "max": 100},
    "adjust_grain": {"description": "Adds film grain effect. Range: 0 to 100.", "type": "slider", "min": 0, "max": 100},
    "adjust_vignette": {"description": "Adds a dark vignette effect to edges. Range: 0 to 100.", "type": "slider", "min": 0, "max": 100},
    "apply_ai_accent": {"description": "Applies intelligent auto enhancement. No value needed.", "type": "ai_action"},
    "apply_ai_sky": {"description": "Performs sky replacement. No value needed.", "type": "ai_action"},
    "apply_ai_portrait": {"description": "Enhances portraits (skin smoothing, eye enhance). No value needed.", "type": "ai_action"},
    "apply_ai_bg_blur": {"description": "Blurs the background. No value needed.", "type": "ai_action"},
    "apply_ai_hdr": {"description": "Applies HDR merge effect. No value needed.", "type": "ai_action"},
    "apply_ai_lens": {"description": "Corrects lens distortions. No value needed.", "type": "ai_action"},
    "apply_ai_style": {"description": "Transfers color style. No value needed.", "type": "ai_action"},
    "apply_ai_wb": {"description": "Performs auto white balance. No value needed.", "type": "ai_action"},
    "generate_mask_skin": {"description": "Generates a mask for skin areas. Returns mask ID.", "type": "mask_action"},
    "generate_mask_sky": {"description": "Generates a mask for sky areas. Returns mask ID.", "type": "mask_action"},
    "apply_adjustment_to_mask": {"description": "Applies an adjustment to a specific masked area. Requires mask ID, tool name, and value.", "type": "masked_adjustment", "parameters": {"mask_id": {"type": "string"}, "tool_name": {"type": "string"}, "value": {"type": "integer"}}},
}

SYSTEM_PROMPT = f"""You are Advance Copilot, a professional photography AI assistant built into the 'Advance Editor'. 
Your job is to help beginners edit their photos. You are friendly, concise, and highly knowledgeable about color theory and photography.

You have the magical ability to ACTUALLY change the sliders and apply AI effects in the app on behalf of the user.
To perform an action, you MUST output a command on a new line exactly matching this format:
[EXECUTE: tool_name, value]

Here are the tools you can use:
{json.dumps(AVAILABLE_TOOLS, indent=2)}

When a user asks you to make an image warmer, brighter, etc., you should respond with a friendly message explaining what you are doing, AND include the [EXECUTE: ...] tags at the end of your message to actually do it!
If you need to perform multiple steps, output multiple [EXECUTE: ...] commands, one per line.
If the user asks for a selective edit (e.g., 'make the sky bluer'), first generate a mask for that object, then apply the adjustment to the mask.
"""

class CopilotWorker(QThread):
    finished = pyqtSignal(str, list) # response_text, executed_commands
    error = pyqtSignal(str)
    
    def __init__(self, messages, image=None):
        super().__init__()
        self.messages = messages
        self.image = image # cv2 image for vision

    def _encode_image(self, img):
        # Resize to max 1024x1024 for API limits
        h, w = img.shape[:2]
        max_dim = 1024
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img = cv2.resize(img, (int(w*scale), int(h*scale)))
            
        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return base64.b64encode(buffer).decode('utf-8')

    def run(self):
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Advance Editor",
            "Content-Type": "application/json"
        }
        
        try:
            # 1. If image is provided, we use the vision model to analyze it first
            vision_context = ""
            if self.image is not None:
                b64_img = self._encode_image(self.image)
                payload = {
                    "model": VISION_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Analyze this photo as a professional photographer. What are its strengths and weaknesses? What edits (exposure, contrast, color temperature, etc.) would make it look better? Consider composition, lighting, color harmony, and subject. Suggest specific tool actions and values if possible."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                            ]
                        }
                    ]
                }
                
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    vision_context = resp.json()['choices'][0]['message']['content']
                else:
                    print(f"Vision model failed ({resp.status_code}), falling back: {resp.text}")
            
            # 2. Add System Prompt and Vision Context
            final_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            if vision_context:
                final_messages.append({"role": "system", "content": f"You just looked at the user's photo. Here is your analysis of it:\n{vision_context}\nUse this context to advise the user and suggest edits."})
                
            final_messages.extend(self.messages)
            
            # 3. Call Chat Model with Manual Fallback
            fallback_models = [
                CHAT_MODEL, 
                "meta-llama/llama-3-8b-instruct:free", 
                "google/gemma-2-9b-it:free",
                "mistralai/mistral-7b-instruct:free"
            ]
            
            response_text = None
            last_err = None
            
            for model_id in fallback_models:
                payload = {
                    "model": model_id,
                    "messages": final_messages,
                    "temperature": 0.7
                }
                
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
                
                if resp.status_code == 200:
                    response_text = resp.json()['choices'][0]['message']['content']
                    break # Success!
                else:
                    last_err = f"API Error {resp.status_code} with {model_id}: {resp.text}"
                    print(f"Fallback warning: {last_err}")
            
            if response_text is not None:
                # Parse commands
                commands = []
                clean_text_lines = []
                for line in response_text.split('\n'):
                    if line.strip().startswith('[EXECUTE:') and line.strip().endswith(']'):
                        cmd_str = line.strip()[9:-1] # remove [EXECUTE: and ]
                        parts = [p.strip() for p in cmd_str.split(',')] # Split by comma
                        
                        tool_name = parts[0]
                        tool_info = AVAILABLE_TOOLS.get(tool_name)
                        
                        if tool_info:
                            if tool_info["type"] == "slider":
                                if len(parts) == 2:
                                    try:
                                        value = int(parts[1])
                                        commands.append({"tool": tool_name, "value": value})
                                    except ValueError:
                                        clean_text_lines.append(f"[Invalid value for {tool_name}: {parts[1]}]")
                                else:
                                    clean_text_lines.append(f"[Missing value for slider tool: {tool_name}]")
                            elif tool_info["type"] == "ai_action":
                                commands.append({"tool": tool_name, "value": None}) # AI actions don't need a value
                            elif tool_info["type"] == "mask_action":
                                commands.append({"tool": tool_name, "value": None}) # Mask actions don't need a value initially
                            elif tool_info["type"] == "masked_adjustment":
                                if len(parts) == 3:
                                    try:
                                        mask_id = parts[1]
                                        adj_tool_name = parts[2]
                                        adj_value = int(parts[3]) # Assuming value is always integer for now
                                        commands.append({"tool": tool_name, "mask_id": mask_id, "adj_tool": adj_tool_name, "value": adj_value})
                                    except ValueError:
                                        clean_text_lines.append(f"[Invalid values for masked adjustment: {parts[1:]}]")
                                else:
                                    clean_text_lines.append(f"[Missing parameters for masked adjustment: {tool_name}]")
                        else:
                            clean_text_lines.append(f"[Unknown tool: {tool_name}]")
                    else:
                        clean_text_lines.append(line)
                        
                self.finished.emit('\n'.join(clean_text_lines).strip(), commands)
            else:
                self.error.emit(last_err or "All fallback models failed.")
                
        except Exception as e:
            self.error.emit(str(e))
