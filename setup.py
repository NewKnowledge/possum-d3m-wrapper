from distutils.core import setup

setup(name='PossumD3MWrapper',
    version='1.0.3',
    description='A thin wrapper for interacting with New Knowledge text summarization library Possum',
    packages=['PossumD3MWrapper'],
    install_requires=['Possum==1.1.4'],
    dependency_links=[
        "git+https://github.com/NewKnowledge/Possum@dc3ee5d479d225ef7cdf1f19ba4cf446ee1c2ec2#egg=Possum-1.1.4"
    ],
    entry_points = {
        'd3m.primitives': [
            'data_cleaning.text_summarization.Possum = PossumD3MWrapper:nk_possum'
        ],
    }, 
)
