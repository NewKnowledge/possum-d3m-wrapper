from distutils.core import setup

setup(name='PossumD3MWrapper',
    version='1.0.2',
    description='A thin wrapper for interacting with New Knowledge text summarization library Possum',
    packages=['PossumD3MWrapper'],
    install_requires=['Possum==1.1.3'],
    dependency_links=[
        "git+https://github.com/NewKnowledge/Possum@0120bb62ac9e4b726bc8ca8d934956ca9e400302f#egg=Possum-1.1.3"
    ],
    entry_points = {
        'd3m.primitives': [
            'data_cleaning.text_summarization.Possum = PossumD3MWrapper:nk_possum'
        ],
    }, 
)
