import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="facebook_crawler",
  version="0.0.3",
  author="TENG-LIN YU",
  author_email="tlyu0419@gmail.com",
  description="You can collect data from Facebook's Fanspage/group elegantly.",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/TLYu0419/quantumtw",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
  python_requires=">=3.6",
  install_requires=[
      "requests==2.24.0",
      "bs4==0.0.1"
      "numpy==1.20.3",
      "pandas==1.2.4"
    ],
)