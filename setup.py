from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="geointel",
    version="0.1.12",
    packages=find_packages(exclude=["tests", "examples"]),
    include_package_data=True,
    package_data={
        "geointel": ["../geointel_ui_template/*"],
    },
    install_requires=[
        "requests>=2.31.0",
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
    ],
    extras_require={
        "web": [
            "flask>=2.3.0",
            "flask-cors>=4.0.0",
        ],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "geointel=geointel.cli:main",
        ],
    },
    author="Atilla",
    author_email="atilla@tuta.io",
    description="AI-powered geolocation analysis using Google Gemini 2.5 Flash",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atiilla/geointel",
    project_urls={
        "Bug Reports": "https://github.com/atiilla/geointel/issues",
        "Source": "https://github.com/atiilla/geointel",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    keywords="geolocation, ai, gemini, image-analysis, computer-vision, osint",
)
