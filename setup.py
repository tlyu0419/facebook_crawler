import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="facebook_crawler",
  version="0.0.27",
  author="TENG-LIN YU",
  author_email="tlyu0419@gmail.com",
  description="Facebook crawler package can help you crawl the posts on public fanspages and groups from Facebook.",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/TLYu0419/facebook_crawler",
  packages=setuptools.find_packages(),
  py_modules=['facebook_crawler'],
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: Apache Software License",
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