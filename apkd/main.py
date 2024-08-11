import argparse
import logging
import os
import sys
from functools import cmp_to_key
from importlib import util as importutil
from queue import Empty as QueueEmpty
from queue import Queue
from threading import Lock, Thread
from typing import Optional

from prettytable import PrettyTable

from apkd.utils import (App, AppNotFoundError, AppVersion, BaseSource,
                        get_logger)
from typing import Callable
from tqdm import tqdm


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

    def get_app_info(self, package_name: str) -> list[App]:
        apps: list[App] = list()

        for source in self.__sources.values():
            try:
                app = source.get_app_info(package_name)
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

class SourceImportError(ImportError):
    pass

class SourceNotFoundError(FileNotFoundError):
    pass

def download_apps(apkd: Apkd, queue: Queue, output_file: str, version_code: int = -1):
    while True:
        try:
            pkg = queue.get(block=False)
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
        except AppNotFoundError as e:
            print(e)
        except Exception:
            pass
        queue.task_done()

def list_apps_versions(lock: Lock, apkd: Apkd, queue: Queue, table: PrettyTable):
    while True:
        try:
            pkg = queue.get(block=False)
        except QueueEmpty:
            break

        try:
            apps = apkd.get_app_info(pkg)
        except Exception:
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

def cli():
    apkd = Apkd(auto_load_sources=False)
    sources_names = Utils.get_available_sources_names()

    parser = argparse.ArgumentParser('apkd')
    parser.add_argument('--package', '-p', help='Package name')
    parser.add_argument('--packages-list', '-l', help='File with package names')
    parser.add_argument('--version-code', '-vc', help='Version code', type=int)
    parser.add_argument('--download', '-d', help='Download', action='store_true')
    parser.add_argument('--list-versions', '-lv', help='List available versions', action='store_true')
    parser.add_argument('--source', '-s', help='Source', nargs='+', default=sources_names, choices=sources_names)
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--verbose', '-v', help='Verbose logging', action='store_true', default=False)
    args = parser.parse_args(sys.argv[1:])

    if args.verbose:
        logger = get_logger()
        logger.setLevel(logging.DEBUG)
        logging_handler = logging.StreamHandler()
        logging_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(logging_handler)

    if args.list_versions and args.download:
        parser.error('--list-versions and --download cannot be used together')

    if not args.list_versions and not args.download:
        parser.error('At least one of --list-versions and --download is required')

    if not args.download and args.version_code:
        parser.error('--version-code can only be used with --download')

    sources = Utils.import_sources(args.source)
    for source_name, source in sources.items():
        apkd.add_source(source_name, source)

    packages: set[str] = set()
    if args.package:
        packages.add(args.package)
    elif args.packages_list:
        with open(args.packages_list, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    packages.add(line)

    q = Queue()
    for pkg in packages:
        q.put(pkg)

    table: PrettyTable|None = None
    if args.list_versions:
        table = PrettyTable(field_names=['Package', 'Source', 'Version name', 'Version code', 'Update date', 'Size'], align='l')

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
            if args.version_code:
                arguments.append(args.version_code)
        elif args.list_versions:
            arguments.insert(0, lock)
            arguments.append(table)
            target = list_apps_versions
        thread = Thread(target=target, args=tuple(arguments))
        thread.start()
        threads.add(thread)

    q.join()
    for thread in threads:
        thread.join()

    if args.list_versions:
        assert table is not None
        def sort(row1, row2):
            if row1[3] == 'N/A':
                return 1
            if row2[3] == 'N/A':
                return -1
            if row1[0] > row2[0]:
                return 1
            elif row1[0] < row2[0]:
                return -1
            else:
                return row2[3] - row1[3]
        table._rows.sort(key=cmp_to_key(sort))
        pkg = None
        for idx, row in enumerate(table.rows):
            if pkg is None:
                pkg = row[0]

            if pkg != row[0]:
                table._dividers[idx-1] = True
                pkg = row[0]
        print(table)