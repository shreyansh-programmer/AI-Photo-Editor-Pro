# AI Photo Editor Pro 🎨✨

**A Professional-Grade, Museum-Quality AI Photo Editor with Offline Intelligence.**

AI Photo Editor Pro is a high-performance desktop application designed for professional photographers and digital artists. It combines traditional high-fidelity image processing with state-of-the-art AI models to provide a workflow comparable to Adobe Lightroom Classic, but with the power of modern AI automation.

---

## 🚀 Key Features

- **Museum-Quality Processing**: Advanced tone mapping, histogram management, and multi-scale sharpening.
- **AI Copilot**: An integrated AI assistant that analyzes your photos and suggests/executes edits using vision-based reasoning.
- **Hybrid AI Pipeline**:
  - **Local Inference**: Background removal (ONNX), Portrait retouching, and Noise reduction.
  - **Vision Intelligence**: Connected to NVIDIA Nemotron models via OpenRouter for complex image analysis.
- **Professional Tools**:
  - Multi-channel Tone Curves.
  - Live Histogram analysis.
  - 14+ Professional Filter Presets (Film Simulations & Color Grades).
- **Privacy First**: Process images locally without mandatory cloud uploads.

---

## 🏗️ System Architecture

The following diagram illustrates the hybrid pipeline that powers the editor:

```mermaid
graph TD
    A[User Interface / Editor Canvas] --> B{AI Coordinator}
    
    subgraph "Hybrid AI Pipeline"
        B --> C[Local Image Processing Engine]
        B --> D[Local Machine Learning Inference]
        B --> E[Cloud AI Copilot]
    end

    subgraph "Local Image Processing (OpenCV / C++)"
        C --> C1[AccentAI: Histogram & Tone Mapping]
        C --> C2[SkyAI: Semantic Detection & fBm Clouds]
        C --> C3[NoiselessAI: fastNlMeans & Guided Filters]
        C --> C4[SupersharpAI: Multi-Scale Unsharp Mask]
        C --> C5[EraseAI: Navier-Stokes Inpainting]
    end

    subgraph "Local ML Inference (ONNX / HuggingFace / PyTorch)"
        D --> D1[BackgroundAI: rembg / u2net ONNX]
        D --> D2[RelightAI: HF Depth Anything v2]
        D --> D3[PortraitAI: MediaPipe Face Mesh / Haar]
    end

    subgraph "Cloud Assistant (OpenRouter API)"
        E --> E1[Vision Model: NVIDIA Nemotron-3-Nano]
        E --> E2[Text Fallback: Llama 3 / Ring-2.6]
        E1 --> E3[Command Parser]
        E2 --> E3
        E3 -->|"[EXECUTE: tool, val]"| A
    end
```

---

## 🛠️ Technology Stack

- **Frontend**: Python with Qt (PyQt6/PySide6) for a native, responsive desktop experience.
- **Image Processing**: OpenCV, NumPy, and Scipy for low-latency operations.
- **AI/ML**: ONNX Runtime, HuggingFace Transformers, and OpenRouter API integration.
- **UI Design**: Modern "Glassmorphism" theme with dynamic micro-animations.

---

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/shreyansh-programmer/AI-Photo-Editor-Pro.git
   cd AI-Photo-Editor-Pro
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

---

## 🤝 Selling / License Note
This project is architected for scalability. The modular engine design allows for easy integration of new AI models and custom filters.

---
*Created by [shreyansh-programmer](https://github.com/shreyansh-programmer)*
