import sys
import os
import subprocess
import importlib

# No Linux, o SDL2 precisa do backend evdev para detectar controles modernos
# (Xbox One/Series, PS4/PS5) que aparecem como /dev/input/event* e não /dev/input/js*
# O Firefox usa evdev diretamente — aqui forçamos o SDL2 a fazer o mesmo.
if sys.platform.startswith("linux"):
    os.environ.setdefault("SDL_JOYSTICK_LINUX_EVDEV", "1")

REQUIRED_PYTHON = (3, 12)
REQUIRED_PACKAGES = [
    "pygame-ce",
    "supabase"
]


def check_python():
    if sys.version_info < REQUIRED_PYTHON:
        print("Python 3.12 ou superior é necessário.")
        print(f"Versão atual: {sys.version}")
        sys.exit(1)


def install_package(package):
    print(f"Instalando dependência: {package}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def check_dependencies():
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package.replace("-", "_"))
        except ImportError:
            install_package(package)


def bootstrap():
    check_python()
    check_dependencies()


def main():
    bootstrap()

    from game.app import run
    run()


if __name__ == "__main__":
    main()
