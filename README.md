# ImageForge 3D

ImageForge 3D is a local Windows desktop web interface for turning a single image into an editable 3D model with TripoSR. Images and generated files stay on the local machine.

## Windows build

The current package is **v0.1.4**. It targets Windows 10/11 and Python 3.11 x64. An NVIDIA GPU with a recent driver is recommended for model inference; the final marching-cubes mesh extraction uses PyMCubes on the CPU, so a locally installed CUDA Toolkit / `nvcc` is not required.

1. Download the latest successful **ImageForge3D-v0.1.4-Windows** artifact from [GitHub Actions](https://github.com/SilverWallDiscs/imageforge3d/actions/workflows/windows-ci.yml).
2. Extract the ZIP.
3. Run `setup.bat` and let it finish.
4. Run `launch.bat`. The local interface opens at `http://127.0.0.1:7860`.

The first generation downloads the TripoSR weights from Hugging Face and stores them in the local model cache.

## Compatibility fixes

The UI dependencies are pinned to a compatible set for Gradio 4.44.1: FastAPI 0.115.14, Starlette 0.46.2, Jinja2 3.1.6, Gradio Client 1.3.0, and Hugging Face Hub 0.25.2. The installer also applies and verifies the boolean JSON Schema compatibility fix in `gradio_client`.

The v0.1.4 package explicitly installs **ImageIO 2.38.2** in both the UI and engine dependency lists. The installer verifies that `import imageio` works before reporting success, and the Windows CI smoke test checks the same import before it starts Gradio. This fixes generation failures caused by the engine importing ImageIO when it was absent from an already-created virtual environment.

## GitHub Actions

The Windows CI job reconstructs the original Windows package, applies the versioned runtime dependency patch, rebuilds the v0.1.4 ZIP, installs the pinned dependencies, applies the Gradio compatibility patch, runs Python compilation checks, and launches the **actual `app.py`**. It verifies ImageIO imports and checks that both `/` and `/config` return HTTP 200, then publishes the tested ZIP as an Actions artifact.

CI validates the application startup, ImageIO import and web UI. It does not claim to benchmark or run TripoSR inference on an NVIDIA GPU; actual model generation still depends on the local machine, its drivers, and the downloaded model weights.

## Repair an existing installation

Extract the new ZIP over the existing `imageforge3d` folder. Do not delete `.venv`, `engine`, or `outputs`. Open PowerShell in that folder and run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ui.txt
.\.venv\Scripts\python.exe -c "import imageio; print(imageio.__version__)"
```

Then restart ImageForge with `launch.bat`. You do not need to download TripoSR or PyTorch again just to add ImageIO.

## Project folders

- `engine/TripoSR`: downloaded model engine (created by setup).
- `outputs/`: generated models.
- `setup.bat`: Windows installer.
- `launch.bat`: local app launcher.
- `SOLUCION_DE_PROBLEMAS.md`: troubleshooting guide.
