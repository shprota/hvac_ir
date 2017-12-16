from setuptools import setup

setup(name='hvac-ir',
      version='0.1',
      description='Air conditioner control code generator',
      url='http://github.com/shprota/hvac_ir',
      author='Shprota',
      author_email='shprota@gmail.com',
      license='MIT',
      packages=['hvac_ir'],
      install_requires=[
          'broadlink'
      ],
      zip_safe=False)