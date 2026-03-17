import pkgutil
from pathlib import Path


def load_all_models() -> None:
    package_dir = Path(__file__).resolve().parent
    modules = pkgutil.walk_packages(
        path=[str(package_dir)], prefix='src.infrastructure.database.'
    )

    for module in modules:
        __import__(module.name)
