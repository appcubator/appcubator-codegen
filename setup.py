from distutils.core import setup

setup(
    name='Appcubator-codegen',
    version='0.1.0',
    author='Appcubator',
    author_email='team@appcubator.com',
    packages=['app_builder',
              'app_builder.analyzer',
              'app_builder.code_templates',
              'app_builder.code_templates.htmlgen',
              'app_builder.codes',
              ],
    url='https://github.com/appcubator/appcubator-codegen',
    license='LICENSE.txt',
    description='Tranforms app state to code',
    long_description=open('README.md').read(),
    install_requires=['shell'],
)
