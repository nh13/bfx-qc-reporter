from setuptools import setup
#from setuptools import setup, find_packages

setup(
    name = "bfx-qc-reporter",
    author = "Nils Homer",
    author_email = "nilshomer@gmail.com",
    version = 0.1,
    description = "Simple scripts to collate per-sample bioinformatic QC metrics. Supports fgbio, Picard, and CSV metric files.",
    url = "https://github.com/nh13/bfx-qc-reporter",
    license = "MIT",
	#packages = find_packages("src/python"),
	packages = ["bfx_qc_reporter", "bfx_qc_reporter.util"],
	package_dir = {"bfx_qc_reporter" : "src/python/bfx_qc_reporter", "bfx_qc_reporter.util" : "src/python/bfx_qc_reporter/util"},
	#package_data = {"bfx_qc_reporter" : "resources/*.csv"},
	package_data = {"bfx_qc_reporter" : "src/python/bfx_qc_reporter/resources/*.csv"},
    install_requires = [],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    entry_points= {
        'console_scripts': [
			'bfx-qc-reporter = bfx_qc_reporter.__main__:main'
        ]
    },
    include_package_data=True,
)
