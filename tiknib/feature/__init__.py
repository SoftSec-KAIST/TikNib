__all__ = ["Feature"]


class Feature:
    """
    template class for feature extraction modules
    """

    def __init__(self):
        pass

    @staticmethod
    def get(f):
        """
        feature extraction function

        get receives function data extracted from IDA script,
        which is dictionary of various fields (see tiknib/ida/fetch_funcdata.py).

        get should return dictionary of features.
        ex)
        features = {}
        features['feature_A_B'] = C
        features['feature_X_Y'] = Z
        """
        pass


from .feature_manager import FeatureManager
