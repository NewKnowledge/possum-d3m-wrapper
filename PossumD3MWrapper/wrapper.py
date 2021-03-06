import sys
import os.path
import os
import typing
import numpy as np
import pandas

from Possum import Possum

from d3m.primitive_interfaces.transformer import TransformerPrimitiveBase
from d3m.primitive_interfaces.base import CallResult

from d3m import container, utils
from d3m.container import DataFrame as d3m_DataFrame
from d3m.metadata import hyperparams, base as metadata_base
#from d3m.primitives.datasets import DatasetToDataFrame
from common_primitives import utils as utils_cp

import traceback
import logging
import nltk
import datetime

logger = logging.getLogger('possum_d3m_wrapper')
logger.setLevel(logging.DEBUG)

__author__ = 'Distil'
__version__ = '1.0.4'
__contact__ = 'mailto:nklabs@newknowledge.io'

Inputs = container.pandas.DataFrame
Outputs = container.pandas.DataFrame

# 
def log_traceback(ex, ex_traceback=None):
    if ex_traceback is None:
        ex_traceback = ex.__traceback__
    tb_lines = [ line.rstrip('\n') for line in
                 traceback.format_exception(ex.__class__, ex, ex_traceback)]
    logger.log(tb_lines)



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
    return_result = hyperparams.Enumeration(default = 'all', 
        semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        values = ['new','all','replace'],
        description = 'what data should be returned')
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
                "type": "TGZ",
                "key": "nltk_data",
                "file_uri": "http://public.datadrivendiscovery.org/nltk_tokenizers.tar.gz",
                "file_digest":"1eff17629fa9bcc06e979fef8a3804f1d29bf7b2502ef78d3be6cd9f1dab3f6f"
            },
             {
            'type': metadata_base.PrimitiveInstallationType.PIP,
            'package_uri': 'git+https://github.com/NewKnowledge/possum-d3m-wrapper.git@{git_commit}#egg=PossumD3MWrapper'.format(
                git_commit=utils.current_git_commit(os.path.dirname(__file__)),
            ),
        }],
        
        # The same path the primitive is registered with entry points in setup.py.
        'python_path': 'd3m.primitives.data_cleaning.text_summarization.Possum',
        # Choose these from a controlled vocabulary in the schema. If anything is missing which would
        # best describe the primitive, make a merge request.
        'algorithm_types': [
            metadata_base.PrimitiveAlgorithmType.LATENT_SEMANTIC_ANALYSIS
        ],
        'primitive_family': metadata_base.PrimitiveFamily.DATA_CLEANING,
    })

    def __init__(self, *, hyperparams: Hyperparams, volumes: typing.Dict[str,str]=None)-> None:
        super().__init__(hyperparams=hyperparams, volumes=volumes)
        self.volumes = volumes

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
        # Add method 
        if self.hyperparams['algorithm']:
            TopicExtractor = Possum(nltk_directory=self.volumes['nltk_data'])
        else:
            TopicExtractor = Possum(nltk_directory=self.volumes['nltk_data'], method=self.hyperparams['algorithm'])
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
        
        # Write the inputs to a temporary file to be processed.
        process_id = os.getpid()
        current_datetime = str(datetime.datetime.now()).replace(" ","_")
        filename = 'temp_' + str(process_id) + '_' + current_datetime + '.txt'
        logger.info(filename)
        input_df.to_csv(filename,index=False)
        
        try:
            sentences = TopicExtractor.ExtractivelySummarizeCorpus(corpus_path=filename,HTML=HTML_flag,sentence_count=nsentences)   
        except Exception as ex:
            logger.info('Error creating summary sentences.')
            log_traceback(ex)
            sys.exit(-1)
        logger.info(sentences)
        
        
        # Create the output dataframe
        out_df_possum = pandas.DataFrame(sentences)
        logger.info(out_df_possum)

        # Delete the temporary file.
        if os.path.exists(filename):
            os.remove(filename)

        # Write the results to a temporary file for review.
        # out_filename = 'output_' + filename
        # out_df_possum.to_csv(out_filename,index=False)

        if self.hyperparams['return_result'] == 'new' or self.hyperparams['return_result'] == 'replace':
            logger.info("Returning only summaries.")
            outd3m_df_possum = d3m_DataFrame(out_df_possum)
        else:  # append summaries to the input data
            logger.info("Returning original documents with summaries.")
            tmp_df = input_df.append(out_df_possum)
            outd3m_df_possum = d3m_DataFrame(tmp_df)
        return CallResult(outd3m_df_possum)

if __name__ == '__main__':
    # Load test data and run 
    # SIAM 2007 Text Mining Competition dataset (first 100 rows)
    # https://c3.nasa.gov/dashlink/resources/138/
    input_df = pandas.read_csv('data/NASA_TestData.txt', dtype=str, header=None,index_col=False)
    inputs = d3m_DataFrame(input_df)
    volumes = {} # d3m large primitive architecture dictionary of large files
    volumes['nltk_data'] = '/tmp/nltk_data'
    possum_client = nk_possum(hyperparams={'algorithm':'text_rank','source_type':'plain_text', 
    'language':'english','nsentences':30, 'return_result':'all'}, volumes=volumes)
    result = possum_client.produce(inputs=inputs)
    logger.info(result.value)
