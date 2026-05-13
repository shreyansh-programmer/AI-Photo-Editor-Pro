"""
Advance Editor - Non-Destructive Layer System
Supports multiple layers with blend modes, opacity, visibility.
"""
import cv2
import numpy as np
from engine.image_processor import ImageProcessor
import uuid


class Layer:
    """A single image layer with properties."""

    def __init__(self, name, image, layer_type='pixel'):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.image = image.copy()  # Original pixels (never modified)
        self.visible = True
        self.locked = False
        self.opacity = 100  # 0-100
        self.blend_mode = 'normal'
        self.layer_type = layer_type  # 'pixel' or 'adjustment'
        self.adjustments = {}  # Non-destructive adjustments stored here
        self._cache = None
        self._cache_valid = False

    def get_rendered(self):
        """Get the layer image with adjustments applied."""
        if self._cache_valid and self._cache is not None:
            return self._cache

        result = self.image.copy()

        # Apply non-destructive adjustments
        for adj_name, adj_value in self.adjustments.items():
            if adj_name.startswith('_'):
                continue
            if adj_name.startswith('split_') or adj_name.startswith('hsl_'):
                continue  # handled below in batch
            if adj_value == 0:
                continue
            method = getattr(ImageProcessor, f'adjust_{adj_name}', None)
            if method:
                try:
                    result = method(result, adj_value)
                except Exception:
                    pass

        # Apply HSL Color Mixer per-channel
        from engine.image_processor import ImageProcessor as IP
        hsl_colors = [
            ('red', 15),    ('orange', 25),  ('yellow', 45),
            ('green', 75),  ('aqua', 105),   ('blue', 120),
            ('purple', 150),('magenta', 165),
        ]
        for color_name, target_hue in hsl_colors:
            h_val = self.adjustments.get(f'hsl_h_{color_name}', 0)
            s_val = self.adjustments.get(f'hsl_s_{color_name}', 0)
            l_val = self.adjustments.get(f'hsl_l_{color_name}', 0)
            if h_val != 0 or s_val != 0 or l_val != 0:
                result = IP.apply_hsl(result,
                    h_shift=h_val * 0.5,
                    s_shift=s_val * 1.5,
                    l_shift=l_val * 1.5,
                    target_hue=target_hue, hue_range=25)

        # Apply Split Toning
        hi_hue = self.adjustments.get('split_hi_hue', 40)
        hi_sat = self.adjustments.get('split_hi_sat', 0)
        lo_hue = self.adjustments.get('split_lo_hue', 220)
        lo_sat = self.adjustments.get('split_lo_sat', 0)
        balance = self.adjustments.get('split_balance', 0)
        if hi_sat > 0 or lo_sat > 0:
            result = IP.apply_split_toning(result, hi_hue, hi_sat, lo_hue, lo_sat, balance)

        # Apply curves (stored as _curves key)
        curves = self.adjustments.get('_curves')
        if curves:
            result = ImageProcessor.apply_curves_multi(result, curves)

        self._cache = result
        self._cache_valid = True
        return result

    def invalidate_cache(self):
        self._cache_valid = False
        self._cache = None

    def set_adjustment(self, name, value):
        self.adjustments[name] = value
        self.invalidate_cache()

    def set_image(self, image):
        self.image = image.copy()
        self.invalidate_cache()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'visible': self.visible,
            'locked': self.locked,
            'opacity': self.opacity,
            'blend_mode': self.blend_mode,
            'layer_type': self.layer_type,
        }


class LayerSystem:
    """Manages multiple layers with compositing."""

    BLEND_MODES = [
        'normal', 'multiply', 'screen', 'overlay',
        'soft_light', 'hard_light', 'color_dodge', 'color_burn',
        'difference', 'exclusion', 'luminosity'
    ]

    def __init__(self):
        self.layers = []
        self.active_layer_id = None

    def add_layer(self, name, image, layer_type='pixel'):
        layer = Layer(name, image, layer_type)
        self.layers.append(layer)
        self.active_layer_id = layer.id
        return layer

    def remove_layer(self, layer_id):
        self.layers = [l for l in self.layers if l.id != layer_id]
        if self.active_layer_id == layer_id:
            self.active_layer_id = self.layers[-1].id if self.layers else None

    def get_layer(self, layer_id):
        for l in self.layers:
            if l.id == layer_id:
                return l
        return None

    def get_active_layer(self):
        return self.get_layer(self.active_layer_id)

    def set_active_layer(self, layer_id):
        self.active_layer_id = layer_id

    def move_layer(self, layer_id, direction):
        """Move layer up or down. direction: 1=up, -1=down."""
        for i, l in enumerate(self.layers):
            if l.id == layer_id:
                new_idx = i + direction
                if 0 <= new_idx < len(self.layers):
                    self.layers[i], self.layers[new_idx] = self.layers[new_idx], self.layers[i]
                break

    def duplicate_layer(self, layer_id):
        src = self.get_layer(layer_id)
        if src:
            new_layer = Layer(f"{src.name} (copy)", src.image.copy(), src.layer_type)
            new_layer.opacity = src.opacity
            new_layer.blend_mode = src.blend_mode
            new_layer.adjustments = src.adjustments.copy()
            idx = self.layers.index(src)
            self.layers.insert(idx + 1, new_layer)
            self.active_layer_id = new_layer.id
            return new_layer
        return None

    def flatten(self):
        """Flatten all layers into one."""
        result = self.compose()
        if result is not None:
            self.layers.clear()
            self.add_layer("Flattened", result)
        return result

    def compose(self):
        """Compose all visible layers into a single image."""
        visible = [l for l in self.layers if l.visible]
        if not visible:
            return None

        # Start with first visible layer
        base = visible[0].get_rendered().copy()

        # Composite subsequent layers
        for layer in visible[1:]:
            overlay = layer.get_rendered()

            # Resize overlay if needed
            if overlay.shape[:2] != base.shape[:2]:
                overlay = cv2.resize(overlay, (base.shape[1], base.shape[0]))

            opacity = layer.opacity / 100.0
            base = ImageProcessor.blend_images(base, overlay, opacity, layer.blend_mode)

        return base

    def clear(self):
        self.layers.clear()
        self.active_layer_id = None
