from setuptools import setup

setup(name='hvac-ir',
      version='0.7',
      description='Air conditioner control code generator',
      url='http://github.com/shprota/hvac_ir',
      author='Shprota',
      author_email='shprota@gmail.com',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      keywords='airconditioner hvac ac control ir infrared heatpump midea gree daikin carrier',
      packages=['hvac_ir'],
      install_requires=[
      ],
      zip_safe=False)
