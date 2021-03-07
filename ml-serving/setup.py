from setuptools import setup

setup(
    name='ml-serving',
    version='0.1.0',    
    packages=['ml_serving'],
    install_requires=[
        'pika==1.2.0',
        'redis==3.5.3',                     
    ],
)
