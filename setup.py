from distutils.core import setup

setup(name='PossumD3MWrapper',
    version='1.0.3',
    description='A thin wrapper for interacting with New Knowledge text summarization library Possum',
    packages=['PossumD3MWrapper'],
    install_requires=['Possum==1.1.4'],
    dependency_links=[
        "git+https://github.com/NewKnowledge/Possum@f1346af84167cdbad9b59c390369873a41709be2#egg=Possum-1.1.4"
    ],
    entry_points = {
        'd3m.primitives': [
            'data_cleaning.text_summarization.Possum = PossumD3MWrapper:nk_possum'
        ],
    }, 
)
