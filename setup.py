from setuptools import setup, find_packages

setup(
    name="hfqco", # これがパッケージ名になります～
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "matplotlib",
        "numpy",
        "scipy",
        "tqdm"
    ],
    author="tanetakumi",
    description="Optimizer of half flux quantum circuits composed of π-shift and conventional Josephson junctions",
    url="https://github.com/tanetakumi/hfqco",
    python_requires='>=3.8',
)

