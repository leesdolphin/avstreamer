from setuptools import setup, find_packages

# From: http://stackoverflow.com/a/16624700/369021
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("build-requirements.txt",
                            session="ASDF") # I have no idea what this does
# reqs is a list of requirement]
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='PyCon AV Streaming Solution',
    version='0.1.0',
    url='https://github.com/leesdolphin/avstreamer',
    description='',
    license='MIT',
    author='PyCon 2014/15 AV team',
    author_email='leesdolphin@gmail.com',
    packages=find_packages(include=['avstreamer*', 'tests*']),
    scripts=[
      # TODO add
    ],
    install_requires=reqs,
    tests_require=[],
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python'
    ],
    # TODO Investigate this:
    zip_safe=False,
)
