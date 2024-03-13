import argparse
import sys

from apkpure import ApkPure
from apkcombo import ApkCombo

parser = argparse.ArgumentParser('apkd')
parser.add_argument('--package', '-p', help='Package name', required=True)
parser.add_argument('--version', '-v', help='Version code')
parser.add_argument('--download', '-d', help='Download', action='store_true')
parser.add_argument('--list-versions', '-lv', help='List available versions', action='store_true')
parser.add_argument('--source', '-s', help='Source', nargs='+', default=['apkpure', 'apkcombo'], choices=['apkpure', 'apkcombo'])

args = parser.parse_args(sys.argv[1:])

if args.list_versions and args.download:
    parser.error('Cannot use --list-versions and --download at the same time')

sources = []
for source in args.source:
    match source:
        case 'apkpure':
            sources.append(ApkPure())
        case 'apkcombo':
            sources.append(ApkCombo())
        case _:
            raise TypeError(f'Invalid source: {source}')

apps = []

for source in sources:
    app: dict
    try:
        app = source.search_app(args.package)
    except FileNotFoundError:
        continue
    apps.append({
        'app': app,
        'source': source
    })

if len(apps) == 0:
    print(f'{args.package} not found')
    exit(1)

newest_version = None
for info in apps:
    app = info['app']
    versions = sorted(app['versions'], key=lambda x: x['version_code'], reverse=True)
    if newest_version is not None and newest_version['version']['version_code'] >= versions[0]['version_code']:
        continue
    newest_version = {
        'source': info['source'],
        'version': versions[0]
    }

if newest_version is None:
    print(f'{args.package} not found')
    exit(1)

if args.list_versions:
    print(f'Newest version: {newest_version["version"]["version"]} ({newest_version["version"]["version_code"]}) from {newest_version["source"].source_name}')
    print('')

    for info in apps:
        print(f'Available versions for "{args.package}" from {info["source"].source_name}:')
        for version in info['app']['versions']:
            size_mb = version['file_size'] / (1024 * 1024)
            print(f'    {version["version"]} ({version["version_code"]}) | {version["update_date"]} | {size_mb:.2f} MB')
        print('')
elif args.download:
    if args.version:
        for info in apps:
            app = info['app']
            source = info['source']
            try:
                version = next((v for v in app['versions'] if v['version_code'] == args.version))
                print(f'Downloading "{args.package}" ({version["version_code"]}) from {source.source_name}')
                source.download_app(args.package, version)
                break
            except StopIteration:
                continue
    else:
        print(f'Downloading "{args.package}" ({newest_version["version"]["version_code"]}) from {newest_version["source"].source_name}')
        file = newest_version['source'].download_app(args.package, newest_version['version'])

    # if args.download:
    #     if args.version:
    #         try:
    #             version = next((v for v in app['versions'] if v['version_code'] == args.version))
    #         except StopIteration:
    #             continue
    #     else:
    #         version = app['versions'][0]

    #     print(f'Downloading "{args.package}" ({version["version_code"]}) from {source.source_name}')
    #     file = source.download_app(args.package, version)
    #     break
    # elif args.list_versions:
        # print(f'Available versions for "{args.package}" from {source.source_name}:')
        # for version in app['versions']:
        #     size_mb = version['file_size'] / (1024 * 1024)
        #     print(f'    {version["version"]} ({version["version_code"]}) | {version["update_date"]} | {size_mb:.2f} MB')