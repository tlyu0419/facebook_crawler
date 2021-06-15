import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="facebook_crawler",
  version="0.0.11",
  author="TENG-LIN YU",
  author_email="tlyu0419@gmail.com",
  description="You can collect data from Facebook's Fanspage/group elegantly.",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/TLYu0419/facebook_crawler",
  packages=setuptools.find_packages(),
  py_modules=['facebook_crawler'],
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
  python_requires=">=3.6",
  install_requires=[
      "requests",
      "bs4",
      "numpy",
      "pandas",
      "lxml"
    ],
)