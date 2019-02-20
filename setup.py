from distutils.core import setup

setup(name='PossumD3MWrapper',
    version='1.0.0',
    description='A thin wrapper for interacting with New Knowledge text summarization library Possum',
    packages=['PossumD3MWrapper'],
    install_requires=['Possum==1.0.1'],
    dependency_links=[
        "git+https://github.com/NewKnowledge/Possum@d067d4659ddd8010c5d05ec1cc8f399f54cad868#egg=Possum-1.0.1"
    ],
    entry_points = {
        'd3m.primitives': [
            'feature_extraction.text_summarization.Possum = PossumD3MWrapper:nk_possum'
        ],
    }, 
)
