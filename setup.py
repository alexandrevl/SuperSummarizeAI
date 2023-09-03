from setuptools import setup, find_packages

setup(
    name='ssai',
    version='1.0.3',
    description='A tool for summarizing content',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Alexandre Lima',
    author_email='alexandrevl@gmail.com',
    url='https://github.com/alexandrevl/SuperSummarizeAI',  # Assuming it's on GitHub
    packages=find_packages(),
    install_requires=open('requirements.txt').readlines(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': [
            'ssai=ssai:main',
        ],
    },
)

