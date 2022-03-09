from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='yt2mp3',
    version='0.2.1',
    packages=['ong_yt2mp3', 'ong_yt2mp3.icons', 'ong_yt2mp3.i18n'],
    package_data={
        "ong_yt2mp3.icons": ["*.png"],          # Include icon files
        "ong_yt2mp3.i18n": ["*.qm"],            # Include translation files
    },
    url='https://github.com/Oneirag/yt2mp3.git',
    license='GPL',
    author='oneirag',
    author_email='oneirag@yahoo.es',
    description='Simple tool to download mp3 from youtube',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'yt2mp3 = ong_yt2mp3.browser:main',
        ],
    }
)
