# Functional Minecraft Launcher

![Downloads](https://img.shields.io/github/downloads/wyj2006/FMCL/total)
![Stars](https://img.shields.io/github/stars/wyj2006/FMCL)
![CodeSize](https://img.shields.io/github/languages/code-size/wyj2006/FMCL)
![MadeBy](https://img.shields.io/badge/Made%20By-YongjianWang-green.svg)

[English](README_en.md) | 中文

## 介绍

FMCL (Functional Minecraft Launcher) 是一个Minecraft启动器

## 运行

FMCL的功能依赖python运行环境，所以请先安装python，推荐安装3.14.x版本，安装好python后还需要安装好`requirements.txt`中的依赖，再运行。

## 构建

先运行以下指令生成必要的文件

```cmd
cd scripts
python generate_ui.py
python generate_qm.py
cd ..
cd resources
python build.py
```

然后`cargo run`即可(需要`Rust`环境)
