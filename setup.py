from setuptools import setup

setup(
    name='apkd',
    version='1.0.0',
    author='kiber.io',
    license='MIT',
    url='https://github.com/kiber-io/apkd',
    install_requires=[
        'beautifulsoup4==4.12.3',
        'progressbar2==4.4.2',
        'PyPasser==0.0.5',
        'requests==2.31.0',
        'user-agent==0.1.10'
    ],
    keywords=['apk downloader', 'apk download', 'android downloader', 'app downloader', 'app download'],
    description='APK downloader from few sources',
    packages=['apkd', 'apkd.sources'],
    entry_points={
        'console_scripts': [
            'apkd = apkd.main:cli'
        ]
    }
)