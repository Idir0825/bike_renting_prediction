"""
Baseline model for bicycle rent prediction. Here a Support Vector Regressor is used with the default scikit-learn arguments.
"""
from sklearn.svm import SVR
from typing import Optional, Dict, Any

from model_template import TemplateSKLModel


class SVRModel(TemplateSKLModel):

    def __init__(self, parameters=None):
        super().__init__()
        self.model = self.get_model(parameters=parameters)

    @staticmethod
    def get_model(parameters: Optional[Dict[str, Any]] = None) -> SVR:
        """
        Build and return an SVR regressor.
        """
        params = dict(parameters) if parameters else {}
        return SVR(**params)
