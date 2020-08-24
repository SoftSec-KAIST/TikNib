from .asm import AsmFeature
from .cfg import CfgFeature
from .cg import CgFeature
from .data import DataFeature
from .functype import TypeFeature


class FeatureManager:
    """
    new feature extraction module should be added here
    """

    def __init__(self):
        self.all_features = [
            AsmFeature,
            CfgFeature,
            CgFeature,
            DataFeature,
            TypeFeature,
        ]
        pass

    def get_all(self, f):
        """
        extract all features from feature extract modules
        """
        result = {}
        for feature in self.all_features:
            result.update(feature.get(f))
        return result
