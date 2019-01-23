import sys
import os.path
import os
import numpy as np
import pandas

from Possum import Possum
from tslearn.datasets import CachedDatasets

from d3m.primitive_interfaces.transformer import TransformerPrimitiveBase
from d3m.primitive_interfaces.base import CallResult

from d3m import container, utils
from d3m.container import DataFrame as d3m_DataFrame
from d3m.metadata import hyperparams, base as metadata_base
from d3m.primitives.datasets import DatasetToDataFrame
from common_primitives import utils as utils_cp

__author__ = 'Distil'
__version__ = '1.0.0'

Inputs = container.pandas.DataFrame
Outputs = container.pandas.DataFrame

class Hyperparams(hyperparams.Hyperparams):
    algorithm = hyperparams.Enumeration(default = 'text_rank', 
        semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        values = ['luhn','edmundson','lsa','text_rank','sum_basic','kl'],
        description = 'type of summarization algorithm to use')
    source_type = hyperparams.Enumeration(default = 'plain_text', 
        semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        values = ['plain_text','url'],
        description = 'type of source documents to be analyzed')
    language = hyperparams.Enumeration(default = 'english', 
        semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        values = ['danish','dutch','english','finnish','french','german','hungarian','italian','norwegian','porter','portuguese','romanian','russian','spanish','swedish'],
        description = 'language to use for the NLTK stemming process')
    nsentences = hyperparams.UniformInt(lower=1, upper=sys.maxsize, default=20, semantic_types=
        ['https://metadata.datadrivendiscovery.org/types/ControlParameter'], description = 'number of summary sentences to return')  
    pass

class nk_possum(TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
    metadata = metadata_base.PrimitiveMetadata({
        # Simply an UUID generated once and fixed forever. Generated using "uuid.uuid4()".
        'id': "77bf4b92-2faa-3e38-bb7e-804131243a7f",
        'version': __version__,
        'name': "Possum",
        # Keywords do not have a controlled vocabulary. Authors can put here whatever they find suitable.
        'keywords': ['Natural Language Processing','NLP','Text Summarization'],
        'source': {
            'name': __author__,
            'uris': [
                # Unstructured URIs.
                "https://github.com/NewKnowledge/possum-d3m-wrapper",
            ],
        },
        # A list of dependencies in order. These can be Python packages, system packages, or Docker images.
        # Of course Python packages can also have their own dependencies, but sometimes it is necessary to
        # install a Python package first to be even able to run setup.py of another package. Or you have
        # a dependency which is not on PyPi.
         'installation': [{
            'type': metadata_base.PrimitiveInstallationType.PIP,
            'package_uri': 'git+https://github.com/NewKnowledge/possum-d3m-wrapper.git@{git_commit}#egg=PossumD3MWrapper'.format(
                git_commit=utils.current_git_commit(os.path.dirname(__file__)),
            ),
        }],
        # The same path the primitive is registered with entry points in setup.py.
        'python_path': 'd3m.primitives.distil.Possum',
        # Choose these from a controlled vocabulary in the schema. If anything is missing which would
        # best describe the primitive, make a merge request.
        'algorithm_types': [
            metadata_base.PrimitiveAlgorithmType.LATENT_SEMANTIC_ANALYSIS
        ],
        'primitive_family': metadata_base.PrimitiveFamily.FEATURE_EXTRACTION ,
    })

    def __init__(self, *, hyperparams: Hyperparams)-> None:
        super().__init__(hyperparams=hyperparams)

    def produce(self, *, inputs: Inputs) -> CallResult[Outputs]:
        """
        Applies the selected text summarization.

        Parameters
        ----------
        inputs : Input pandas dataframe where each row is a string representing a text document or a URL (if the source_type parameter is 'url').  

        Returns
        -------
        Outputs
            The output is a dataframe containing the requested number of summary sentences. The sentence column contains a summary sentence, and the importance column contains the weighted importance as a float number.
        """
        process_id = os.getpid()
        
        # set up model
        TopicExtractor = Possum()

        # set number of sentences to be returned
        if self.hyperparams['nsentences'] < 1 or not self.hyperparams['nsentences']:
            # enforce default value
            nsentences = 20
        else:
            nsentences = self.hyperparams['nsentences']
            
        if self.hyperparams['source_type'] == 'url':
            HTML_flag = True
        else:
            HTML_flag = False
      
        # Create a pandas dataframe from the input values.
        input_df = pandas.DataFrame(inputs.values)
        print(input)
        
        # Write the inputs to a temporary file to be processed.
        filename = 'temp_' + process_id + '.txt'
        input_df.to_csv(filename,index=False)
        
        try:
            sentences = TopicExtractor.ExtractivelySummarizeCorpus(corpus_path=filename,HTML=HTML_flag,sentence_count=nsentences)
        except Exception:
            print('Error creating summary sentences.')
            sys.exit(-1)
        print(sentences)
        
        try:
            extracted_topics = TopicExtractor.ExtractTopics(sentences)
        except Exception:
            print('Error creating importance weights.')
            sys.exit(-1)
        print(extracted_topics)

        # Create the output dataframe
        out_df_possum = pd.DataFrame.from_dict(extracted_topics, orient='index',
...                        columns=['sentence', 'importance_weight'])
        print(out_df_possum)
        outd3m_df_possum = d3m_DataFrame(out_df_possum)

        return CallResult(outd3m_df_possum)

if __name__ == '__main__':
    # Load test data and run 
    # SIAM 2007 Text Mining Competition dataset (first 100 rows)
    # https://c3.nasa.gov/dashlink/resources/138/
    input_df = pd.read_csv('data/NASA_TestData.txt', dtype=str, header=None)
    inputs = d3m_DataFrame(input_df)
    possum_client = nk_possum(hyperparams={'algorithm':'text_rank','source_type':'plain_text', 'language':'english','nsentences':30})
    #frame = pandas.read_csv("path/csv_containing_one_series_per_row.csv",dtype=str)
    result = possum_client.produce(inputs)
    print(result.value)
