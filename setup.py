from distutils.core import setup

setup(
    name='Appcubator-codegen',
    version='0.1.0',
    author='Appcubator',
    author_email='team@appcubator.com',
    packages=['app_builder',
              'app_builder.analyzer',
              'app_builder.codes',
              'app_builder.deployment',
              'app_builder.tests'
              ],
    package_data={"app_builder": ['tests/master_state.json',
                                  'codes/code_templates/*.*', 'codes/code_templates/*/*.*',
                                  'analyzer/templates/*.*', 'analyzer/templates/*/*.*']},
    url='https://github.com/appcubator/appcubator-codegen',
    license='LICENSE.txt',
    description='Tranforms app state to code',
    long_description=open('README.md').read(),
    install_requires=['shell'],
)
