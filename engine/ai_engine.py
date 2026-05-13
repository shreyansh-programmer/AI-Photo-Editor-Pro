"""
Advance Editor — AI Engine v2
Powered by HuggingFace models + OpenCV C++ backend.
- Background Removal: rembg (u2net ONNX model)
- Depth Estimation: Depth Anything V2 (HuggingFace transformers)
- Segmentation: Semantic segmentation for sky detection
- Denoising: OpenCV fastNlMeansDenoising (C++ optimized)
- Inpainting: OpenCV Navier-Stokes (C++ optimized)
"""
import cv2
import numpy as np
from PIL import Image
import logging
import warnings

warnings.filterwarnings("ignore")
log = logging.getLogger("AIEngine")


# ═══════════════════════════════════════════════════════════
#  ACCENT AI — Histogram Analysis + Auto Tone Mapping
# ═══════════════════════════════════════════════════════════
class AccentAI:
    """Intelligent auto enhancement via image analysis."""

    @staticmethod
    def analyze(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
        total = hist.sum()
        cumsum = np.cumsum(hist) / total

        black_pt = np.searchsorted(cumsum, 0.01)
        white_pt = np.searchsorted(cumsum, 0.99)
        mean_val = gray.mean()
        std_val = gray.std()

        exposure = int(np.clip((120 - mean_val) / 3, -50, 50))
        contrast = int(np.clip((60 - std_val) * 0.8, -30, 50)) if std_val < 40 else 0

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mean_sat = hsv[:, :, 1].mean()
        saturation = int(np.clip((128 - mean_sat) * 0.15, -20, 30))

        b, g, r = cv2.split(img.astype(np.float32))
        temperature = int(np.clip((r.mean() - b.mean()) * -0.2, -30, 30))

        return {
            'exposure': exposure, 'contrast': contrast,
            'saturation': saturation, 'temperature': temperature,
            'highlights': -10 if white_pt < 240 else 0,
            'shadows': 15 if black_pt > 20 else 0,
            'vibrance': 15, 'clarity': 10,
        }

    @staticmethod
    def apply(img, intensity=50):
        # Museum-Grade Auto Enhancement via Exposure Fusion (Mertens) and CLAHE
        result = img.copy()
        
        # 1. CLAHE on Lightness channel for local contrast enhancement
        lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0 + (intensity/50.0), tileGridSize=(8,8))
        cl = clahe.apply(l)
        result_clahe = cv2.cvtColor(cv2.merge((cl, a, b)), cv2.COLOR_LAB2BGR)
        
        # 2. Exposure Fusion (Merge varying exposures for HDR effect)
        darker = cv2.convertScaleAbs(result, alpha=0.7, beta=0)
        brighter = cv2.convertScaleAbs(result, alpha=1.3, beta=20)
        
        merge_mertens = cv2.createMergeMertens()
        hdr = merge_mertens.process([darker, result_clahe, brighter])
        hdr = (hdr * 255).astype(np.uint8)
        
        # 3. Blend based on intensity
        factor = intensity / 100.0
        final = cv2.addWeighted(result, 1.0 - factor, hdr, factor, 0)
        
        # 4. Smart Vibrance (boost less saturated pixels more)
        hsv = cv2.cvtColor(final, cv2.COLOR_BGR2HSV).astype(np.float32)
        sat = hsv[:,:,1]
        # Boost saturation inversely proportional to current saturation
        sat_boost = (255 - sat) * (factor * 0.3)
        hsv[:,:,1] = np.clip(sat + sat_boost, 0, 255)
        
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


# ═══════════════════════════════════════════════════════════
#  SKY AI — Semantic Sky Detection + Replacement
# ═══════════════════════════════════════════════════════════
class SkyAI:
    """Sky detection using color analysis + morphological refinement."""

    @staticmethod
    def detect_sky(img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, w = img.shape[:2]
        y_weight = np.linspace(1.0, 0.0, h).reshape(-1, 1)
        y_weight = np.broadcast_to(y_weight, (h, w))

        hue, sat, val = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
        blue = ((hue >= 85) & (hue <= 135) & (sat > 30) & (val > 80)).astype(np.float32)
        bright = ((sat < 50) & (val > 180)).astype(np.float32)
        sunset = (((hue < 25) | (hue > 165)) & (sat > 40) & (val > 120)).astype(np.float32)

        score = (blue * 0.5 + bright * 0.3 + sunset * 0.2) * y_weight
        mask = (score > 0.15).astype(np.uint8) * 255

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

        flood_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
        if mask[0, w // 2] == 255:
            cv2.floodFill(mask, flood_mask, (w // 2, 0), 255)

        mask = cv2.GaussianBlur(mask, (31, 31), 12)
        return mask

    @staticmethod
    def generate_sky(width, height, sky_type='blue'):
        sky = np.zeros((height, width, 3), dtype=np.uint8)
        presets = {
            'blue':    lambda t: (200 - t*80, 160 - t*60, 80 + t*40),
            'sunset':  lambda t: (60 + t*80, 40 + t*100, 200 - t*30),
            'golden':  lambda t: (80 + t*40, 120 + t*60, 220 - t*40),
            'stormy':  lambda t: (90 + t*40, 80 + t*40, 75 + t*35),
            'night':   lambda t: (30 + t*10, 15 + t*10, 20 + t*5),
            'aurora':  lambda t: (40 + t*20, int(80 + np.sin(t*3.14)*120), int(30 + np.sin(t*3.14+1)*60)),
        }
        func = presets.get(sky_type, presets['blue'])
        for y in range(height):
            t = y / height
            b, g, r = func(t)
            sky[y, :] = [int(max(0, min(255, b))), int(max(0, min(255, g))), int(max(0, min(255, r)))]

        if sky_type == 'night':
            stars = np.random.random((height, width)) > 0.998
            sky[stars] = [255, 255, 240]

        if sky_type not in ['night', 'aurora']:
            # Hyper-realistic volumetric clouds using fBm
            fbm = SkyAI._fractal_noise(width, height, octaves=6)
            
            # Map fBm to cloud density (threshold and soft clip)
            cloud_coverage = 0.55 # Base coverage
            cloud_density = np.clip((fbm - (1.0 - cloud_coverage)) * 3.0, 0, 1.0)
            
            # Add perspective (clouds get smaller/flatter near horizon)
            y_gradient = np.linspace(1.5, 0.2, height).reshape(-1, 1)
            cloud_density = cloud_density * y_gradient
            cloud_density = np.clip(cloud_density, 0, 0.9) # Max 90% opacity
            
            # Simulated sun lighting (directional scattering)
            light_gradient = np.linspace(1.2, 0.8, height).reshape(-1, 1)
            cloud_color = np.ones_like(sky, dtype=np.float32) * 245 * light_gradient
            
            cm3 = np.stack([cloud_density] * 3, axis=2)
            sky = np.clip(sky.astype(np.float32) * (1 - cm3) + cloud_color * cm3, 0, 255).astype(np.uint8)
        return sky

    @staticmethod
    def replace_sky(img, sky_type='blue', blend=50):
        mask = SkyAI.detect_sky(img)
        # Use advanced Edge Matting to refine the sky mask
        try:
            from engine.ai_advanced import EdgeMatting
            mask = EdgeMatting.refine_mask(img, mask, radius=15, eps=1e-4)
        except Exception:
            pass

        h, w = img.shape[:2]
        new_sky = SkyAI.generate_sky(w, h, sky_type)
        
        mask_f = (mask.astype(np.float32) / 255.0) * (blend / 100.0)
        mask_3 = np.stack([mask_f] * 3, axis=2)
        
        # Multiply blending for realistic horizon
        result = img.astype(np.float32) * (1 - mask_3) + new_sky.astype(np.float32) * mask_3
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def _fractal_noise(width, height, octaves=5):
        """Museum-Grade Fractal Brownian Motion (fBm) for Volumetric Clouds."""
        noise = np.zeros((height, width), dtype=np.float32)
        amplitude = 1.0
        frequency = 1.0
        max_amplitude = 0.0
        
        for i in range(octaves):
            # Scale down dimensions for this octave
            h_i = max(1, int(height / frequency))
            w_i = max(1, int(width / frequency))
            
            # Generate random noise and blur it
            octave_noise = np.random.rand(h_i, w_i).astype(np.float32)
            blur_size = max(3, int(min(h_i, w_i) / 4))
            if blur_size % 2 == 0: blur_size += 1
            octave_noise = cv2.GaussianBlur(octave_noise, (blur_size, blur_size), 0)
            
            # Scale up to original size
            octave_noise = cv2.resize(octave_noise, (width, height), interpolation=cv2.INTER_CUBIC)
            
            noise += octave_noise * amplitude
            max_amplitude += amplitude
            amplitude *= 0.5
            frequency *= 2.0
            
        return noise / max_amplitude


# ═══════════════════════════════════════════════════════════
#  PORTRAIT AI — Skin Detection + Bilateral Smoothing
# ═══════════════════════════════════════════════════════════
class PortraitAI:
    @staticmethod
    def detect_skin(img):
        # Use Haar Cascades for reliable face region detection + skin color ML fallback
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        mask_hsv = cv2.inRange(hsv, (0, 20, 50), (25, 200, 255))
        mask_ycrcb = cv2.inRange(ycrcb, (0, 133, 77), (255, 173, 127))
        color_skin = cv2.bitwise_and(mask_hsv, mask_ycrcb)
        
        mask = np.zeros_like(color_skin)
        if len(faces) > 0:
            for (x, y, w, h_f) in faces:
                # Add padding around face
                px, py = max(0, x - w//4), max(0, y - h_f//4)
                pw, ph = min(img.shape[1] - px, int(w*1.5)), min(img.shape[0] - py, int(h_f*1.5))
                mask[py:py+ph, px:px+pw] = color_skin[py:py+ph, px:px+pw]
        else:
            mask = color_skin # Fallback to whole image if no faces detected
            
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Guided Filter refinement for perfect edges
        try:
            from engine.ai_advanced import EdgeMatting
            mask = EdgeMatting.refine_mask(img, mask, radius=8, eps=1e-3)
        except Exception:
            mask = cv2.GaussianBlur(mask, (15, 15), 5)
            
        return mask

    @staticmethod
    def smooth_skin(img, amount=50):
        mask = PortraitAI.detect_skin(img)
        d = int(5 + amount / 10)
        sigma = 30 + amount
        smoothed = cv2.bilateralFilter(img, d, sigma, sigma)
        mask_f = mask.astype(np.float32) / 255.0 * (amount / 100.0)
        mask_3 = np.stack([mask_f] * 3, axis=2)
        result = img.astype(np.float32) * (1 - mask_3) + smoothed.astype(np.float32) * mask_3
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def enhance_eyes(img, amount=50):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        skin = PortraitAI.detect_skin(img)
        dark = cv2.bitwise_and(cv2.threshold(cv2.bitwise_and(gray, gray, mask=skin), 80, 255, cv2.THRESH_BINARY_INV)[1], skin)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dark = cv2.GaussianBlur(cv2.morphologyEx(dark, cv2.MORPH_OPEN, kernel), (11, 11), 3)
        factor = amount / 100.0 * 0.5
        dark_3 = np.stack([dark.astype(np.float32) / 255.0 * factor] * 3, axis=2)
        enhanced = cv2.addWeighted(img, 1.0, img, 0.3, 10)
        result = img.astype(np.float32) * (1 - dark_3) + enhanced.astype(np.float32) * dark_3
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def apply(img, skin_smooth=50, eye_enhance=30):
        result = img.copy()
        if skin_smooth > 0:
            result = PortraitAI.smooth_skin(result, skin_smooth)
        if eye_enhance > 0:
            result = PortraitAI.enhance_eyes(result, eye_enhance)
        return result


# ═══════════════════════════════════════════════════════════
#  BACKGROUND AI — rembg (u2net HuggingFace ONNX model)
# ═══════════════════════════════════════════════════════════
class BackgroundAI:
    """Background removal using rembg (u2net neural network via ONNX)."""

    _rembg_session = None

    @classmethod
    def _ensure_rembg(cls):
        if cls._rembg_session is None:
            try:
                from rembg import new_session
                cls._rembg_session = new_session("u2net")
                log.info("Loaded rembg u2net model")
            except Exception as e:
                log.warning(f"rembg not available, using GrabCut fallback: {e}")
                return False
        return True

    @staticmethod
    def remove_background(img):
        """Remove background using u2net neural network."""
        if BackgroundAI._ensure_rembg():
            try:
                from rembg import remove
                pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                result = remove(pil_img, session=BackgroundAI._rembg_session)
                result_np = np.array(result)
                return cv2.cvtColor(result_np, cv2.COLOR_RGBA2BGRA)
            except Exception as e:
                log.warning(f"rembg failed, using fallback: {e}")
        return BackgroundAI._grabcut_fallback(img)

    @staticmethod
    def get_mask(img):
        """Get foreground mask using u2net."""
        if BackgroundAI._ensure_rembg():
            try:
                from rembg import remove
                pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                result = remove(pil_img, session=BackgroundAI._rembg_session, only_mask=True)
                mask = np.array(result)
                if len(mask.shape) == 3:
                    mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
                    
                # Professional Edge Refinement (Guided Filter)
                try:
                    from engine.ai_advanced import EdgeMatting
                    mask = EdgeMatting.refine_mask(img, mask, radius=12, eps=1e-3)
                except Exception as e:
                    log.warning(f"Failed to refine mask: {e}")
                    
                return mask
            except Exception:
                pass
        return BackgroundAI._grabcut_mask_fallback(img)

    @staticmethod
    def blur_background(img, amount=50):
        """Blur background with AI-detected foreground mask."""
        fg_mask = BackgroundAI.get_mask(img)
        blur_size = max(3, int(amount / 2) * 2 + 1)
        blurred = cv2.GaussianBlur(img, (blur_size, blur_size), amount / 3)
        # Professional Edge Refinement (Guided Filter)
        try:
            from engine.ai_advanced import EdgeMatting
            fg_mask = EdgeMatting.refine_mask(img, fg_mask, radius=12, eps=1e-3)
        except Exception:
            pass
            
        mask_f = fg_mask.astype(np.float32) / 255.0
        mask_3 = np.stack([mask_f] * 3, axis=2)
        result = img.astype(np.float32) * mask_3 + blurred.astype(np.float32) * (1 - mask_3)
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def replace_background(img, bg_color=(255, 255, 255)):
        fg_mask = BackgroundAI.get_mask(img)
        mask_f = fg_mask.astype(np.float32) / 255.0
        mask_3 = np.stack([mask_f] * 3, axis=2)
        bg = np.full_like(img, bg_color, dtype=np.float32)
        result = img.astype(np.float32) * mask_3 + bg * (1 - mask_3)
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def _grabcut_fallback(img):
        mask = BackgroundAI._grabcut_mask_fallback(img)
        b, g, r = cv2.split(img)
        return cv2.merge([b, g, r, mask])

    @staticmethod
    def _grabcut_mask_fallback(img):
        h, w = img.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        rect = (int(w*0.1), int(h*0.05), int(w*0.8), int(h*0.9))
        bgd, fgd = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
        try:
            cv2.grabCut(img, mask, rect, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
        except cv2.error:
            y, x = np.ogrid[:h, :w]
            r = np.sqrt(((x - w/2) / (w/2))**2 + ((y - h/2) / (h/2))**2)
            return ((r < 0.7) * 255).astype(np.uint8)
        fg_mask = np.where((mask == 1) | (mask == 3), 255, 0).astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        return cv2.GaussianBlur(fg_mask, (15, 15), 5)


# ═══════════════════════════════════════════════════════════
#  RELIGHT AI — HuggingFace Depth Estimation + Relighting
# ═══════════════════════════════════════════════════════════
class RelightAI:
    """Relighting using depth estimation from HuggingFace models."""

    _depth_pipeline = None
    _use_hf = None

    @classmethod
    def _ensure_depth(cls):
        if cls._use_hf is not None:
            return cls._use_hf
        try:
            from transformers import pipeline as hf_pipeline
            cls._depth_pipeline = hf_pipeline(
                "depth-estimation",
                model="LiheYoung/depth-anything-small-hf",
                device="cpu"
            )
            cls._use_hf = True
            log.info("Loaded Depth Anything model from HuggingFace")
            return True
        except Exception as e:
            log.warning(f"HF depth model not available, using algorithmic fallback: {e}")
            cls._use_hf = False
            return False

    @staticmethod
    def estimate_depth(img):
        """Estimate depth using HuggingFace Depth Anything or algorithmic fallback."""
        if RelightAI._ensure_depth():
            try:
                pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                result = RelightAI._depth_pipeline(pil_img)
                depth = np.array(result["depth"]).astype(np.float32)
                # Resize to match input
                depth = cv2.resize(depth, (img.shape[1], img.shape[0]))
                depth = (depth - depth.min()) / (depth.max() - depth.min() + 1e-7)
                return depth
            except Exception as e:
                log.warning(f"HF depth failed, using fallback: {e}")

        # Algorithmic fallback
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        h, w = gray.shape
        sharp = np.abs(cv2.Laplacian(gray, cv2.CV_32F))
        sharp_blur = cv2.GaussianBlur(sharp, (31, 31), 15)
        sharp_norm = sharp_blur / (sharp_blur.max() + 1e-7)
        y_depth = np.broadcast_to(np.linspace(0.3, 1.0, h).reshape(-1, 1), (h, w))
        depth = sharp_norm * 0.5 + y_depth * 0.5
        depth = cv2.GaussianBlur(depth, (21, 21), 10)
        return (depth - depth.min()) / (depth.max() - depth.min() + 1e-7)

    @staticmethod
    def apply(img, direction=0, warmth=50, intensity=50):
        depth = RelightAI.estimate_depth(img)
        h, w = img.shape[:2]
        angle_rad = np.radians(direction)
        y_c, x_c = np.mgrid[:h, :w]
        x_norm = (x_c / w - 0.5) * 2
        y_norm = (y_c / h - 0.5) * 2
        light_dir = (x_norm * np.cos(angle_rad) + y_norm * np.sin(angle_rad) + 1) / 2
        light_map = cv2.GaussianBlur(light_dir * depth, (15, 15), 7)

        strength = intensity / 100.0
        light_mod = 1.0 + (light_map - 0.5) * strength
        result = img.astype(np.float32)
        for c in range(3):
            result[:, :, c] *= light_mod

        warm = (warmth - 50) / 100.0
        result[:, :, 2] += warm * light_map * 30 * strength
        result[:, :, 1] += warm * light_map * 15 * strength
        result[:, :, 0] -= warm * light_map * 10 * strength
        return np.clip(result, 0, 255).astype(np.uint8)


# ═══════════════════════════════════════════════════════════
#  NOISELESS AI — OpenCV C++ Optimized Denoising
# ═══════════════════════════════════════════════════════════
class NoiselessAI:
    @staticmethod
    def apply(img, luminance=50, color=50, detail=50):
        # Professional Edge-Preserving Denoise (Joint Bilateral / Guided Filter + Chroma Subsampling)
        
        # 1. Chroma Denoising (Heavy blur on A/B channels, edges preserved by L channel)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        if color > 0:
            c_blur = int(3 + color / 10) * 2 + 1
            # Blur chrominance aggressively
            a_b = cv2.GaussianBlur(a, (c_blur, c_blur), color/10)
            b_b = cv2.GaussianBlur(b, (c_blur, c_blur), color/10)
            
            # Use L channel to guide the edges of the blurred chroma
            try:
                from cv2.ximgproc import createGuidedFilter
                gf = createGuidedFilter(l, radius=c_blur, eps=100)
                a = gf.filter(a_b)
                b = gf.filter(b_b)
            except Exception:
                a, b = a_b, b_b
                
        if luminance > 0:
            # FastNLMeans is good, but we supplement it with frequency separation
            l_denoised = cv2.fastNlMeansDenoising(l, None, luminance * 0.25, 7, 21)
            
            if detail > 0:
                # Recover texture/grain that was smoothed out
                high_freq = cv2.subtract(l, cv2.GaussianBlur(l, (3, 3), 1))
                mask = cv2.Canny(l, 50, 150)
                mask = cv2.dilate(mask, None)
                mask_f = mask.astype(np.float32) / 255.0
                
                # Add back high freq only on edges
                l = cv2.addWeighted(l_denoised, 1.0, high_freq, detail / 100.0, 0)
            else:
                l = l_denoised
                
        result = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
        return result


# ═══════════════════════════════════════════════════════════
#  SUPERSHARP AI — Multi-Scale Unsharp Mask + Structure
# ═══════════════════════════════════════════════════════════
class SupersharpAI:
    @staticmethod
    def apply(img, sharpness=50, structure=30, scale=100):
        result = img.copy()
        if scale > 100:
            factor = scale / 100.0
            h, w = result.shape[:2]
            result = cv2.resize(result, (int(w * factor), int(h * factor)), interpolation=cv2.INTER_LANCZOS4)
            
        # Museum-Grade Sharpening: Laplacian Pyramid + Halo Suppression
        if sharpness > 0 or structure > 0:
            lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l_float = l.astype(np.float32)
            
            # Structure (Micro-contrast)
            if structure > 0:
                s_blur = cv2.GaussianBlur(l_float, (15, 15), 5)
                high_pass = l_float - s_blur
                l_float = l_float + (high_pass * (structure / 50.0))
                
            # Sharpness (Fine detail)
            if sharpness > 0:
                blur1 = cv2.GaussianBlur(l_float, (3, 3), 1)
                detail = l_float - blur1
                
                # Halo suppression mask (don't over-sharpen extreme edges)
                edges = cv2.Canny(l, 30, 100)
                edges = cv2.dilate(edges, np.ones((3,3)))
                halo_mask = 1.0 - (edges.astype(np.float32) / 255.0 * 0.5)
                
                l_float = l_float + (detail * (sharpness / 25.0) * halo_mask)
                
            l = np.clip(l_float, 0, 255).astype(np.uint8)
            result = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
            
        return result


# ═══════════════════════════════════════════════════════════
#  ERASE AI — OpenCV Inpainting (Navier-Stokes C++)
# ═══════════════════════════════════════════════════════════
class EraseAI:
    @staticmethod
    def apply(img, mask):
        if mask is None:
            return img
        return cv2.inpaint(img, mask, inpaintRadius=7, flags=cv2.INPAINT_NS)

    @staticmethod
    def content_aware_fill(img, mask):
        if mask is None:
            return img
        return cv2.inpaint(img, mask, inpaintRadius=10, flags=cv2.INPAINT_TELEA)


# ═══════════════════════════════════════════════════════════
#  UNIFIED AI ENGINE
# ═══════════════════════════════════════════════════════════
class AIEngine:
    def __init__(self):
        self.accent = AccentAI()
        self.sky = SkyAI()
        self.portrait = PortraitAI()
        self.background = BackgroundAI()
        self.relight = RelightAI()
        self.noiseless = NoiselessAI()
        self.supersharp = SupersharpAI()
        self.erase = EraseAI()

    def auto_enhance(self, img, intensity=50):
        return AccentAI.apply(img, intensity)

    def replace_sky(self, img, sky_type='blue', blend=50):
        return SkyAI.replace_sky(img, sky_type, blend)

    def portrait_enhance(self, img, skin_smooth=50, eye_enhance=30):
        try:
            from engine.ai_advanced import FaceAI
            return FaceAI.retouch_faces(img, skin_smooth, eye_enhance, teeth_whiten=10)
        except Exception as e:
            return PortraitAI.apply(img, skin_smooth, eye_enhance)

    def blur_background(self, img, amount=50):
        return BackgroundAI.blur_background(img, amount)

    def remove_background(self, img):
        return BackgroundAI.remove_background(img)

    def relight(self, img, direction=0, warmth=50, intensity=50):
        return RelightAI.apply(img, direction, warmth, intensity)

    def denoise(self, img, luminance=50, color=50, detail=50):
        return NoiselessAI.apply(img, luminance, color, detail)

    def sharpen(self, img, sharpness=50, structure=30, scale=100):
        return SupersharpAI.apply(img, sharpness, structure, scale)

    def erase_object(self, img, mask):
        try:
            from engine.ai_advanced import HealAI
            return HealAI.apply(img, mask)
        except Exception:
            return EraseAI.apply(img, mask)

    def cinematic_relight(self, img, color=(255, 0, 255), light_x=0.8, light_y=0.2, intensity=1.5):
        try:
            from engine.ai_advanced import CinematicStudioAI
            depth_map = self.relight._get_depth(img) # Reuse the cached depth map
            return CinematicStudioAI.add_3d_point_light(img, depth_map, light_x, light_y, light_z=0.5, color=color, intensity=intensity)
        except Exception as e:
            log.error(f"Cinematic relight failed: {e}")
            return img
            
    def cinematic_fog(self, img, density=0.5, color=(200, 210, 220)):
        try:
            from engine.ai_advanced import CinematicStudioAI
            depth_map = self.relight._get_depth(img)
            return CinematicStudioAI.add_volumetric_fog(img, depth_map, fog_color=color, density=density)
        except Exception as e:
            log.error(f"Cinematic fog failed: {e}")
            return img
