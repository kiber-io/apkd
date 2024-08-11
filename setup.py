from setuptools import find_packages, setup

packages = ['apkd', 'apkd.sources']
for lib in find_packages('apkd/libs'):
    packages.append(f'apkd.libs.{lib}')

setup(
    name='apkd',
    version='1.1.0',
    author='kiber.io',
    license='MIT',
    url='https://github.com/kiber-io/apkd',
    install_requires=[
        'beautifulsoup4',
        'tqdm',
        'requests',
        'user-agent',
        'prettytable',
    ],
    include_package_data=True,
    keywords=['apk downloader', 'apk download', 'android downloader', 'app downloader', 'app download'],
    description='APK downloader from few sources',
    packages=packages,
    entry_points={
        'console_scripts': [
            'apkd = apkd.main:cli'
        ]
    }
)