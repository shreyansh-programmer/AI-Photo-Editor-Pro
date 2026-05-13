"""
Advance Editor - History Manager (Undo/Redo)
Memory-efficient state-based history with configurable depth.
"""
import copy
import numpy as np


class HistoryState:
    """A single history state snapshot."""

    def __init__(self, description, layer_data):
        self.description = description
        self.layer_data = layer_data  # Serialized layer state


class HistoryManager:
    """Manages undo/redo history."""

    def __init__(self, max_states=50):
        self.states = []
        self.current_index = -1
        self.max_states = max_states

    def push(self, description, layer_system):
        """Save current state to history."""
        # Serialize layer data
        layer_data = []
        for layer in layer_system.layers:
            layer_data.append({
                'id': layer.id,
                'name': layer.name,
                'image': layer.image.copy(),
                'visible': layer.visible,
                'locked': layer.locked,
                'opacity': layer.opacity,
                'blend_mode': layer.blend_mode,
                'layer_type': layer.layer_type,
                'adjustments': dict(layer.adjustments),
            })

        state = HistoryState(description, layer_data)

        # Remove any redo states
        self.states = self.states[:self.current_index + 1]

        # Add new state
        self.states.append(state)
        self.current_index = len(self.states) - 1

        # Trim old states if exceeding max
        if len(self.states) > self.max_states:
            self.states = self.states[-self.max_states:]
            self.current_index = len(self.states) - 1

    def undo(self, layer_system):
        """Restore previous state."""
        if not self.can_undo():
            return False
        self.current_index -= 1
        self._restore(layer_system)
        return True

    def redo(self, layer_system):
        """Restore next state."""
        if not self.can_redo():
            return False
        self.current_index += 1
        self._restore(layer_system)
        return True

    def can_undo(self):
        return self.current_index > 0

    def can_redo(self):
        return self.current_index < len(self.states) - 1

    def _restore(self, layer_system):
        """Restore layer system from saved state."""
        from engine.layer_system import Layer
        state = self.states[self.current_index]
        layer_system.layers.clear()

        for data in state.layer_data:
            layer = Layer(data['name'], data['image'], data['layer_type'])
            layer.id = data['id']
            layer.visible = data['visible']
            layer.locked = data['locked']
            layer.opacity = data['opacity']
            layer.blend_mode = data['blend_mode']
            layer.adjustments = dict(data['adjustments'])
            layer_system.layers.append(layer)

        if layer_system.layers:
            layer_system.active_layer_id = layer_system.layers[-1].id

    def get_history_list(self):
        """Return list of history descriptions."""
        return [(i, s.description, i == self.current_index)
                for i, s in enumerate(self.states)]

    def clear(self):
        self.states.clear()
        self.current_index = -1
