"""
Advance Editor — Batch Processing System (Sync Settings)
Allows applying a consistent editing "recipe" across multiple photos.
"""
import os
import cv2
import json
from PyQt6.QtCore import QThread, pyqtSignal
from engine.image_processor import ImageProcessor
from ui.filters_panel import FilterProcessor

class Recipe:
    """A collection of non-destructive edits to be synced."""
    def __init__(self):
        self.adjustments = {}
        self.curves = {}
        self.filter = None
        self.filter_strength = 100
        
    def from_layer(self, layer, active_filter=None):
        self.adjustments = {k: v for k, v in layer.adjustments.items() if not k.startswith('_')}
        self.curves = layer.adjustments.get('_curves', {})
        self.filter = active_filter
        return self
        
    def save(self, filepath):
        data = {
            "adjustments": self.adjustments,
            "curves": self.curves,
            "filter": self.filter,
            "filter_strength": self.filter_strength
        }
        with open(filepath, 'w') as f:
            json.dump(data, f)
            
    def load(self, filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.adjustments = data.get("adjustments", {})
            self.curves = data.get("curves", {})
            self.filter = data.get("filter")
            self.filter_strength = data.get("filter_strength", 100)
        return self

class BatchProcessor(QThread):
    """Applies a Recipe to a list of files asynchronously."""
    progress = pyqtSignal(int, int, str) # current, total, filename
    finished = pyqtSignal()
    error = pyqtSignal(str, str) # filename, error
    
    def __init__(self, recipe, filepaths, output_dir):
        super().__init__()
        self.recipe = recipe
        self.filepaths = filepaths
        self.output_dir = output_dir
        
    def run(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        total = len(self.filepaths)
        for i, filepath in enumerate(self.filepaths):
            filename = os.path.basename(filepath)
            self.progress.emit(i+1, total, filename)
            
            try:
                # 1. Read Image
                img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
                if img is None:
                    continue
                    
                if len(img.shape) == 2:
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                elif img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                result = img.copy()
                
                # 2. Apply Filter Base
                if self.recipe.filter:
                    result = FilterProcessor.apply_preset(result, self.recipe.filter, self.recipe.filter_strength)
                    
                # 3. Apply Adjustments
                for adj_name, adj_value in self.recipe.adjustments.items():
                    if adj_value == 0: continue
                    method = getattr(ImageProcessor, f'adjust_{adj_name}', None)
                    if method:
                        result = method(result, adj_value)
                        
                # 4. Apply Curves
                if self.recipe.curves:
                    result = ImageProcessor.apply_curves_multi(result, self.recipe.curves)
                    
                # 5. Save Output
                out_path = os.path.join(self.output_dir, filename)
                
                # Use high quality encoding
                ext = os.path.splitext(filename)[1].lower()
                params = []
                if ext in ['.jpg', '.jpeg']:
                    params = [cv2.IMWRITE_JPEG_QUALITY, 95]
                elif ext == '.webp':
                    params = [cv2.IMWRITE_WEBP_QUALITY, 95]
                cv2.imwrite(out_path, result, params)
                
            except Exception as e:
                self.error.emit(filename, str(e))
                
        self.finished.emit()
