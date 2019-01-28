from PossumD3MWrapper.nk_possum import nk_possum
import traceback
import logging

logger = logging.getLogger('possum_d3m_wrapper')
logger.setLevel(logging.DEBUG)

try:
    import nltk
    nltk.download('punkt')
except Exception:
    print('Error downloading NLTK tokenizers.')
    log_traceback(ex)
    sys.exit(-1)



__version__ = '1.0.0'

__all__ = [
           "nk_possum"
           ]