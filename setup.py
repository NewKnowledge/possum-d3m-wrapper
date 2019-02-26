from distutils.core import setup

setup(name='PossumD3MWrapper',
    version='1.0.1',
    description='A thin wrapper for interacting with New Knowledge text summarization library Possum',
    packages=['PossumD3MWrapper'],
    install_requires=['Possum==1.1.0'],
    dependency_links=[
        "git+https://github.com/NewKnowledge/Possum@269d39180f07167507180e7f48d6b285f92183df#egg=Possum-1.0.1"
    ],
    entry_points = {
        'd3m.primitives': [
            'data_cleaning.text_summarization.Possum = PossumD3MWrapper:nk_possum'
        ],
    }, 
)
