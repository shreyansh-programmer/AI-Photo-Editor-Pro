# Next-Gen Agentic System & UI Design Document

## 1. Next-Level Agentic System: "Visionary Agent"

The current copilot is a simple command-executor. The "Visionary Agent" will be a proactive, state-aware autonomous system.

### Core Architecture
- **Perception Layer**: Uses Vision LLMs (Nemotron-3 / GPT-4o) to not just "see" the image, but to create a semantic map of objects, lighting, and aesthetic flaws.
- **Reasoning Layer**: Uses a Chain-of-Thought (CoT) approach to plan edits. It doesn't just execute "exposure +10"; it plans "Fix underexposure -> Enhance sky contrast -> Warm up skin tones".
- **Action Layer**: Expanded toolset including masking, layer management, and specific AI modules (HDR, Lens, etc.).
- **Feedback Loop**: Post-execution analysis to verify if the goal was achieved.

### New Agentic Features
- **Auto-Pilot Mode**: One-click full autonomous editing with a detailed reasoning report.
- **Selective Editing**: Agent can now generate masks for specific objects (e.g., "Make only the flowers more vibrant").
- **Contextual Memory**: Remembers the "vibe" the user is going for across multiple photos.

---

## 2. Next-Gen UI: "Glassmorphism 2.0"

Moving from a static theme to a dynamic, interactive experience.

### Visual Design
- **Deep Glassmorphism**: Multi-layered backdrop blurs with dynamic edge lighting.
- **Animated Transitions**: Every panel, slider, and button will have fluid, physics-based animations.
- **Dynamic Accent Colors**: The UI accent color will subtly shift based on the dominant colors of the photo being edited.

### Interactive Features
- **Floating Command Bar**: A "Spotlight" style interface (Ctrl+K) for quick AI commands.
- **Interactive AI Overlay**: The canvas will show real-time "thinking" heatmaps when the agent is analyzing.
- **Modernized Panels**: Collapsible, draggable panels with improved typography and spacing.

---

## 3. Implementation Plan

### Phase 1: Backend (Agent Engine)
- Upgrade `copilot_engine.py` to support multi-step plans.
- Implement `AgentPlanner` to break down complex requests.
- Add "Tool Definition" system for better LLM steering.

### Phase 2: Frontend (UI/UX)
- Enhance `styles.py` with advanced Qt properties.
- Add `QPropertyAnimation` for smooth UI transitions.
- Implement the "Floating Command Bar".
- Redesign the Copilot chat to feel more like a "Workspace Assistant".

### Phase 3: Integration
- Connect the Agent's "Visual Analysis" to real-time UI updates.
- Implement the "Auto-Pilot" progress report.
