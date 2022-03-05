from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='yt2mp3',
    version='0.1.5',
    packages=['ong_yt2mp3', 'ong_yt2mp3.icons'],
    package_data={
        # Include icon files
        "ong_yt2mp3.icons": ["*.png"],
    },
    url='https://github.com/Oneirag/yt2mp3.git',
    license='',
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
