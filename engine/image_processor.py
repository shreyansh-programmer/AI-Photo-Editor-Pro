"""
Advance Editor - Core Image Processing Engine
All operations use OpenCV (C++ optimized) and NumPy (C/Fortran optimized)
"""
import cv2
import numpy as np
from scipy import ndimage


class ImageProcessor:
    """Core image processing with C++ optimized OpenCV backend."""

    @staticmethod
    def adjust_brightness(img, value):
        """Brightness: shift pixel values. value in [-100, 100]"""
        val = value * 2.55
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] + val, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    @staticmethod
    def adjust_contrast(img, value):
        """Contrast: scale around midpoint. value in [-100, 100]"""
        factor = (259 * (value + 255)) / (255 * (259 - value))
        result = img.astype(np.float32)
        result = np.clip(factor * (result - 128) + 128, 0, 255)
        return result.astype(np.uint8)

    @staticmethod
    def adjust_exposure(img, value):
        """Exposure: multiply by 2^value. value in [-3, 3]"""
        factor = 2.0 ** (value / 50.0)
        result = img.astype(np.float32) * factor
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def adjust_saturation(img, value):
        """Saturation: interpolate gray<->color. value in [-100, 100]"""
        factor = 1.0 + value / 100.0
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    @staticmethod
    def adjust_vibrance(img, value):
        """Vibrance: boost only desaturated colors. value in [-100, 100]"""
        factor = value / 100.0
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        sat = hsv[:, :, 1] / 255.0
        boost = factor * (1.0 - sat)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1.0 + boost), 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    @staticmethod
    def adjust_temperature(img, value):
        """White balance temperature. value in [-100, 100]"""
        result = img.astype(np.float32)
        shift = value * 0.5
        result[:, :, 0] = np.clip(result[:, :, 0] - shift, 0, 255)  # B
        result[:, :, 2] = np.clip(result[:, :, 2] + shift, 0, 255)  # R
        return result.astype(np.uint8)

    @staticmethod
    def adjust_tint(img, value):
        """Tint: shift green-magenta. value in [-100, 100]"""
        result = img.astype(np.float32)
        shift = value * 0.5
        result[:, :, 1] = np.clip(result[:, :, 1] + shift, 0, 255)
        return result.astype(np.uint8)

    @staticmethod
    def adjust_highlights(img, value):
        """Highlights: adjust bright regions. value in [-100, 100]"""
        result = img.astype(np.float32)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        mask = np.clip((gray - 0.5) * 2.0, 0, 1)
        mask = np.stack([mask] * 3, axis=2)
        shift = value * 1.5
        result = result + mask * shift
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def adjust_shadows(img, value):
        """Shadows: adjust dark regions. value in [-100, 100]"""
        result = img.astype(np.float32)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        mask = np.clip(1.0 - gray * 2.0, 0, 1)
        mask = np.stack([mask] * 3, axis=2)
        shift = value * 1.5
        result = result + mask * shift
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def adjust_whites(img, value):
        """Whites: adjust white clipping point. value in [-100, 100]"""
        result = img.astype(np.float32)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        mask = np.clip((gray - 0.7) * 3.33, 0, 1)
        mask = np.stack([mask] * 3, axis=2)
        result = result + mask * value * 2.0
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def adjust_blacks(img, value):
        """Blacks: adjust black clipping point. value in [-100, 100]"""
        result = img.astype(np.float32)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        mask = np.clip(1.0 - gray * 3.33, 0, 1)
        mask = np.stack([mask] * 3, axis=2)
        result = result + mask * value * 2.0
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def adjust_clarity(img, value):
        """Clarity: midtone local contrast via unsharp mask. value in [-100, 100]"""
        if value == 0:
            return img
        blurred = cv2.GaussianBlur(img, (0, 0), sigmaX=20)
        strength = value / 100.0
        result = cv2.addWeighted(img, 1.0 + strength, blurred, -strength, 0)
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def adjust_dehaze(img, value):
        """Dehaze: dark channel prior based dehazing. value in [0, 100]"""
        if value == 0:
            return img
        strength = value / 100.0
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
        l_channel = lab[:, :, 0]
        clahe = cv2.createCLAHE(clipLimit=2.0 + strength * 4.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(l_channel.astype(np.uint8)).astype(np.float32)
        result = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        return cv2.addWeighted(img, 1.0 - strength, result, strength, 0)

    @staticmethod
    def adjust_sharpen(img, value):
        """Sharpen: unsharp mask. value in [0, 100]"""
        if value == 0:
            return img
        amount = value / 50.0
        blurred = cv2.GaussianBlur(img, (0, 0), sigmaX=2)
        return cv2.addWeighted(img, 1.0 + amount, blurred, -amount, 0)

    @staticmethod
    def adjust_grain(img, value):
        """Film grain simulation. value in [0, 100]"""
        if value == 0:
            return img
        noise = np.random.normal(0, value * 0.5, img.shape).astype(np.float32)
        result = img.astype(np.float32) + noise
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def adjust_vignette(img, value):
        """Vignette: darken edges. value in [0, 100]"""
        if value == 0:
            return img
        h, w = img.shape[:2]
        y, x = np.ogrid[:h, :w]
        cx, cy = w / 2, h / 2
        r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        max_r = np.sqrt(cx ** 2 + cy ** 2)
        mask = 1.0 - (r / max_r) * (value / 100.0)
        mask = np.clip(mask, 0, 1)
        mask = np.stack([mask] * 3, axis=2)
        return (img.astype(np.float32) * mask).astype(np.uint8)

    @staticmethod
    def apply_curve(img, curve_points):
        """Apply tone curve. curve_points: list of (x, y) tuples."""
        if not curve_points or len(curve_points) < 2:
            return img
        xs = [p[0] for p in curve_points]
        ys = [p[1] for p in curve_points]
        from scipy.interpolate import interp1d
        try:
            f = interp1d(xs, ys, kind='cubic', fill_value='extrapolate')
        except Exception:
            f = interp1d(xs, ys, kind='linear', fill_value='extrapolate')
        lut = np.clip(f(np.arange(256)), 0, 255).astype(np.uint8)
        return cv2.LUT(img, lut)

    @staticmethod
    def apply_curves_multi(img, curves_dict):
        """Apply per-channel tone curves.
        curves_dict: {'rgb': [(x,y),...], 'red': [...], 'green': [...], 'blue': [...]}
        Points are normalized [0,1].
        """
        result = img.copy()

        def build_lut(points):
            if len(points) < 2:
                return np.arange(256, dtype=np.uint8)
            xs = [p[0] * 255 for p in points]
            ys = [p[1] * 255 for p in points]
            try:
                from scipy.interpolate import CubicSpline
                cs = CubicSpline(xs, ys, bc_type='clamped')
                lut = np.clip(cs(np.arange(256)), 0, 255).astype(np.uint8)
            except Exception:
                lut = np.clip(np.interp(np.arange(256), xs, ys), 0, 255).astype(np.uint8)
            return lut

        # Apply individual channel curves first (BGR order in OpenCV)
        channel_map = {'blue': 0, 'green': 1, 'red': 2}
        for ch_name, ch_idx in channel_map.items():
            pts = curves_dict.get(ch_name, [(0, 0), (1, 1)])
            if len(pts) >= 2 and pts != [(0, 0), (1, 1)] and pts != [(0.0, 0.0), (1.0, 1.0)]:
                lut = build_lut(pts)
                result[:, :, ch_idx] = cv2.LUT(result[:, :, ch_idx], lut)

        # Apply RGB composite curve to all channels
        rgb_pts = curves_dict.get('rgb', [(0, 0), (1, 1)])
        if len(rgb_pts) >= 2 and rgb_pts != [(0, 0), (1, 1)] and rgb_pts != [(0.0, 0.0), (1.0, 1.0)]:
            lut = build_lut(rgb_pts)
            result = cv2.LUT(result, lut)

        return result

    @staticmethod
    def compute_histogram(img):
        """Compute luminance histogram for display. Returns 256-element array."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
        return hist

    @staticmethod
    def apply_hsl(img, h_shift, s_shift, l_shift, target_hue=None, hue_range=30):
        """HSL adjustment for specific or all color ranges."""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        if target_hue is not None:
            hue = hsv[:, :, 0]
            dist = np.minimum(np.abs(hue - target_hue), 180 - np.abs(hue - target_hue))
            mask = np.clip(1.0 - dist / hue_range, 0, 1)
        else:
            mask = np.ones(hsv.shape[:2], dtype=np.float32)
        hsv[:, :, 0] = (hsv[:, :, 0] + h_shift * mask) % 180
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] + s_shift * mask, 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] + l_shift * mask, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    @staticmethod
    def crop(img, x, y, w, h):
        return img[y:y+h, x:x+w].copy()

    @staticmethod
    def rotate(img, angle):
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        nW = int(h * sin + w * cos)
        nH = int(h * cos + w * sin)
        M[0, 2] += (nW / 2) - center[0]
        M[1, 2] += (nH / 2) - center[1]
        return cv2.warpAffine(img, M, (nW, nH), borderValue=(0, 0, 0))

    @staticmethod
    def flip_horizontal(img):
        return cv2.flip(img, 1)

    @staticmethod
    def flip_vertical(img):
        return cv2.flip(img, 0)

    @staticmethod
    def resize_image(img, width, height, interpolation=cv2.INTER_LANCZOS4):
        return cv2.resize(img, (width, height), interpolation=interpolation)

    @staticmethod
    def blend_images(base, overlay, opacity=1.0, mode='normal'):
        """Blend two images with blend mode support."""
        base_f = base.astype(np.float32) / 255.0
        over_f = overlay.astype(np.float32) / 255.0

        if mode == 'normal':
            result = over_f
        elif mode == 'multiply':
            result = base_f * over_f
        elif mode == 'screen':
            result = 1.0 - (1.0 - base_f) * (1.0 - over_f)
        elif mode == 'overlay':
            mask = base_f < 0.5
            result = np.where(mask, 2 * base_f * over_f,
                              1 - 2 * (1 - base_f) * (1 - over_f))
        elif mode == 'soft_light':
            result = np.where(over_f < 0.5,
                              base_f * (2 * over_f + base_f * (1 - 2 * over_f)),
                              base_f + (2 * over_f - 1) * (np.sqrt(base_f) - base_f))
        elif mode == 'hard_light':
            mask = over_f < 0.5
            result = np.where(mask, 2 * base_f * over_f,
                              1 - 2 * (1 - base_f) * (1 - over_f))
        elif mode == 'color_dodge':
            result = np.where(over_f >= 1.0, 1.0,
                              np.minimum(base_f / (1.0 - over_f + 1e-7), 1.0))
        elif mode == 'color_burn':
            result = np.where(over_f <= 0.0, 0.0,
                              1.0 - np.minimum((1.0 - base_f) / (over_f + 1e-7), 1.0))
        elif mode == 'difference':
            result = np.abs(base_f - over_f)
        elif mode == 'exclusion':
            result = base_f + over_f - 2 * base_f * over_f
        elif mode == 'luminosity':
            base_lab = cv2.cvtColor((base_f * 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
            over_lab = cv2.cvtColor((over_f * 255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
            base_lab[:, :, 0] = over_lab[:, :, 0]
            result = cv2.cvtColor(base_lab.astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32) / 255.0
        else:
            result = over_f

        blended = base_f * (1 - opacity) + result * opacity
        return np.clip(blended * 255, 0, 255).astype(np.uint8)

    # ─────────── Lightroom Missing: Noise Reduction ───────────
    @staticmethod
    def adjust_noise_reduction(img, value):
        """Luminance noise reduction. value in [0, 100]"""
        if value == 0:
            return img
        strength = value / 100.0
        # Wavelet-based: blur slightly in luminance channel
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
        d = int(3 + strength * 12)
        if d % 2 == 0: d += 1
        lab[:, :, 0] = cv2.bilateralFilter(lab[:, :, 0].astype(np.uint8), d,
                                            30 + strength * 70, 30 + strength * 70)
        return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

    @staticmethod
    def adjust_color_noise(img, value):
        """Color (chrominance) noise reduction. value in [0, 100]"""
        if value == 0:
            return img
        strength = value / 100.0
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
        k = int(3 + strength * 10)
        if k % 2 == 0: k += 1
        lab[:, :, 1] = cv2.GaussianBlur(lab[:, :, 1], (k, k), strength * 5)
        lab[:, :, 2] = cv2.GaussianBlur(lab[:, :, 2], (k, k), strength * 5)
        return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

    # ─────────── Lightroom Missing: Transform ───────────
    @staticmethod
    def adjust_perspective_vertical(img, value):
        """Vertical perspective correction. value in [-100, 100]"""
        if value == 0:
            return img
        h, w = img.shape[:2]
        t = value / 200.0
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        shift = w * abs(t)
        if t > 0:  # top squish
            dst = np.float32([[shift, 0], [w - shift, 0], [w, h], [0, h]])
        else:  # bottom squish
            dst = np.float32([[0, 0], [w, 0], [w - shift, h], [shift, h]])
        M = cv2.getPerspectiveTransform(src, dst)
        return cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

    @staticmethod
    def adjust_perspective_horizontal(img, value):
        """Horizontal perspective correction. value in [-100, 100]"""
        if value == 0:
            return img
        h, w = img.shape[:2]
        t = value / 200.0
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        shift = h * abs(t)
        if t > 0:
            dst = np.float32([[0, shift], [w, 0], [w, h], [0, h - shift]])
        else:
            dst = np.float32([[0, 0], [w, shift], [w, h - shift], [0, h]])
        M = cv2.getPerspectiveTransform(src, dst)
        return cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)

    @staticmethod
    def adjust_rotate(img, value):
        """Straighten / rotation. value in [-45, 45] degrees"""
        if value == 0:
            return img
        return ImageProcessor.rotate(img, value)

    # ─────────── Lightroom Missing: Split Toning ───────────
    @staticmethod
    def apply_split_toning(img, highlight_hue=40, highlight_sat=30, shadow_hue=220, shadow_sat=30, balance=0):
        """Split toning: different color tints in highlights and shadows."""
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        balance_f = (balance + 100) / 200.0  # 0..1
        hi_thresh = 0.5 + balance_f * 0.3
        lo_thresh = 0.5 - (1 - balance_f) * 0.3

        hi_mask = np.clip((gray - hi_thresh) / (1.0 - hi_thresh + 1e-7), 0, 1)
        lo_mask = np.clip((lo_thresh - gray) / (lo_thresh + 1e-7), 0, 1)

        result = img.astype(np.float32)
        def tint_channel(mask_2d, hue, sat):
            color_bgr = np.array(cv2.cvtColor(
                np.uint8([[[hue // 2, int(sat * 2.55), 200]]]),
                cv2.COLOR_HSV2BGR)[0][0], dtype=np.float32)
            m = np.stack([mask_2d * sat / 100.0] * 3, axis=2)
            return color_bgr * m

        result += tint_channel(hi_mask, highlight_hue, highlight_sat)
        result += tint_channel(lo_mask, shadow_hue, shadow_sat)
        return np.clip(result, 0, 255).astype(np.uint8)

    # ─────────── Lightroom Missing: Hue Shift per channel ───────────
    @staticmethod
    def adjust_hue(img, value):
        """Global hue rotation. value in [-180, 180]"""
        if value == 0:
            return img
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 0] = (hsv[:, :, 0] + value) % 180
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    # ─────────── Lightroom Missing: Texture ───────────
    @staticmethod
    def adjust_texture(img, value):
        """Texture: fine-detail midtone sharpening. value in [-100, 100]"""
        if value == 0:
            return img
        strength = value / 100.0
        # High frequency extraction at smaller radius than clarity
        blurred = cv2.GaussianBlur(img, (0, 0), sigmaX=5)
        result = cv2.addWeighted(img, 1.0 + strength * 0.8, blurred, -strength * 0.8, 0)
        return np.clip(result, 0, 255).astype(np.uint8)

    # ─────────── Histogram: RGB separate ───────────
    @staticmethod
    def compute_rgb_histogram(img):
        """Returns dict with 'r', 'g', 'b', 'luma' arrays of 256 floats each."""
        hists = {}
        for i, ch in enumerate(['b', 'g', 'r']):
            h = cv2.calcHist([img], [i], None, [256], [0, 256]).flatten()
            hists[ch] = h / (h.max() + 1e-7)  # normalized
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        luma = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
        hists['luma'] = luma / (luma.max() + 1e-7)
        return hists
