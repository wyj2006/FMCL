# Functional Minecraft Launcher

![Downloads](https://img.shields.io/github/downloads/wyj2006/FMCL/total)
![Stars](https://img.shields.io/github/stars/wyj2006/FMCL)
![CodeSize](https://img.shields.io/github/languages/code-size/wyj2006/FMCL)
![MadeBy](https://img.shields.io/badge/Made%20By-YongjianWang-green.svg)

[English](README_en.md) | 中文

## 介绍

FMCL (Functional Minecraft Launcher) 是一个MC启动器

## 构建

目前只支持Windows系统, 需要C编译器支持C23标准

1. 准备

    ```shell
    cd scripts
    python decompress.py
    ```

2. 构建

    ```shell
    mkdir build
    cd build
    cmake ..
    make
    ```
