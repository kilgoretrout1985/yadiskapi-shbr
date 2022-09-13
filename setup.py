import setuptools
import os
from pkg_resources import parse_requirements


def load_requirements(fname: str) -> list:
    """
    This allows us to store all project requirements in `requirements*.txt`
    files, lots of people are used to. And here in setup.py we dynamically 
    read them from txt-files to avoid duplication.
    """
    requirements = []
    with open(fname, 'r') as fp:
        for req in parse_requirements(fp.read()):
            extras = '[{}]'.format(','.join(req.extras)) if req.extras else ''
            requirements.append(
                '{}{}{}'.format(req.name, extras, req.specifier)
            )
    return requirements


if __name__ == "__main__":
    SETUP_CWD = os.path.dirname(os.path.abspath(__file__))
    README = open(os.path.join(SETUP_CWD, 'README.md')).read()

    setuptools.setup(
        # metadata
        name = 'yadiskapi',
        version = '0.0.1',
        author = 'Yuriy Zemskov',
        author_email = 'zemskyura@gmail.com',
        license = 'MIT',
        license_files = ('LICENSE',),
        description = 'your description here',
        long_description = README,
        long_description_content_type = "text/markdown; charset=UTF-8",
        url = 'https://github.com/kilgoretrout1985/yadiskapi-shbr',
        platforms = 'unix, linux, osx, cygwin, win32',
        classifiers = [
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
        ],

        # options
        python_requires = '>=3.9',
        # packages = find_packages(exclude=['tests']),
        packages = ['yadiskapi'],
        include_package_data = True,
        # for package_data see MANIFEST.in file
        package_dir = {'': 'src'},
        install_requires = load_requirements(os.path.join(SETUP_CWD, 'requirements.txt')),
        extras_require = {'dev': load_requirements(os.path.join(SETUP_CWD, 'requirements.dev.txt'))}
    )
