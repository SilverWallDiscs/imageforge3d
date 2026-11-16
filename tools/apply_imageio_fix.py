from __future__ import annotations

import sys
from pathlib import Path


IMAGEIO_VERSION = "2.38.2"


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    if new in source:
        return
    if old not in source:
        raise RuntimeError(f"No se encontro el texto esperado en {path.name}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python apply_imageio_fix.py <carpeta-imageforge3d>")
        return 2

    root = Path(sys.argv[1]).resolve()
    required = ["app.py", "setup.bat", "requirements-ui.txt", "requirements-engine.txt"]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise SystemExit(f"Carpeta ImageForge invalida; faltan: {', '.join(missing)}")

    ui = root / "requirements-ui.txt"
    ui_text = ui.read_text(encoding="utf-8")
    if f"imageio=={IMAGEIO_VERSION}" not in ui_text:
        ui.write_text(ui_text.rstrip() + f"\nimageio=={IMAGEIO_VERSION}\n", encoding="utf-8")

    engine = root / "requirements-engine.txt"
    engine_text = engine.read_text(encoding="utf-8")
    engine_lines = []
    found_imageio = False
    for line in engine_text.splitlines():
        if line.strip().lower().startswith("imageio"):
            if not found_imageio:
                engine_lines.append(f"imageio[ffmpeg]=={IMAGEIO_VERSION}")
                found_imageio = True
        else:
            engine_lines.append(line)
    if not found_imageio:
        engine_lines.append(f"imageio[ffmpeg]=={IMAGEIO_VERSION}")
    engine.write_text("\n".join(engine_lines).rstrip() + "\n", encoding="utf-8")

    replace_once(
        root / "setup.bat",
        '"%PY%" -m pip install -r requirements-engine.txt\n'
        'if errorlevel 1 goto :fail\n'
        '"%PY%" repair_triposr_mesh.py',
        '"%PY%" -m pip install -r requirements-engine.txt\n'
        'if errorlevel 1 goto :fail\n'
        '"%PY%" -c "import imageio; print(\'ImageIO \' + imageio.__version__ + \' listo.\')"\n'
        'if errorlevel 1 (\n'
        '  echo [ERROR] ImageIO no se pudo importar. Reintentando instalacion...\n'
        '  "%PY%" -m pip install --force-reinstall "imageio==2.38.2"\n'
        '  if errorlevel 1 goto :fail\n'
        '  "%PY%" -c "import imageio; print(imageio.__version__)"\n'
        '  if errorlevel 1 goto :fail\n'
        ')\n'
        '"%PY%" repair_triposr_mesh.py',
    )

    smoke = root / "tests" / "smoke_test.py"
    replace_once(
        smoke,
        "def main() -> int:\n    env = os.environ.copy()",
        "def main() -> int:\n"
        "    try:\n"
        "        import imageio\n"
        "        print(f\"[OK] ImageIO {imageio.__version__} esta instalado.\")\n"
        "    except Exception as exc:\n"
        "        raise RuntimeError(f\"Falta la dependencia del motor ImageIO: {exc}\") from exc\n"
        "\n"
        "    env = os.environ.copy()",
    )

    replace_once(
        root / "patch_gradio_client.py",
        '        from gradio_client.utils import _json_schema_to_python_type\n'
        '        assert _json_schema_to_python_type(True, None) == "Any"\n'
        '        assert _json_schema_to_python_type(False, None) == "None"',
        '        import importlib\n'
        '        import gradio_client.utils as utils\n'
        '        utils = importlib.reload(utils)\n'
        '        assert utils._json_schema_to_python_type(True, None) == "Any"\n'
        '        assert utils._json_schema_to_python_type(False, None) == "None"',
    )

    replace_once(
        root / "app.py",
        '        if "torchmcubes" in detail.lower() or "mcubes" in detail.lower():\n',
        '        if "no module named \'imageio\'" in detail.lower():\n'
        '            detail += "\\n\\nFalta una dependencia del motor. Actualiza ImageIO ejecutando: '
        '.venv\\\\Scripts\\\\python.exe -m pip install --force-reinstall imageio==2.38.2"\n'
        '        elif "torchmcubes" in detail.lower() or "mcubes" in detail.lower():\n',
    )

    app = root / "app.py"
    app_text = app.read_text(encoding="utf-8")
    app_text = app_text.replace('<span class="pill">V 0.1.2</span>', '<span class="pill">V 0.1.4</span>')
    app.write_text(app_text, encoding="utf-8")

    version_file = root / "VERSION.txt"
    version_file.write_text(
        f"ImageForge 3D v0.1.4\nImageIO {IMAGEIO_VERSION} is a required runtime dependency.\n",
        encoding="utf-8",
    )

    # Validate the package metadata and source-level smoke test before CI proceeds.
    assert f"imageio=={IMAGEIO_VERSION}" in ui.read_text(encoding="utf-8")
    assert f"imageio[ffmpeg]=={IMAGEIO_VERSION}" in engine.read_text(encoding="utf-8")
    assert "import imageio" in smoke.read_text(encoding="utf-8")
    print(f"[OK] ImageForge actualizado a v0.1.4; ImageIO {IMAGEIO_VERSION} incluido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
