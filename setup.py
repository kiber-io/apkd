from setuptools import find_packages, setup

packages = ['apkd', 'apkd.sources']
for lib in find_packages('apkd/libs'):
    packages.append(f'apkd.libs.{lib}')

setup(
    name='apkd',
    version='1.1.2',
    author='kiber.io',
    license='MIT',
    url='https://github.com/kiber-io/apkd',
    install_requires=[
        'prettytable==3.11.0',
        'cloudscraper==1.2.71',
        'tqdm==4.66.5',
        'beautifulsoup4==4.12.3',
        'user_agent==0.1.10'
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
