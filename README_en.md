# Functional Minecraft Launcher

![Downloads](https://img.shields.io/github/downloads/wyj2006/FMCL/total)
![Stars](https://img.shields.io/github/stars/wyj2006/FMCL)
![CodeSize](https://img.shields.io/github/languages/code-size/wyj2006/FMCL)
![MadeBy](https://img.shields.io/badge/Made%20By-YongjianWang-green.svg)

English | [中文](README.md)

## Introduction

FMCL (Functional Minecraft Launcher) is a Minecraft Launcher.

## Build

Currently only Windows systems are supported, and a C compiler supporting the C23 standard is required.

1. Prepare

    ```shell
    cd scripts
    python decompress.py
    ```

2. Build

    ```shell
    mkdir build
    cd build
    cmake ..
    make
    ```
