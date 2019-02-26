from distutils.core import setup

setup(name='PossumD3MWrapper',
    version='1.0.1',
    description='A thin wrapper for interacting with New Knowledge text summarization library Possum',
    packages=['PossumD3MWrapper'],
    install_requires=['Possum==1.1.2'],
    dependency_links=[
        "git+https://github.com/NewKnowledge/Possum@0f51cef455643c50df0ba3a185eab4324762d420#egg=Possum-1.1.2"
    ],
    entry_points = {
        'd3m.primitives': [
            'data_cleaning.text_summarization.Possum = PossumD3MWrapper:nk_possum'
        ],
    }, 
)
