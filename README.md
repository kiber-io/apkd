# APK Downloader

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/your-username/apk-downloader/blob/main/LICENSE)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-Repository-blue?logo=docker)](https://hub.docker.com/r/kiber1o/apkd)

```shell
# find the versions...
$ apkd -p com.twitter.android -lv
+---------------------+---------+-------------------+--------------+-------------+-----------+
| Package             | Source  | Version name      | Version code | Update date | Size      |
+---------------------+---------+-------------------+--------------+-------------+-----------+
| com.twitter.android | ApkPure | 10.49.0-release.0 | 310490000    | 10.07.2024  | 120.61 MB |
| com.twitter.android | ApkPure | 10.48.0-release.0 | 310480000    | 03.07.2024  | 115.43 MB |
| com.twitter.android | ApkPure | 10.47.0-release.0 | 310470000    | 26.06.2024  | 115.55 MB |
+---------------------+---------+-------------------+--------------+-------------+-----------+

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

`Developer ID` - support for downloading of all applications from a single developer

| Store                                       | Multiple versions  |    Update date     | Developer ID |
|---------------------------------------------|:------------------:|:------------------:| - |
| [F-Droid](https://f-droid.org)              | :heavy_check_mark: | :heavy_check_mark: |:x:
| [ApkPure](https://apkpure.com)              | :heavy_check_mark: | :heavy_check_mark: |:heavy_check_mark:
| [ApkCombo](https://apkcombo.com)            | :heavy_check_mark: |        :x:         |:heavy_check_mark:
| [AppGallery](https://appgallery.huawei.com) |        :x:         |        :x:         |:x:
| [RuStore](https://rustore.ru)               |        :x:         | :heavy_check_mark: |:heavy_check_mark:
| [RuMarket](https://ruplay.market)           |        :x:         | :heavy_check_mark: |:x:
| [NashStore](https://nashstore.ru)           |        :x:         | :heavy_check_mark: |:x:

## Features

- Support for multiple sources
- Automatic search across all sources
- Batch downloading support
    - Batch downloading of all applications from a single developer
- Simple and intuitive command-line interface
- Modularity and extensibility; PRs are welcome
- Active support and development
- ???

## Installation
### Stable version
```shell
pip install git+https://github.com/kiber-io/apkd
```
### Beta version
```shell
pip install git+https://github.com/kiber-io/apkd@beta
```

And use command "apkd" anywhere!

### Docker
```shell
docker run kiber1o/apkd --version

docker run kiber1o/apkd:beta --version # for beta version
```

## Use cases
### Simple download
```shell
$ apkd -p com.instagram.android -d [[-s SOURCE] [-vc <VERSION_CODE>]]
```
### List available versions
```shell
$ apkd -p com.instagram.android -lv [-s SOURCE]
```
### Batch download
```shell
$ cat packages.txt
com.instagram.android
com.twitter.android
com.facebook.katana==454214928

$ apkd -l packages.txt -d
```
### Batch download of all applications from one developer
Due to the fact that different stores store the developer's name in different formats (or even do not store it at all), there are several restrictions:
- Before downloading, you need to find out the developer ID from a specific store using any package name from that developer
- Simultaneous downloads from different stores are possible only if these stores have the same developer ID (e.g., some IDs match ApkCombo and APKPure)
- This type of download is not available from all stores (the list of supported stores will be updated whenever possible). A list of stores that support this feature can be found in the table at the top of the file

```shell
# Find the developer id in the store you need
$ apkd -ld -p com.instagram.android -s apkpure
+-----------------------+---------+--------------+
| Package               | Source  | Developer ID |
+-----------------------+---------+--------------+
| com.instagram.android | ApkPure | Instagram    |
+-----------------------+---------+--------------+
# [Optional] Check out the list of all packages from this developer
$ apkd -lv -did Instagram -s apkpure
+--------------------------+---------+----------------+--------------+-------------+----------+
| Package                  | Source  | Version name   | Version code | Update date | Size     |
+--------------------------+---------+----------------+--------------+-------------+----------+
| com.instagram.android    | ApkPure | 348.0.0.0.7    | 374800592    | 01.09.2024  | 68.42 MB |
+--------------------------+---------+----------------+--------------+-------------+----------+
| com.instagram.barcelona  | ApkPure | 347.0.0.0.78   | 501706269    | 29.08.2024  | 77.58 MB |
+--------------------------+---------+----------------+--------------+-------------+----------+
# Download all the apps from this developer
$ apkd -d -did Instagram -s apkpure
```

## Dependencies
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) - for easy parsing of html pages
- [tqdm](https://github.com/tqdm/tqdm/) - to visually display the download process
- [requests](https://pypi.org/project/requests/) - for all network requests
- [user-agent](https://pypi.org/project/user-agent/) - to randomize the user-agent
- [prettytable](https://pypi.org/project/prettytable/) - for a beautiful display of the list of versions in the table
- [pypasser](https://pypi.org/project/PyPasser/) - to bypass ReCaptcha at ApkCombo
- [cloudscraper](https://github.com/VeNoMouS/cloudscraper) - to bypass Cloudflare at ApkPure
