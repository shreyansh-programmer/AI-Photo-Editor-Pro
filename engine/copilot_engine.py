import base64
import json
import requests
from PyQt6.QtCore import QThread, pyqtSignal
import cv2

API_KEY = "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"
VISION_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
CHAT_MODEL = "inclusionai/ring-2.6-1t:free"

SYSTEM_PROMPT = """You are Advance Copilot, a professional photography AI assistant built into the 'Advance Editor'. 
Your job is to help beginners edit their photos. You are friendly, concise, and highly knowledgeable about color theory and photography.

You have the magical ability to ACTUALLY change the sliders in the app on behalf of the user.
To change a slider, you MUST output a command on a new line exactly matching this format:
[EXECUTE: tool_name, value]

Available sliders (value ranges from -100 to +100, except where noted):
[EXECUTE: exposure, 15]
[EXECUTE: contrast, 10]
[EXECUTE: saturation, 20]
[EXECUTE: temperature, -10]
[EXECUTE: highlights, -20]
[EXECUTE: shadows, 25]

Available AI effects (no value needed):
[EXECUTE: apply_ai, accent] (Auto Enhance)
[EXECUTE: apply_ai, sky] (Sky Replacement)
[EXECUTE: apply_ai, portrait] (Portrait Enhancement)
[EXECUTE: apply_ai, bg_blur] (Background Blur)

When a user asks you to make an image warmer, brighter, etc., you should respond with a friendly message explaining what you are doing, AND include the [EXECUTE: ...] tags at the end of your message to actually do it!
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
                                {"type": "text", "text": "Analyze this photo as a professional photographer. What are its strengths and weaknesses? What edits (exposure, contrast, color temperature) would make it look better?"},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                            ]
                        }
                    ]
                }
                
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    vision_context = resp.json()['choices'][0]['message']['content']
                else:
                    # Fallback to chat model if vision model fails/unavailable
                    print("Vision model failed, falling back")
            
            # 2. Add System Prompt and Vision Context
            final_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            if vision_context:
                final_messages.append({"role": "system", "content": f"You just looked at the user's photo. Here is your analysis of it:\n{vision_context}\nUse this context to advise the user."})
                
            final_messages.extend(self.messages)
            
            # 3. Call Chat Model with Manual Fallback
            # List of models to try in order of preference
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
                        parts = [p.strip() for p in cmd_str.split(',')]
                        if len(parts) >= 2:
                            commands.append({"tool": parts[0], "value": parts[1]})
                    else:
                        clean_text_lines.append(line)
                        
                self.finished.emit('\n'.join(clean_text_lines).strip(), commands)
            else:
                # All models failed
                self.error.emit(last_err or "All fallback models failed.")
                
        except Exception as e:
            self.error.emit(str(e))
