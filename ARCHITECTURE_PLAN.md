  "tool_name": "adjust_exposure",
      "description": "Adjusts the overall brightness of the image.",
      "parameters": {"value": {"type": "integer", "min": -100, "max": 100}}
    }
    ```
-   **Modification**: `copilot_engine.py` will call `AgentPlanner` to get a structured plan instead of directly parsing `[EXECUTE:...]` tags.

**D. Action Layer (Enhanced `main_window.py` / `engine` modules)**
-   **Expanded Toolset**: The agent will have access to a wider range of granular operations:
    -   **Layer Management**: Add/remove layers, change blend modes, adjust opacity, create adjustment layers.
    -   **Masking**: Generate, refine, and apply masks to specific regions or objects (leveraging `MaskAI` in `ai_advanced.py`).
    -   **Advanced AI Tools**: Direct calls to `HDRMergeAI`, `LensAI`, `StyleTransferAI`, `FaceAI`, etc., with specific parameters.
-   **Transactional Execution**: Implement a mechanism to group multiple agent actions into a single undoable history state.
    -   **Modification**: `main_window.py`'s `_on_copilot_exec` will be updated to handle a list of commands and potentially commit them as a single history entry.

### 1.2. Agentic System Enhancements

-   **Auto-Pilot Mode**: The `_auto_pilot` function in `copilot_panel.py` will trigger the `AgentOrchestrator` with a goal to fully enhance the image, allowing it to generate and execute a multi-step plan.
-   **Selective Editing**: The agent will be able to request mask generation (e.g., `MaskAI.detect_skin`, `BackgroundAI.get_mask`) and then apply adjustments only to the masked regions using `MaskAI.apply_adjustment_with_mask`.
-   **Contextual Memory**: The `AgentOrchestrator` will maintain a session history and potentially use a small vector database (in-memory for now) to store semantic descriptions of images and successful edit sequences, allowing for more intelligent suggestions over time.

## 2. Glassmorphism 2.0: Next-Gen UI Redesign Architecture

The UI will be upgraded to provide a more dynamic, visually rich, and interactive experience, leveraging Qt's animation framework and advanced styling capabilities.

### 2.1. Visual Design & Styling

-   **Deep Glassmorphism**: Extend `styles.py` to define more complex gradients, shadows, and blur effects for panels and elements, creating a multi-layered glass aesthetic.
    -   **Modification**: `styles.py` will include new CSS properties for `QGraphicsDropShadowEffect` and `QGraphicsBlurEffect` (if supported by PyQt6's QSS, otherwise implemented via custom painting or proxy styles).
-   **Dynamic Accent Colors**: Implement a mechanism in `main_window.py` to analyze the dominant colors of the currently loaded image and dynamically update a set of CSS variables or QSS properties in `styles.py`.
    -   **Modification**: A new method `_update_accent_color(image)` in `main_window.py` will use `cv2.kmeans` or similar to find dominant colors and then update the stylesheet.
-   **Animated Transitions**: Integrate `QPropertyAnimation` for smooth transitions between UI states.
    -   **Modification**: `main_window.py` and panel widgets will use `QPropertyAnimation` for showing/hiding panels, tab changes, and button interactions.

### 2.2. Interactive Features

-   **Floating Command Bar (`command_bar.py` - NEW MODULE)**
    -   **Role**: A global, searchable command palette (like VS Code's Command Palette or macOS Spotlight) for quick access to agent commands, tools, and settings.
    -   **Trigger**: `Ctrl+K` shortcut.
    -   **Functionality**: Users can type natural language commands or search for specific tools. The input will be fed to the `AgentOrchestrator`.
    -   **Implementation**: A `QLineEdit` with a `QListView` for suggestions, styled with glassmorphism effects and animations.
-   **Interactive AI Overlay (Enhanced `canvas_widget.py`)**
    -   **Real-time Feedback**: When the agent is analyzing or applying selective edits, the canvas will display visual cues.
    -   **Heatmaps**: Show areas of interest or regions being processed by the AI (e.g., skin detection, sky mask).
    -   **Progress Visualization**: More detailed progress indicators for long-running AI tasks.
    -   **Modification**: `canvas_widget.py`'s `paintEvent` will be extended to draw these dynamic overlays based on data provided by the `AgentOrchestrator`.
-   **Modernized Panels (Enhanced `ui/panels.py`, `ui/library_widget.py`, `ui/copilot_panel.py`)**
    -   **Collapsible/Draggable**: Ensure all panels (Adjustments, AI Tools, Layers) are easily manageable.
    -   **Improved Typography & Spacing**: Further refine the layout and text presentation for optimal readability and aesthetic appeal.
    -   **Micro-animations**: Add subtle animations to sliders, checkboxes, and buttons on interaction.

## 3. Integration & Refinement

-   **Centralized Event Bus**: Implement a simple `QObject`-based event bus to allow different UI components and the agentic backend to communicate asynchronously without tight coupling.
-   **Error Handling & Feedback**: Improve user feedback for agent actions, including success messages, warnings, and clear error reporting.
-   **Performance Optimization**: Ensure that animations and AI processing do not degrade overall application responsiveness. Leverage threading for AI tasks (already present in `CopilotWorker`).

This architectural plan provides a roadmap for evolving the AI Photo Editor Pro into a highly intelligent and visually stunning application. The next steps will involve implementing these changes incrementally, starting with the agentic backend.
