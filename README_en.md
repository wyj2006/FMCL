# Functional Minecraft Launcher

![Downloads](https://img.shields.io/github/downloads/wyj2006/FMCL/total)
![Stars](https://img.shields.io/github/stars/wyj2006/FMCL)
![CodeSize](https://img.shields.io/github/languages/code-size/wyj2006/FMCL)
![MadeBy](https://img.shields.io/badge/Made%20By-YongjianWang-green.svg)

English | [中文](README.md)

## Introduction

FMCL (Functional Minecraft Launcher) is a Minecraft Launcher.

## Run

FMCL requires a Python runtime environment. Please install Python first (Python 3.14.x is recommended). After installing Python, you also need to install the dependencies listed in `requirements.txt` before running the application.

## Build

First, run the following commands to generate necessary files:

```cmd
cd scripts
python generate_ui.py
python generate_qm.py
cd ..
cd resources
python build.py
```

Then simply run `cargo run` (a `Rust` environment is required).
