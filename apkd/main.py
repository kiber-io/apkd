import argparse
import os
import sys
from importlib import util as importutil
from typing import Optional

from apkd.utils import App, AppNotFoundError, AppVersion, BaseSource
from prettytable import PrettyTable


class Utils:
    @staticmethod
    def get_available_sources_names():
        sources_path = os.path.join(os.path.dirname(__file__), 'sources')
        sources_names = []
        for file in os.listdir(sources_path):
            filename, fileext = os.path.splitext(file)
            if fileext != '.py':
                continue
            sources_names.append(filename)

        return sources_names

    @staticmethod
    def import_sources(sources_names: Optional[list[str]] = None) -> dict[str, BaseSource]:
        if sources_names is None:
            sources_names = Utils.get_available_sources_names()

        sources_path = os.path.join(os.path.dirname(__file__), 'sources')

        sources = {}
        for source_name in sources_names:
            source_file = os.path.join(sources_path, f'{source_name}.py')
            if not os.path.exists(source_file):
                raise SourceImportError(f'Source "{source_name}" not found')
            spec = importutil.spec_from_file_location(source_name, source_file)
            if spec is None:
                raise SourceImportError()
            module = importutil.module_from_spec(spec)
            if spec.loader is None:
                raise SourceImportError()
            spec.loader.exec_module(module)
            sources[source_name] = module.Source()

        return sources

class Apkd:
    __sources: dict[str, BaseSource]

    def __init__(self, auto_load_sources: bool = True):
        self.__sources = {}
        if auto_load_sources:
            self.__load_sources()

    def add_source(self, source_name: str, source: BaseSource):
        self.__sources[source_name] = source

    def remove_source(self, source_name: str):
        if source_name in self.__sources:
            del self.__sources[source_name]

    def clear_sources(self):
        self.__sources.clear()

    def get_sources(self):
        return self.__sources.copy()

    def __load_sources(self):
        sources = Utils.import_sources()
        self.__sources = sources

    def get_app_info(self, package_name: str) -> tuple[list[App], AppVersion]:
        apps: list[App] = []

        source: BaseSource
        for source in self.__sources.values():
            app: App
            try:
                app = source.get_app_info(package_name)
            except AppNotFoundError:
                continue
            apps.append(app)

        if len(apps) == 0:
            raise AppNotFoundError(f'{package_name} not found')

        newest_version: Optional[AppVersion] = None
        for app in apps:
            if newest_version is not None and newest_version.code >= app.get_version_by_idx(0).code:
                continue
            newest_version = app.get_version_by_idx(0)

        if newest_version is None:
            raise AppNotFoundError(f'{package_name} not found')

        return apps, newest_version

    def download_app(self, package_name: str, version_code: int = -1, output_file: Optional[str] = None) -> None:
        apps, newest_version = self.get_app_info(package_name)
        if version_code != -1:
            downloaded = False
            for app in apps:
                try:
                    version = app.get_version_by_code(version_code)
                    version.source.download_app(app.package, version, output_file)
                    downloaded = True
                    break
                except StopIteration:
                    continue
            if not downloaded:
                raise AppNotFoundError(f'Version {version_code} not found')
        else:
            newest_version.source.download_app(package_name, newest_version, output_file)

class SourceImportError(ImportError):
    pass

class SourceNotFoundError(FileNotFoundError):
    pass

def cli():
    apkd = Apkd(auto_load_sources=False)
    sources_names = Utils.get_available_sources_names()

    parser = argparse.ArgumentParser('apkd')
    parser.add_argument('--package', '-p', help='Package name', required=True)
    parser.add_argument('--version-code', '-vc', help='Version code', type=int)
    parser.add_argument('--download', '-d', help='Download', action='store_true')
    parser.add_argument('--list-versions', '-lv', help='List available versions', action='store_true')
    parser.add_argument('--source', '-s', help='Source', nargs='+', default=sources_names, choices=sources_names)
    parser.add_argument('--output', '-o', help='Output file')
    args = parser.parse_args(sys.argv[1:])

    if args.list_versions and args.download:
        parser.error('--list-versions and --download cannot be used together')

    if not args.list_versions and not args.download:
        parser.error('At least one of --list-versions and --download is required')

    if not args.download and args.version_code:
        parser.error('--version-code can only be used with --download')

    sources = Utils.import_sources(args.source)
    for source_name, source in sources.items():
        apkd.add_source(source_name, source)

    if args.list_versions:
        try:
            apps, newest_version = apkd.get_app_info(args.package)
        except AppNotFoundError as e:
            print(e)
            exit(1)
        print(
            f'Newest version: {newest_version.name} ({newest_version.code}) from {newest_version.source.name}')
        print('')

        for app in apps:
            print(app.source.name)
            table = PrettyTable(field_names=['Version name', 'Version code', 'Update date', 'Size'], align='l')
            version: AppVersion
            for version in app.get_versions():
                size_mb = version.size / (1024 * 1024)
                table.add_row([version.name, version.code, version.update_date or 'N/A', f'{size_mb:.2f} MB'])
            print(table)
            print('')

    if args.download:
        apkd.download_app(args.package, args.version_code if args.version_code is not None else -1, args.output)