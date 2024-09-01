import argparse
import logging
import os
import sys
from functools import cmp_to_key
from importlib import util as importutil
from queue import Empty as QueueEmpty
from queue import Queue
from threading import Lock, Thread
from typing import Callable, Optional

from prettytable import PrettyTable
from tqdm import tqdm

from apkd.utils import (App, AppNotFoundError, AppVersion, BaseSource,
                        DeveloperNotFoundError, get_logger)

VERSION = '1.1.2'


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

    @staticmethod
    def find_last_version(apps: list[App]) -> AppVersion|None:
        last_version: AppVersion|None = None
        for app in apps:
            if last_version is not None and last_version.code >= app.get_versions()[0].code:
                continue
            last_version = app.get_versions()[0]

        return last_version

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

    def get_app_info(self, package_name: str, versions_limit: int = -1) -> list[App]:
        apps: list[App] = list()

        for source in self.__sources.values():
            try:
                app = source.get_app_info(package_name, versions_limit)
            except AppNotFoundError:
                continue
            apps.append(app)

        if len(apps) == 0:
            raise AppNotFoundError(f'{package_name} not found')

        return apps

    def download_app(self, package_name: str, version_code: int = -1, output_file: Optional[str] = None, on_download_start: Callable[[AppVersion, int], None]|None = None, on_chunk_received: Callable[[int], None]|None = None, on_download_end: Callable[[int], None]|None = None) -> None:
        apps = self.get_app_info(package_name)
        if version_code != -1:
            downloaded = False
            for app in apps:
                try:
                    version = app.get_version_by_code(version_code)
                    version.source.download_app(app.package, version, output_file, on_download_start, on_chunk_received, on_download_end)
                    downloaded = True
                    break
                except StopIteration:
                    continue
            if not downloaded:
                raise AppNotFoundError(f'Version {version_code} not found')
        else:
            last_version = Utils.find_last_version(apps)
            if last_version is not None:
                last_version.source.download_app(package_name, last_version, output_file, on_download_start, on_chunk_received, on_download_end)

    def get_developer_id(self, package_name: str) -> set[tuple[BaseSource, str]]:
        developers: set[tuple[BaseSource, str]] = set()

        for source in self.__sources.values():
            try:
                developer = source.get_developer_id(package_name)
            except AppNotFoundError:
                continue
            if developer is not None:
                developers.add((source, developer))

        if len(developers) == 0:
            raise AppNotFoundError(f'{package_name} not found')

        return developers

    def get_packages_from_developer(self, developer_id: str) -> set[str]:
        packages = set()

        for source in self.__sources.values():
            try:
                packages.update(source.find_packages_from_developer(developer_id))
            except DeveloperNotFoundError:
                continue

        return packages

class SourceImportError(ImportError):
    pass

class SourceNotFoundError(FileNotFoundError):
    pass

def download_apps(apkd: Apkd, queue: Queue, output_file: str):
    while True:
        try:
            pkg, version_code = queue.get(block=False)
        except QueueEmpty:
            break

        bar: tqdm
        def on_download_start(version: AppVersion, file_size: int, pkg=pkg):
            nonlocal bar
            bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=f'{pkg} ver. {version.code} ({version.source.name})', bar_format='{l_bar}{bar}{r_bar}')

        def on_chunk_received(downloaded_size: int):
            nonlocal bar
            bar.n = downloaded_size
            bar.update(0)

        def on_download_end(_: int):
            nonlocal bar
            bar.close()

        try:
            apkd.download_app(pkg, version_code, output_file, on_download_start, on_chunk_received, on_download_end)
        except AppNotFoundError:
            pass
        queue.task_done()

def list_apps_versions(lock: Lock, apkd: Apkd, queue: Queue, table: PrettyTable, versions_limit: int = -1):
    while True:
        try:
            pkg, _ = queue.get(block=False)
        except QueueEmpty:
            break

        try:
            apps = apkd.get_app_info(pkg, versions_limit)
        except Exception as e:
            get_logger().error(f'Error at list_apps_versions for "{pkg}": {e}')
            not_available = 'N/A'
            with lock:
                table.add_row([pkg, not_available, not_available, not_available, not_available, not_available])
            queue.task_done()
            continue

        for app in apps:
            version: AppVersion
            for version in app.get_versions():
                size_mb = version.size / (1024 * 1024)
                with lock:
                    table.add_row([app.package, version.source.name, version.name, version.code, version.update_date or 'N/A', f'{size_mb:.2f} MB'])

        queue.task_done()

def get_developer_id(lock: Lock, apkd: Apkd, queue: Queue, table: PrettyTable):
    while True:
        try:
            pkg, _ = queue.get(block=False)
        except QueueEmpty:
            break

        try:
            developers = apkd.get_developer_id(pkg)
        except Exception:
            not_available = 'N/A'
            with lock:
                table.add_row([pkg, not_available, not_available])
            queue.task_done()
            continue

        with lock:
            for source, developer in developers:
                table.add_row([pkg, source.name, developer])

        queue.task_done()

def divide_rows_by_pkg(table: PrettyTable):
    pkg = None
    for idx, row in enumerate(table.rows):
        if pkg is None:
            pkg = row[0]

        if pkg != row[0]:
            if row[3] == 'N/A':
                if pkg != '-':
                    table._dividers[idx-1] = True
                pkg = '-'
            else:
                table._dividers[idx-1] = True
                pkg = row[0]

def divide_rows_by_source(table: PrettyTable):
    source = None
    for idx, row in enumerate(table.rows):
        if source is None:
            source = row[1]

        if source != row[1]:
            table._dividers[idx-1] = True
            source = row[1]

def cli():
    apkd = Apkd(auto_load_sources=False)
    sources_names = Utils.get_available_sources_names()

    parser = argparse.ArgumentParser('apkd')
    parser.add_argument('--package', '-p', help='Package name', type=str)
    parser.add_argument('--packages-list', '-l', help='File with package names', type=str)
    parser.add_argument('--version-code', '-vc', help='Version code', type=int, default=-1)
    parser.add_argument('--list-developers', '-ld', help='Get developer name by pkg', action='store_true')
    parser.add_argument('--developer-id', '-did', help='Developer ID', type=str)
    parser.add_argument('--download', '-d', help='Download', action='store_true')
    parser.add_argument('--list-versions', '-lv', help='List available versions', action='store_true')
    parser.add_argument('--source', '-s', help='Source', nargs='+', default=sources_names, choices=sources_names)
    parser.add_argument('--output', '-o', help='Output file', type=str)
    parser.add_argument('--verbose', '-v', help='Verbose logging', action='store_true', default=False)
    parser.add_argument('--version', help='Print version', action='store_true', default=False)
    args = parser.parse_args(sys.argv[1:])

    if args.version:
        print(f'apkd by kiber.io\nv{VERSION}')
        return

    if args.verbose:
        logger = get_logger()
        logger.setLevel(logging.DEBUG)
        logging_handler = logging.StreamHandler()
        logging_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(logging_handler)

    if [args.list_versions, args.download, args.list_developers].count(True) == 0:
        parser.error('At least one of --list-versions/--download/--get-developer is required')
    elif [args.list_versions, args.download, args.list_developers].count(True) > 1:
        parser.error('--list-versions/--download/--get-developer cannot be used together')

    if not args.download and args.version_code != -1:
        parser.error('--version-code can only be used with --download')

    if args.list_versions and (not args.package and not args.packages_list and not args.developer_id):
        parser.error('--list-versions required one of --package/--packages-list/--developer-id option')

    sources = Utils.import_sources(args.source)
    for source_name, source in sources.items():
        apkd.add_source(source_name, source)

    packages: set[tuple[str, int]] = set()
    if args.package:
        packages.add((args.package, args.version_code))
    elif args.packages_list:
        with open(args.packages_list, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    pkg = line
                    version_code = -1
                    if '==' in line:
                        pkg, version_code = line.split('==')
                        try:
                            version_code = int(version_code)
                        except ValueError:
                            get_logger().warn(f'Incorrect line: {line}, skip')
                            continue
                    packages.add((pkg, version_code))
    elif args.developer_id:
        for pkg in apkd.get_packages_from_developer(args.developer_id):
            packages.add((pkg, -1))

    q = Queue()
    for pkg in packages:
        q.put(pkg)

    table: PrettyTable|None = None
    if args.list_versions:
        table = PrettyTable(field_names=['Package', 'Source', 'Version name', 'Version code', 'Update date', 'Size'], align='l')
    elif args.list_developers:
        table = PrettyTable(field_names=['Package', 'Source', 'Developer ID'], align='l')

    lock = Lock()
    threads = set()
    threads_count = 3
    if len(packages) < 3:
        threads_count = len(packages)
    for _ in range(threads_count):
        arguments = [apkd, q]
        target = None
        if args.download:
            target = download_apps
            arguments.append(args.output)
        elif args.list_versions:
            arguments.insert(0, lock)
            arguments.append(table)
            if args.developer_id:
                arguments.append(1)
            target = list_apps_versions
        elif args.list_developers:
            arguments.insert(0, lock)
            arguments.append(table)
            target = get_developer_id
        thread = Thread(target=target, args=tuple(arguments))
        thread.start()
        threads.add(thread)

    q.join()
    for thread in threads:
        thread.join()

    if args.list_versions:
        assert table is not None
        # sort table by "Source" + "Version code" columns
        def sort_by_pkg_and_vc(row1, row2):
            if row1[3] == 'N/A':
                return 1
            if row2[3] == 'N/A':
                return -1
            pkg1 = row1[0].lower()
            pkg2 = row2[0].lower()
            if pkg1 > pkg2:
                return 1
            elif pkg1 < pkg2:
                return -1
            else:
                return row2[3] - row1[3]
        table._rows.sort(key=cmp_to_key(sort_by_pkg_and_vc))
        # if args.developer_id:
        #     def sort_by_pkg_and_vc(row1, row2):
        #         if row1[3] == 'N/A':
        #             return 1
        #         if row2[3] == 'N/A':
        #             return -1
        #         pkg1 = row1[0].lower()
        #         pkg2 = row2[0].lower()
        #         if pkg1 > pkg2:
        #             return 1
        #         elif pkg1 < pkg2:
        #             return -1
        #         else:
        #             source1 = row1[1].lower()
        #             source2 = row2[1].lower()
        #             if source1 > source2:
        #                 return 1
        #             else:
        #                 return -1

        #     table._rows.sort(key=cmp_to_key(sort_by_pkg_and_vc))
        #     divide_rows_by_pkg(table)
        # else:
        divide_rows_by_pkg(table)
        print(table)
    elif args.list_developers:
        assert table is not None
        # sort table by "Source" column
        def sort(row1, row2):
            if row1[2] == 'N/A':
                return 1
            if row2[2] == 'N/A':
                return -1
            return row2[1] < row1[1]
        table._rows.sort(key=cmp_to_key(sort))
        divide_rows_by_pkg(table)
        print(table)