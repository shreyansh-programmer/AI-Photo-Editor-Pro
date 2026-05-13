"""
Advance Editor — Advanced AI Modules
Additional AI capabilities including Face, Lens, HDR, and Style transfer.
"""
import cv2
import numpy as np
import logging
import warnings

warnings.filterwarnings("ignore")
log = logging.getLogger("AIEngineAdvanced")

class EdgeMatting:
    """Advanced Edge Matting using Guided Filter for hair-level mask precision."""
    
    @staticmethod
    def guided_filter(I, p, r=15, eps=1e-3):
        """
        Implementation of the Guided Filter.
        I: guidance image (usually the original high-res color image)
        p: filtering input image (usually the rough AI mask)
        r: radius
        eps: regularization
        """
        if len(I.shape) == 3:
            # Color guidance
            I_gray = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        else:
            I_gray = I.astype(np.float32) / 255.0
            
        p = p.astype(np.float32) / 255.0
        
        mean_I = cv2.boxFilter(I_gray, cv2.CV_32F, (r, r))
        mean_p = cv2.boxFilter(p, cv2.CV_32F, (r, r))
        mean_Ip = cv2.boxFilter(I_gray * p, cv2.CV_32F, (r, r))
        
        cov_Ip = mean_Ip - mean_I * mean_p
        
        mean_II = cv2.boxFilter(I_gray * I_gray, cv2.CV_32F, (r, r))
        var_I = mean_II - mean_I * mean_I
        
        a = cov_Ip / (var_I + eps)
        b = mean_p - a * mean_I
        
        mean_a = cv2.boxFilter(a, cv2.CV_32F, (r, r))
        mean_b = cv2.boxFilter(b, cv2.CV_32F, (r, r))
        
        q = mean_a * I_gray + mean_b
        return np.clip(q * 255, 0, 255).astype(np.uint8)
        
    @staticmethod
    def refine_mask(img, rough_mask, radius=10, eps=1e-4):
        """Takes a rough AI mask and perfectly snaps it to the image edges."""
        return EdgeMatting.guided_filter(img, rough_mask, r=radius, eps=eps)

class HDRMergeAI:
    """Pseudo-HDR from a single image using OpenCV tone mapping and local contrast."""
    
    @staticmethod
    def apply(img, strength=50):
        # We simulate HDR by creating under and over exposed versions, then merging
        factor = strength / 100.0
        
        # Create exposures
        img_float = img.astype(np.float32) / 255.0
        
        # Under-exposed (gamma < 1)
        under = np.power(img_float, 1.0 + (factor * 1.5))
        
        # Over-exposed (gamma > 1)
        over = np.power(img_float, max(0.1, 1.0 - (factor * 0.7)))
        
        # Original
        normal = img_float
        
        # Merge using Mertens algorithm (Exposure Fusion)
        merge_mertens = cv2.createMergeMertens()
        hdr = merge_mertens.process([
            (under * 255).astype(np.uint8), 
            (normal * 255).astype(np.uint8), 
            (over * 255).astype(np.uint8)
        ])
        
        # Boost local contrast slightly
        hdr_8bit = np.clip(hdr * 255, 0, 255).astype(np.uint8)
        
        # Additional CLAHE for HDR look
        lab = cv2.cvtColor(hdr_8bit, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=1.5 + factor*2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        merged = cv2.merge((l, a, b))
        final = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
        
        # Blend with original based on strength
        return cv2.addWeighted(img, 1.0 - factor, final, factor, 0)

class LensAI:
    """Corrects lens distortion and chromatic aberration."""
    
    @staticmethod
    def correct_distortion(img, amount=50):
        """Amount positive = barrel distortion (fix pincushion), negative = pincushion (fix barrel)"""
        h, w = img.shape[:2]
        
        # Normalize amount from -100..100 to a suitable k1 value
        # Typical k1 is between -1e-5 and 1e-5
        k1 = (amount / 100.0) * 0.00001
        
        # Camera matrix
        f = max(h, w)
        K = np.array([
            [f, 0, w/2],
            [0, f, h/2],
            [0, 0, 1]
        ], dtype=np.float32)
        
        # Distortion coeffs: k1, k2, p1, p2, k3
        D = np.array([k1, 0, 0, 0, 0], dtype=np.float32)
        
        # Optimal new camera matrix
        new_K, roi = cv2.getOptimalNewCameraMatrix(K, D, (w, h), 1, (w, h))
        
        # Undistort
        undistorted = cv2.undistort(img, K, D, None, new_K)
        return undistorted

    @staticmethod
    def correct_fringing(img, amount=50):
        """Fix chromatic aberration / color fringing"""
        if amount == 0: return img
        
        b, g, r = cv2.split(img)
        
        # Scale factor for R and B channels
        scale = 1.0 - (amount / 1000.0)
        h, w = img.shape[:2]
        
        # Resize R and B slightly towards center
        M = cv2.getRotationMatrix2D((w/2, h/2), 0, scale)
        r_corr = cv2.warpAffine(r, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        b_corr = cv2.warpAffine(b, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        
        return cv2.merge([b_corr, g, r_corr])

class StyleTransferAI:
    """Basic Color Grading Transfer (Reinhard et al.)"""
    
    @staticmethod
    def transfer_color(source, target):
        """Transfers the color palette from source to target."""
        # Convert to LAB space
        src_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
        tgt_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Get mean and std
        src_mean, src_std = cv2.meanStdDev(src_lab)
        tgt_mean, tgt_std = cv2.meanStdDev(tgt_lab)
        
        src_mean = src_mean.flatten()
        src_std = src_std.flatten()
        tgt_mean = tgt_mean.flatten()
        tgt_std = tgt_std.flatten()
        
        # Apply transfer
        result = tgt_lab.copy()
        for i in range(3):
            # Avoid division by zero
            std_t = tgt_std[i] if tgt_std[i] > 0 else 1
            result[:,:,i] = ((tgt_lab[:,:,i] - tgt_mean[i]) * (src_std[i] / std_t)) + src_mean[i]
            
        result = np.clip(result, 0, 255).astype(np.uint8)
        return cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

class WhiteBalanceAI:
    """Neural/Algorithmic white balance correction."""
    
    @staticmethod
    def auto_wb(img):
        """Gray world assumption based white balance."""
        result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
        avg_a = np.average(result[:, :, 1])
        avg_b = np.average(result[:, :, 2])
        
        result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
        result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
        
        result = np.clip(result, 0, 255).astype(np.uint8)
        return cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

class FaceAI:
    """Advanced facial recognition and retouching using MediaPipe."""
    
    _mp_face_mesh = None
    
    @classmethod
    def _ensure_mediapipe(cls):
        if cls._mp_face_mesh is None:
            try:
                import mediapipe as mp
                cls._mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=True, max_num_faces=5, refine_landmarks=True,
                    min_detection_confidence=0.5)
                return True
            except ImportError:
                log.warning("MediaPipe not installed. FaceAI requires mediapipe>=0.10.9")
                return False
        return True

    @staticmethod
    def retouch_faces(img, skin_smoothing=50, eye_brighten=30, teeth_whiten=30):
        if not FaceAI._ensure_mediapipe():
            return img

        h, w = img.shape[:2]
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = FaceAI._mp_face_mesh.process(rgb)
        
        if not results.multi_face_landmarks:
            return img  # No faces found
            
        result = img.copy()
        
        # Skin smoothing mask
        skin_mask = np.zeros((h, w), dtype=np.uint8)
        eye_mask = np.zeros((h, w), dtype=np.uint8)
        teeth_mask = np.zeros((h, w), dtype=np.uint8)
        
        # Define facial landmark indices (approximate contours)
        import mediapipe as mp
        facemesh_indices = mp.solutions.face_mesh.FACEMESH_FACE_OVAL
        lips_indices = mp.solutions.face_mesh.FACEMESH_LIPS
        left_eye_indices = mp.solutions.face_mesh.FACEMESH_LEFT_EYE
        right_eye_indices = mp.solutions.face_mesh.FACEMESH_RIGHT_EYE
        
        for face_landmarks in results.multi_face_landmarks:
            # 1. Skin Mask (Oval minus eyes/lips)
            oval_pts = np.array([(int(face_landmarks.landmark[p[0]].x * w), 
                                  int(face_landmarks.landmark[p[0]].y * h)) 
                                 for p in facemesh_indices], dtype=np.int32)
            face_hull = cv2.convexHull(oval_pts)
            cv2.fillConvexPoly(skin_mask, face_hull, 255)
            
            # Exclude lips and eyes from skin mask
            for indices in [lips_indices, left_eye_indices, right_eye_indices]:
                pts = np.array([(int(face_landmarks.landmark[p[0]].x * w), 
                                 int(face_landmarks.landmark[p[0]].y * h)) 
                                for p in indices], dtype=np.int32)
                hull = cv2.convexHull(pts)
                cv2.fillConvexPoly(skin_mask, hull, 0)
                
                # Add to specific masks
                if indices == lips_indices:
                    cv2.fillConvexPoly(teeth_mask, hull, 255)
                else:
                    cv2.fillConvexPoly(eye_mask, hull, 255)
        
        # Blur masks for smooth transitions
        skin_mask = cv2.GaussianBlur(skin_mask, (21, 21), 10)
        eye_mask = cv2.GaussianBlur(eye_mask, (11, 11), 5)
        teeth_mask = cv2.GaussianBlur(teeth_mask, (7, 7), 3)
        
        # Apply Skin Smoothing using PROFESSIONAL FREQUENCY SEPARATION
        if skin_smoothing > 0:
            # 1. Blur the image to get Low Frequency (Color/Tone)
            blur_radius = int(5 + skin_smoothing / 5)
            if blur_radius % 2 == 0: blur_radius += 1
            low_freq = cv2.GaussianBlur(result, (blur_radius, blur_radius), 0)
            
            # 2. Subtract blur from original to get High Frequency (Texture/Pores)
            # High_freq = Original - Low_Freq + 128 (offset to avoid negative values)
            high_freq = cv2.addWeighted(result, 1.0, low_freq, -1.0, 128)
            
            # 3. Smooth the Low Frequency (Remove blotchiness)
            d = int(5 + skin_smoothing / 10)
            sigma = 30 + skin_smoothing
            smoothed_low_freq = cv2.bilateralFilter(low_freq, d, sigma, sigma)
            
            # 4. Recombine Smoothed Low Frequency + Original High Frequency (Texture preserved!)
            # Result = Smoothed_Low_Freq + High_Freq - 128
            recombined = cv2.addWeighted(smoothed_low_freq, 1.0, high_freq, 1.0, -128)
            
            # 5. Blend using Edge-Refined Mask
            # Refine the skin mask so it doesn't bleed over jawlines/hair
            refined_skin_mask = EdgeMatting.refine_mask(img, skin_mask, radius=8, eps=1e-3)
            mask_f = refined_skin_mask.astype(np.float32) / 255.0 * (skin_smoothing / 100.0)
            mask_3 = np.stack([mask_f]*3, axis=2)
            
            result = result.astype(np.float32) * (1 - mask_3) + recombined.astype(np.float32) * mask_3
            result = np.clip(result, 0, 255).astype(np.uint8)
            
        # Apply Eye Brightening
        if eye_brighten > 0:
            bright_eyes = cv2.addWeighted(result, 1.0 + (eye_brighten/100.0), result, 0, 10)
            mask_f = eye_mask.astype(np.float32) / 255.0 * (eye_brighten / 100.0)
            mask_3 = np.stack([mask_f]*3, axis=2)
            result = result.astype(np.float32) * (1 - mask_3) + bright_eyes.astype(np.float32) * mask_3
            result = result.astype(np.uint8)
            
        # Apply Teeth Whitening (Desaturate and Brighten)
        if teeth_whiten > 0:
            hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:,:,1] = np.clip(hsv[:,:,1] * (1.0 - (teeth_whiten/100.0)), 0, 255) # desaturate yellow
            hsv[:,:,2] = np.clip(hsv[:,:,2] + (teeth_whiten * 0.5), 0, 255) # brighten
            white_teeth = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
            
            mask_f = teeth_mask.astype(np.float32) / 255.0 * (teeth_whiten / 100.0)
            mask_3 = np.stack([mask_f]*3, axis=2)
            result = result.astype(np.float32) * (1 - mask_3) + white_teeth.astype(np.float32) * mask_3
            result = result.astype(np.uint8)
            
        return result

class SuperResAI:
    """Upscales image resolution."""
    @staticmethod
    def upscale(img, scale=2):
        """High quality upscaling using Lanczos4 and edge sharpening."""
        h, w = img.shape[:2]
        upscaled = cv2.resize(img, (w*scale, h*scale), interpolation=cv2.INTER_LANCZOS4)
        
        # Subtle unsharp mask to restore edge contrast lost in interpolation
        blurred = cv2.GaussianBlur(upscaled, (0, 0), 2.0)
        return cv2.addWeighted(upscaled, 1.2, blurred, -0.2, 0)

class HealAI:
    """Advanced content-aware fill / healing brush using PatchMatch algorithms (simulated via Telea)."""
    @staticmethod
    def apply(img, mask):
        if mask is None or not np.any(mask):
            return img
        # Dilate mask slightly to ensure boundaries are covered
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dilated = cv2.dilate(mask, kernel, iterations=1)
        # Use Telea algorithm for high quality structure inpainting
        return cv2.inpaint(img, dilated, inpaintRadius=10, flags=cv2.INPAINT_TELEA)

class SceneDetectAI:
    """Detects scene characteristics and suggests auto-edits."""
    @staticmethod
    def analyze_scene(img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # Check for nature/landscape (lots of green/blue)
        green_mask = cv2.inRange(h, 35, 85)
        blue_mask = cv2.inRange(h, 90, 130)
        
        green_ratio = np.sum(green_mask > 0) / (img.shape[0] * img.shape[1])
        blue_ratio = np.sum(blue_mask > 0) / (img.shape[0] * img.shape[1])
        
        # Check for dark scene
        avg_v = np.mean(v)
        
        scene_type = "Standard"
        suggested_preset = "Cinematic Teal/Orange"
        
        if green_ratio > 0.2 and blue_ratio > 0.1:
            scene_type = "Landscape"
            suggested_preset = "Landscape & Nature 001"
        elif avg_v < 60:
            scene_type = "Night/Low Light"
            suggested_preset = "Matte & Fade 001"
        
        return {
            "scene_type": scene_type,
            "brightness": "Dark" if avg_v < 85 else ("Bright" if avg_v > 170 else "Normal"),
            "suggested_preset": suggested_preset
        }

class CinematicStudioAI:
    """
    A groundbreaking AI feature: Turns a 2D photo into a 3D scene using Depth Maps.
    Computes surface normals and allows true 3D point lighting and volumetric fog.
    """
    
    @staticmethod
    def compute_normals(depth_map):
        """Converts a 2D depth map into a 3D surface normal map using Sobel filters."""
        # Blur depth slightly to reduce noise in normals
        smooth_depth = cv2.GaussianBlur(depth_map, (5, 5), 0)
        
        # Compute gradients
        dzdx = cv2.Sobel(smooth_depth, cv2.CV_32F, 1, 0, ksize=3)
        dzdy = cv2.Sobel(smooth_depth, cv2.CV_32F, 0, 1, ksize=3)
        
        # Normal vectors (cross product of tangent vectors)
        # Tangent X: (1, 0, dzdx), Tangent Y: (0, 1, dzdy)
        # Normal = (-dzdx, -dzdy, 1)
        normals = np.dstack((-dzdx, -dzdy, np.ones_like(smooth_depth)))
        
        # Normalize the vectors
        norm = np.linalg.norm(normals, axis=2, keepdims=True)
        normals = normals / (norm + 1e-7)
        
        return normals

    @staticmethod
    def add_3d_point_light(img, depth_map, light_x, light_y, light_z, color=(255, 255, 255), intensity=1.0, ambient=0.2):
        """
        Relights the 2D image using true 3D Lambertian reflectance.
        light_x, light_y are normalized [0.0 - 1.0]. light_z represents height above image.
        """
        normals = CinematicStudioAI.compute_normals(depth_map)
        h, w = img.shape[:2]
        
        # Create pixel coordinate grid
        Y, X = np.mgrid[0:h, 0:w]
        
        # Normalize coordinates to [-1, 1] for X/Y
        X_norm = (X / w) * 2.0 - 1.0
        Y_norm = (Y / h) * 2.0 - 1.0
        
        # Convert light coordinates from [0, 1] to [-1, 1]
        lx = light_x * 2.0 - 1.0
        ly = light_y * 2.0 - 1.0
        lz = light_z
        
        # Calculate light direction vector for each pixel
        # The 3D position of the pixel is (X_norm, Y_norm, depth)
        dx = lx - X_norm
        dy = ly - Y_norm
        dz = lz - depth_map
        
        light_dirs = np.dstack((dx, dy, dz))
        # Normalize light directions
        light_norm = np.linalg.norm(light_dirs, axis=2, keepdims=True)
        light_dirs = light_dirs / (light_norm + 1e-7)
        
        # Calculate Lambertian diffuse reflection (Dot product of Normal and Light Direction)
        diffuse = np.sum(normals * light_dirs, axis=2)
        diffuse = np.clip(diffuse, 0, 1)
        
        # Distance attenuation (Inverse square law approximation)
        distance_sq = dx**2 + dy**2 + dz**2
        attenuation = 1.0 / (1.0 + 2.0 * distance_sq)
        
        # Final illumination map
        illumination = ambient + (diffuse * attenuation * intensity)
        illumination = np.clip(illumination, 0, 2.0)
        
        # Apply light color
        light_color = np.array(color, dtype=np.float32) / 255.0
        illum_color = np.dstack([illumination * light_color[0], 
                                 illumination * light_color[1], 
                                 illumination * light_color[2]])
        
        # Multiply image by illumination
        result = img.astype(np.float32) * illum_color
        return np.clip(result, 0, 255).astype(np.uint8)

    @staticmethod
    def add_volumetric_fog(img, depth_map, fog_color=(200, 210, 220), density=0.5, height_falloff=True):
        """
        Adds realistic 3D atmospheric perspective (volumetric fog).
        Fog gets thicker further away (based on depth map).
        """
        # Fog intensity is directly proportional to depth (assuming depth=1 is far, depth=0 is near)
        # Actually depth maps usually have 1=near, 0=far. Let's invert if necessary.
        # Assuming RelightAI depth: usually 1 is near, 0 is far.
        far_mask = 1.0 - depth_map 
        
        fog_factor = 1.0 - np.exp(-far_mask * density * 3.0)
        
        if height_falloff:
            # Fog is usually thicker at the bottom of the image
            h, w = img.shape[:2]
            Y = np.linspace(0.0, 1.0, h).reshape(-1, 1)
            Y = np.broadcast_to(Y, (h, w))
            fog_factor = fog_factor * Y
            
        fog_factor = np.clip(fog_factor, 0, 1)
        
        fog_layer = np.full_like(img, fog_color, dtype=np.float32)
        fog_factor_3 = np.dstack([fog_factor]*3)
        
        result = img.astype(np.float32) * (1 - fog_factor_3) + fog_layer * fog_factor_3
        return np.clip(result, 0, 255).astype(np.uint8)

class MaskAI:
    """Robust masking pipeline for combining, intersecting, and refining AI masks."""
    
    @staticmethod
    def add_masks(mask1, mask2):
        if mask1 is None: return mask2
        if mask2 is None: return mask1
        return cv2.bitwise_or(mask1, mask2)
        
    @staticmethod
    def subtract_masks(base_mask, subtract_mask):
        if base_mask is None: return None
        if subtract_mask is None: return base_mask
        # base_mask AND NOT subtract_mask
        not_mask2 = cv2.bitwise_not(subtract_mask)
        return cv2.bitwise_and(base_mask, not_mask2)
        
    @staticmethod
    def intersect_masks(mask1, mask2):
        if mask1 is None or mask2 is None: return None
        return cv2.bitwise_and(mask1, mask2)
        
    @staticmethod
    def invert_mask(mask):
        if mask is None: return None
        return cv2.bitwise_not(mask)
        
    @staticmethod
    def apply_adjustment_with_mask(img, mask, adjustment_func, *args, **kwargs):
        """Applies any adjustment function only to the masked area, blending smoothly."""
        if mask is None:
            return adjustment_func(img, *args, **kwargs)
            
        adjusted = adjustment_func(img, *args, **kwargs)
        mask_f = mask.astype(np.float32) / 255.0
        
        # Expand dims if image is color
        if len(img.shape) == 3:
            mask_3 = np.stack([mask_f]*3, axis=2)
            result = img.astype(np.float32) * (1 - mask_3) + adjusted.astype(np.float32) * mask_3
        else:
            result = img.astype(np.float32) * (1 - mask_f) + adjusted.astype(np.float32) * mask_f
            
        return result.astype(np.uint8)
