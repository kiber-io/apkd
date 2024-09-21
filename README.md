# APK Downloader

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/your-username/apk-downloader/blob/main/LICENSE)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-Repository-blue?logo=docker)](https://hub.docker.com/r/kiber1o/apkd)

```shell
# find the versions...
$ apkd -p com.instagram.android -lv
+-----------------------+----------+----------------+--------------+-------------+----------+
| Package               | Source   | Version name   | Version code | Update date | Size     |
+-----------------------+----------+----------------+--------------+-------------+----------+
| com.instagram.android | ApkCombo | 343.0.0.33.101 | 374410331    | N/A         | 69.00 MB |
| com.instagram.android | ApkCombo | 343.0.0.33.101 | 374410330    | N/A         | 68.00 MB |
| com.instagram.android | ApkCombo | 343.0.0.33.101 | 374311345    | N/A         | 87.00 MB |
| com.instagram.android | ApkCombo | 343.0.0.33.101 | 374311344    | N/A         | 89.00 MB |
| com.instagram.android | ApkCombo | 343.0.0.33.101 | 374311343    | N/A         | 69.00 MB |
| com.instagram.android | ApkCombo | 343.0.0.33.101 | 374311342    | N/A         | 68.00 MB |
| com.instagram.android | ApkCombo | 343.0.0.33.101 | 374311341    | N/A         | 68.00 MB |
+-----------------------+----------+----------------+--------------+-------------+----------+

# ...and download them (the latest version is downloaded by default)
$ apkd -p com.instagram.android -d -s apkcombo
com.instagram.android ver. 374410331 (ApkCombo):  19%|████            | 13.5M/72.0M [00:01<00:03, 16.2MB/s]

# ...or use batch downloading
$ apkd -l packages.txt -d
com.facebook.katana ver. 454214928 (ApkCombo):  87%|███████████  | 72.1M/82.8M [00:07<00:01, 6.24MB/s]
com.instagram.android ver. 374410331 (ApkCombo):  71%|████████     | 51.0M/72.0M [00:07<00:03, 6.42MB/s]
com.snapchat.android ver. 150472 (ApkCombo):  10%|██          | 15.7M/155M [00:04<00:25, 5.41MB/s]
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
- Support for batch downloading
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
```shell
docker run kiber1o/apkd --version

docker run kiber1o/apkd:beta --version # for beta version
```

## Usage

To download an APK file, run the following command:
```shell
$ apkd -p com.instagram.android -d
```
To list available versions:
```shell
$ apkd -p com.instagram.android -lv
```
To choose source:
```shell
$ apkd -p com.instagram.android -d -s apkpure
```
To download certain version:
```shell
$ apkd -p com.instagram.android -d -vc 310260000
```
For batch download:
```shell
$ cat packages.txt
> com.instagram.android
> com.twitter.android
> com.facebook.katana==454214928

$ apkd -l packages.txt -d
```

## Dependencies
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) - for easy parsing of html pages
- [tqdm](https://github.com/tqdm/tqdm/) - to visually display the download process
- [requests](https://pypi.org/project/requests/) - for all network requests
- [user-agent](https://pypi.org/project/user-agent/) - to randomize the user-agent
- [prettytable](https://pypi.org/project/prettytable/) - for a beautiful display of the list of versions in the table
- [pypasser](https://pypi.org/project/PyPasser/) - to bypass ReCaptcha at ApkCombo
- [cloudscraper](https://github.com/VeNoMouS/cloudscraper) - to bypass Cloudflare at ApkPure
