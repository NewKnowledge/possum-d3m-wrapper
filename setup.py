from distutils.core import setup

setup(name='PossumD3MWrapper',
    version='1.0.0',
    description='A thin wrapper for interacting with New Knowledge text summarization library Possum',
    packages=['PossumD3MWrapper'],
    install_requires=['Possum==1.0.0'],
    dependency_links=[
        "git+https://github.com/NewKnowledge/possum#egg=Possum-1.0.0"
    ],
    entry_points = {
        'd3m.primitives': [
            'feature_extraction.ibex.Possum = PossumD3MWrapper:nk_possum'
        ],
    },
)
