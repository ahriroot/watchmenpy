from setuptools import setup
from setuptools import find_packages
from watchmen import VERSION

with open("README_EN.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="watchmenpy",
    version=VERSION,
    author="ahriknow",
    author_email="ahriknow@ahriknow.com",
    description="Watchmen is a daemon process manager that for you manage and keep your application online 24/7",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "watchmen=watchmen.main:main",
            "watchmend=watchmend.main:main",
        ],
    },
    install_requires=[
        "toml~=0.10.0",
        "pydantic~=2.1.0"
    ],
    extras_require={
        "redis": ["redis >= 4.5.0, < 5.0"],
    },
    python_requires=">=3.5",
)
