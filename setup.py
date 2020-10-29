from setuptools import setup

APP = ['hmm.py']
DATA_FILES = ['external-content.duckduckgo-1.png', 'voice copy.mp3', 'credentials.json', 'credentials.json']
OPTIONS = {
    'iconfile': 'logoapp.icns',
    'argv_emulation': True,
    'packages': ['certifi'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
