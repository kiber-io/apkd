# APK Downloader

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/your-username/apk-downloader/blob/main/LICENSE)

```
> apkd -p com.twitter.android -lv
Newest version: 10.34.0-release.0 (310340000) from ApkCombo

ApkCombo
+-------------------+--------------+-------------+-----------+
| Version name      | Version code | Update date | Size      |
+-------------------+--------------+-------------+-----------+
| 10.34.0-release.0 | 310340000    | N/A         | 116.00 MB |
+-------------------+--------------+-------------+-----------+

ApkPure
+-------------------+--------------+-------------+-----------+
| Version name      | Version code | Update date | Size      |
+-------------------+--------------+-------------+-----------+
| 10.34.0-release.0 | 310340000    | 27.03.2024  | 115.82 MB |
| 10.33.0-release.0 | 310330000    | 20.03.2024  | 115.82 MB |
| 10.32.0-release.1 | 310320001    | 13.03.2024  | 115.76 MB |
+-------------------+--------------+-------------+-----------+
```

```
> apkd -p com.twitter.android -d -s apkcombo
ApkCombo: com.twitter.android (310340000) |####################################        |  13.5 MiB/s
```

## Description

APK Downloader is a tool that allows you to easily download APK files from popular app stores. With this tool, you can quickly obtain APK files for various Android applications directly to your local machine.

## Supported app stores
`Multiple versions` - support for downloading different versions of the application (key `-lv`)

`Update date` - support for getting the app update date

| Store                                       | Multiple versions  |    Update date     |
|---------------------------------------------|:------------------:|:------------------:|
| [F-Droid](https://f-droid.org)              | :heavy_check_mark: | :heavy_check_mark: |
| [ApkPure](https://apkpure.com)              | :heavy_check_mark: | :heavy_check_mark: |
| [ApkCombo](https://apkcombo.com)            | :heavy_check_mark: |        :x:         |
| [AppGallery](https://appgallery.huawei.com) |        :x:         |        :x:         |
| [RuStore](https://rustore.ru)               |        :x:         | :heavy_check_mark: |
| [RuMarket](https://ruplay.market)           |        :x:         | :heavy_check_mark: |
| [NashStore](https://nashstore.ru)           |        :x:         | :heavy_check_mark: |

## Features

- Support for multiple sources
- Automatic search for all sources
- Simple and intuitive command-line interface
- Modularity and extensibility. PR is welcome
- Active support and development
- ???

## Installation
```shell
pip install git+https://github.com/kiber-io/apkd
```

... and use command "apkd" anywhere!

### Docker
1. Install Docker (https://docs.docker.com/get-docker/).
2. Build Docker image
```bash
git clone https://github.com/kiber-io/apkd.git
cd apkd
docker build --tag apkd:1.0 .
```
3. Run
```shell
# on linux
docker run --rm -v ${PWD}:/usr/src/app apkd:1.0 --help

# on windows
docker run --rm -v "%cd%":/usr/src/app apkd:1.0 --help
```

## Usage

To download an APK file, run the following command:
```shell
apkd -p com.twitter.android -d
```
To list available versions:
```shell
apkd -p com.twitter.android -lv
```
To choose source:
```shell
apkd -p com.twitter.android -d -s apkpure
```
To download certain version:
```shell
apkd -p com.twitter.android -d -vc 310260000
```

## Dependencies
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) - for easy parsing of html pages of some stores
- [progressbar2](https://pypi.org/project/progressbar2/) - to visually display the download process
- [requests](https://pypi.org/project/requests/) - for all network requests
- [user-agent](https://pypi.org/project/user-agent/) - to hide and randomize the user-agent
- [prettytable](https://pypi.org/project/prettytable/) - for a beautiful display of the list of versions in the table
- [pypasser](https://pypi.org/project/PyPasser/) - to bypass ReCaptcha at the ApkCombo
