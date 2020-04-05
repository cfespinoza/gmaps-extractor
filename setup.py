import os

from setuptools import find_packages, setup

pjoin = os.path.join

here = os.path.abspath(os.path.dirname(__file__))

# Version
ns = {}
with open(pjoin(here, 'gmaps', '_version.py')) as f:
    exec(f.read(), {}, ns)

dependencies = []
if os.path.isfile("requirements.txt"):
    with open("requirements.txt") as f:
        for l in f.readlines():
            dependencies.append(l)


def setup_package():
    metadata = dict(
        name='gmaps-extractor',
        packages=find_packages(),
        description="""GMaps Places Scraper Library.""",
        install_requires=dependencies,
        author="oetam-selrach",
        platforms="Linux",
        version=ns['__version__'],
        keywords=['Interactive', 'Interpreter', 'Shell', 'Web'],
        classifiers=['Programming Language :: Python :: 3'],
        entry_points={
            'console_scripts': [
                'gmaps-extractor = gmaps.gmaps_extractor:extract',
                'gmaps-db = gmaps.db.db_ops:db_ops',
                'gmaps-url-scrapper = gmaps.gmaps_url_extractor:extract'
            ]
        }
    )

    setup(**metadata)


if __name__ == '__main__':
    setup_package()
