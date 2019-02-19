from distutils.core import setup

setup(name='PossumD3MWrapper',
    version='1.0.0',
    description='A thin wrapper for interacting with New Knowledge text summarization library Possum',
    packages=['PossumD3MWrapper'],
    install_requires=['Possum==1.0.0'],
    dependency_links=[
        "git+https://github.com/NewKnowledge/Possum@6a7aaa03cdc1665b9163b751ccd68f75079071c3#egg=Possum-1.0.0"
    ],
    entry_points = {
        'd3m.primitives': [
            'feature_extraction.text_summarization.Possum = PossumD3MWrapper:nk_possum'
        ],
    }, 
)
