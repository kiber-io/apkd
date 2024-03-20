# APK Downloader

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/your-username/apk-downloader/blob/main/LICENSE)

## Description

APK Downloader is a tool that allows you to easily download APK files from popular app stores. With this tool, you can quickly obtain APK files for various Android applications directly to your local machine.

## Supported app stores
- [ApkPure](https://apkpure.com/)
- [ApkCombo](https://apkcombo.com/)
- [RuStore](https://rustore.ru/)
- [RuMarket](https://ruplay.market/)
- [F-Droid](https://f-droid.org/)
- [AppGallery](https://appgallery.huawei.com/) (in progress)

## Features

- Support for multiple sources
- Automatic search for all sources
- Simple and intuitive command-line interface
- Modularity and extensibility. PR is welcome
- ???

## Installation

1. Clone the repository:

    ```shell
    git clone https://github.com/your-username/apk-downloader.git
    ```

2. Run command:

    ```shell
    pip install .
    ```

3. Use command apkd from anywhere

## Usage

To download an APK file, run the following command:
```shell
apkd -p ru.rostel -d
```
To list available versions:
```shell
apkd -p ru.rostel -lv
```
To choose source:
```shell
apkd -p ru.rostel -d -s rustore
```
To download certain version:
```shell
apkd -p ru.rostel -d -vc 5979
```