import setuptools

setuptools.setup(
    name='gen_data',
    version='0.0.1',
    description='gen obj data',
    install_requires=[
        'numpy',
        'pybullet==2.5.0',
        'google-cloud-storage==1.25.0'
    ],
    packages=setuptools.find_packages(),
)
