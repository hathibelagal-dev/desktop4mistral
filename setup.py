from setuptools import setup, find_packages

long_description = ""
with open("README.md", "r", encoding="utf-8") as f:
    contents = f.readlines()
    for line in contents:
        if "user-attachments/assets" not in line:
            long_description += line

setup(
    name="desktop4mistral",
    version="0.1.0",
    author="Ashraff Hathibelagal",
    description="A powerful desktop client for Mistral LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hathibelagal-dev/desktop4mistral",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "PySide6",
        "requests",
        "markdown",
        "wikipedia",
        "markdownify",
        "git2string",
        "str2speech>=0.3.0",
        "sounddevice",
        "scipy",
    ],
    include_package_data=True,
    package_data={
        "desktop4mistral": ["fonts/*.ttf"],
    },
    entry_points={
        "console_scripts": [
            "desktop4mistral=desktop4mistral.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ai text-to-speech speech-synthesis nlp transformer voice",
    project_urls={
        "Source": "https://github.com/hathibelagal-dev/desktop4mistral",
        "Tracker": "https://github.com/hathibelagal-dev/desktop4mistral/issues",
    },
)
