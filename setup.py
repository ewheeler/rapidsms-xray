from setuptools import setup, find_packages


requirements = [line.strip('\n') for line in open('requirements/base.txt').readlines()]

setup(
    name='rapidsms-xray',
    version=__import__('xray').__version__,
    author='Evan Wheeler',
    author_email='evan@leapfrog.io',
    packages=find_packages(),
    include_package_data=True,
    dependency_links = ['http://github.com/ewheeler/cleaver/tarball/xray#egg=cleaver-0.1.5dev'],
    setup_requires=['Django',],
    install_requires=requirements,
    url='https://github.com/ewheeler/rapidsms-xray/',
    license='BSD',
    description=u' '.join(__import__('xray').__doc__.splitlines()).strip(),
    classifiers=[
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    long_description=open('README.rst').read(),
    test_suite='runtests.runtests',
    zip_safe=False,
)
