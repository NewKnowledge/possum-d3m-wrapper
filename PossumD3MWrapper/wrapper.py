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
#from d3m.primitives.datasets import DatasetToDataFrame
from common_primitives import utils as utils_cp

import traceback
import logging

logger = logging.getLogger('possum_d3m_wrapper')
logger.setLevel(logging.DEBUG)

__author__ = 'Distil'
__version__ = '1.0.0'
__contact__ = 'mailto:steve.kramer@newknowledge.io'

Inputs = container.pandas.DataFrame
Outputs = container.pandas.DataFrame

# 
def log_traceback(ex, ex_traceback=None):
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in
                 traceback.format_exception(ex.__class__, ex, ex_traceback)]
    logger.log(tb_lines)

try:
    import nltk
    dirpath = os.getcwd()
    print("Downloading NLTK data to ", dirpath)
    nltk.download('punkt', download_dir=dirpath)
except Exception as e:
    print('Error downloading NLTK tokenizers.')
    if e:
        log_traceback(e)
    sys.exit(-1)

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
    """
    Applies the selected text summarization algorithms packaged in the Possum base library.  
    The source library is the Python sumy library (https://pypi.org/project/sumy/).

    Parameters
    ----------
    Inputs : Input pandas dataframe where each row is a string representing a text document or a URL (if the source_type parameter is 'url').  

    Hyperparams:
        algorithm (type of summarization algorithm to use): 'luhn','edmundson','lsa','text_rank' (default),'sum_basic','kl'
        source_type (type of source documents to be analyzed) = 'plain_text' (default),'url'
        language (language to use for the NLTK stemming process) = 'danish','dutch','english' (default),'finnish','french','german','hungarian','italian','norwegian','porter','portuguese','romanian','russian','spanish','swedish'],
        nsentences (number of summary sentences to return); default is 20

    Returns
    -------
    Outputs
        The output is a dataframe containing the requested number of summary sentences.
    """
    metadata = metadata_base.PrimitiveMetadata({
        # Simply an UUID generated once and fixed forever. Generated using "uuid.uuid4()".
        'id': "3a0bbaa6-b98c-493c-bd06-4b746eced523",
        'version': __version__,
        'name': "Possum",
        # Keywords do not have a controlled vocabulary. Authors can put here whatever they find suitable.
        'keywords': ['Natural Language Processing','NLP','Text Summarization'],
        'source': {
            'name': __author__,
            'contact': __contact__,
            'uris': [
                # Unstructured URIs.
                "https://github.com/NewKnowledge/possum-d3m-wrapper",
            ],
        },
        # A list of dependencies in order. These can be Python packages, system packages, or Docker images.
        # Of course Python packages can also have their own dependencies, but sometimes it is necessary to
        # install a Python package first to be even able to run setup.py of another package. Or you have
        # a dependency which is not on PyPi.
         'installation': [
            {
                "type": "PIP",
                "package_uri": "git+https://github.com/NewKnowledge/Possum@ffc4d92ac7f08fd291617c714a6fd023469d7924#egg=Possum-1.0.0"
            },
             {
            'type': metadata_base.PrimitiveInstallationType.PIP,
            'package_uri': 'git+https://github.com/NewKnowledge/possum-d3m-wrapper.git@{git_commit}#egg=PossumD3MWrapper'.format(
                git_commit=utils.current_git_commit(os.path.dirname(__file__)),
            ),
        }],
        
        # The same path the primitive is registered with entry points in setup.py.
        'python_path': 'd3m.primitives.feature_extraction.ibex.Possum',
        # Choose these from a controlled vocabulary in the schema. If anything is missing which would
        # best describe the primitive, make a merge request.
        'algorithm_types': [
            metadata_base.PrimitiveAlgorithmType.LATENT_SEMANTIC_ANALYSIS
        ],
        'primitive_family': metadata_base.PrimitiveFamily.FEATURE_EXTRACTION,
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
            The output is a dataframe containing the requested number of summary sentences. 
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
        #input_df = pandas.DataFrame(inputs.values)
        
        input_df = pandas.DataFrame(inputs)
        print(input_df)
        print(type(inputs))
        print(type(input_df))
        
        # Write the inputs to a temporary file to be processed.
        filename = 'temp_' + str(process_id) + '.txt'
        print(filename)
        input_df.to_csv(filename,index=False)
        
        try:
            sentences = TopicExtractor.ExtractivelySummarizeCorpus(corpus_path=filename,HTML=HTML_flag,sentence_count=nsentences)   
        except Exception as ex:
            print('Error creating summary sentences.')
            log_traceback(ex)
            sys.exit(-1)
        print(sentences)
        
        # try:
        #     extracted_topics = TopicExtractor.ExtractTopics(sentences)
        # except Exception:
        #     print('Error creating importance weights.')
        #     log_traceback(ex)
        #     sys.exit(-1)
        # print(extracted_topics)
        # print(type(extracted_topics))
        #out_df_possum = pandas.DataFrame(list(extracted_topics[0].items()), columns=['sentence', 'importance_weight'])

        # Create the output dataframe
        out_df_possum = pandas.DataFrame(sentences)
        print(out_df_possum)

        # Write the results to a temporary file for review.
        out_filename = 'output_' + str(process_id) + '.txt'
        out_df_possum.to_csv(out_filename,index=False)

        outd3m_df_possum = d3m_DataFrame(out_df_possum)

        return CallResult(outd3m_df_possum)

if __name__ == '__main__':
    # Load test data and run 
    # SIAM 2007 Text Mining Competition dataset (first 100 rows)
    # https://c3.nasa.gov/dashlink/resources/138/
    input_df = pandas.read_csv('data/NASA_TestData.txt', dtype=str, header=None,index_col=False)
    inputs = d3m_DataFrame(input_df)
    print(inputs)
    print(type(inputs))
    possum_client = nk_possum(hyperparams={'algorithm':'text_rank','source_type':'plain_text', 'language':'english','nsentences':30})
    result = possum_client.produce(inputs=inputs)
    print(result.value)
