import os

from setuptools import setup, find_packages

with open('stac_tools/__init__.py') as f:
    for line in f:
        if line.find("__version__") >= 0:
            version = line.split("=")[1].strip()
            version = version.strip('"')
            version = version.strip("'")
            continue


with open('README.md') as f:
    readme = f.read()

# Runtime requirements.
inst_reqs = ["rasterio[s3]>=1.0a12"]

extra_reqs = {
    'test': ['mock', 'pytest', 'pytest-cov', 'codecov']}

setup(name='spacenet_stac',
      version=version,
      description=u"""Convert SpaceNet Repository to Stac Items""",
      long_description=readme,
      classifiers=[
          'Intended Audience :: Information Technology',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering :: GIS'],
      keywords='raster aws tiler gdal rasterio spacenet machinelearning',
      author=u"David Lindenbaum",
      author_email='dlindenbaum@iqt.org',
      url='https://github.com/SpaceNetChallenge//spacenet-stac',
      license='Apache 2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      zip_safe=False,
      install_requires=inst_reqs,
      extras_require=extra_reqs)
