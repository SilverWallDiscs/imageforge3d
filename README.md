# ImageForge 3D

ImageForge 3D is a local Windows desktop web interface for turning a single image into an editable 3D model with TripoSR. Images and generated files stay on the local machine.

## Windows build

The current package is **v0.1.3**. It targets Windows 10/11 and Python 3.11 x64. An NVIDIA GPU with a recent driver is recommended for model inference; the final marching-cubes mesh extraction uses PyMCubes on the CPU, so a locally installed CUDA Toolkit / `nvcc` is not required.

1. Download the latest successful **ImageForge3D-v0.1.3-Windows** artifact from [GitHub Actions](https://github.com/SilverWallDiscs/imageforge3d/actions/workflows/windows-ci.yml).
2. Extract the ZIP.
3. Run `setup.bat` and let it finish.
4. Run `launch.bat`. The local interface opens at `http://127.0.0.1:7860`.

The first generation downloads the TripoSR weights from Hugging Face and stores them in the local model cache.

## Compatibility fixes in v0.1.3

The UI dependencies are pinned to a compatible set for Gradio 4.44.1: FastAPI 0.115.14, Starlette 0.46.2, Jinja2 3.1.6, Gradio Client 1.3.0, and Hugging Face Hub 0.25.2. The installer also applies and verifies the boolean JSON Schema compatibility fix in `gradio_client`.

This avoids the Starlette 1.x `TemplateResponse` signature mismatch that caused the local page to return HTTP 500, and prevents newer Hugging Face Hub versions from removing the legacy `HfFolder` symbol expected by this Gradio release.

## GitHub Actions

The Windows CI job reconstructs the Windows ZIP, extracts it, installs the pinned UI dependencies, applies the compatibility patch, runs Python compilation checks, and launches the **actual `app.py`**. It checks that both `/` and `/config` return HTTP 200, then publishes the tested ZIP as an Actions artifact.

CI validates application startup and the web UI. It does not claim to benchmark or run TripoSR inference on an NVIDIA GPU; actual model generation still depends on the local machine, its drivers, and the downloaded model weights.

## Project folders

- `engine/TripoSR`: downloaded model engine (created by setup).
- `outputs/`: generated models.
- `setup.bat`: Windows installer.
- `launch.bat`: local app launcher.
- `SOLUCION_DE_PROBLEMAS.md`: troubleshooting guide.
