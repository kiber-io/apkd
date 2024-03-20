import argparse
import sys
from typing import Optional

from sources.apkcombo import ApkCombo
from sources.apkpure import ApkPure
from sources.base import App, AppNotFoundError, AppVersion, BaseSource
from sources.fdroid import FDroid
from sources.rumarket import RuMarket
from sources.rustore import RuStore

parser = argparse.ArgumentParser('apkd')
parser.add_argument('--package', '-p', help='Package name', required=True)
parser.add_argument('--version-code', '-vc', help='Version code')
parser.add_argument('--download', '-d', help='Download', action='store_true')
parser.add_argument('--list-versions', '-lv',
                    help='List available versions', action='store_true')
parser.add_argument('--source', '-s', help='Source', nargs='+', default=[
                    'apkpure', 'apkcombo', 'rustore', 'rumarket', 'fdroid'], choices=['apkpure', 'apkcombo', 'rustore', 'rumarket', 'fdroid'])

args = parser.parse_args(sys.argv[1:])

if args.list_versions and args.download:
    parser.error('Cannot use --list-versions and --download at the same time')

if not args.list_versions and not args.download:
    parser.error('At least one of --list-versions and --download is required')

if not args.download and args.version_code:
    parser.error('--version-code can only be used with --download')

sources: list[BaseSource] = []
for source_name in args.source:
    match source_name:
        case 'apkpure':
            sources.append(ApkPure())
        case 'apkcombo':
            sources.append(ApkCombo())
        case 'rustore':
            sources.append(RuStore())
        case 'rumarket':
            sources.append(RuMarket())
        case 'fdroid':
            sources.append(FDroid())
        case _:
            raise TypeError(f'Invalid source: {source_name}')

apps: list[App] = []

source: BaseSource
for source in sources:
    app: App
    try:
        app = source.get_app_info(args.package)
    except AppNotFoundError:
        continue
    apps.append(app)

if len(apps) == 0:
    print(f'{args.package} not found')
    exit(1)

newest_version: Optional[AppVersion] = None
for app in apps:
    if newest_version is not None and newest_version.code >= app.get_version_by_idx(0).code:
        continue
    newest_version = app.get_version_by_idx(0)

if newest_version is None:
    print(f'{args.package} not found')
    exit(1)

if args.list_versions:
    print(
        f'Newest version: {newest_version.name} ({newest_version.code}) from {newest_version.source.name}')
    print('')

    for app in apps:
        print(
            f'Available versions for "{args.package}" from {app.source.name}:')
        version: AppVersion
        for version in app.get_versions():
            size_mb = version.size / (1024 * 1024)
            print(
                f'    {version.name} ({version.code}) | {version.update_date} | {size_mb:.2f} MB')
        print('')
elif args.download:
    if args.version_code:
        downloaded = False
        for app in apps:
            try:
                version = app.get_version_by_code(int(args.version_code))
                print(
                    f'Downloading "{app.package}" ({version.code}) from {version.source.name}')
                version.source.download_app(app.package, version)
                downloaded = True
                break
            except StopIteration:
                continue
        if not downloaded:
            print(f'Version {args.version_code} not found')
    else:
        print(
            f'Downloading "{args.package}" ({newest_version.code}) from {newest_version.source.name}')
        newest_version.source.download_app(args.package, newest_version)