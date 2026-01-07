from abc import ABC, abstractmethod
import joblib
from typing import Optional, Dict, Any
import numpy as np
from sklearn.metrics import mean_squared_error
from pathlib import Path

class TemplateModel(ABC):

    def __init__(self, parameters=None):
        self.model = self.get_model(parameters=parameters)

    @staticmethod
    @abstractmethod
    def get_model(parameters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Build and return regressor.
        """
        pass

    @staticmethod
    @abstractmethod
    def train_regressor(
        self,
        x_train: np.ndarray,
        y_train: np.ndarray,
    ) -> Any:
        """
        Train the regressor.
        """
        pass

    @staticmethod
    @abstractmethod
    def predict(
        x: np.ndarray,
    ) -> np.ndarray:
        """
        Run inference with the trained model.
        """
        pass

    def evaluate_rmse(
        self,
        x_val: np.ndarray,
        y_val: np.ndarray,
    ) -> float:
        """
        Evaluate model using RMSE.
        """
        preds = self.predict(x_val)
        rmse = mean_squared_error(y_val, preds)
        return rmse

    @staticmethod
    @abstractmethod
    def save_model(
        self,
        path: str | Path,
    ) -> None:
        """
        Save trained model to disk.
        """
        pass

    @staticmethod
    @abstractmethod
    def load_model(
        path: str | Path,
    ) -> Any:
        """
        Load trained model from disk.
        """
        pass


class TemplateSKLModel(TemplateModel, ABC):
    """
    Abstract template for scikit-learn estimators.
    Implements the common parts:
    - .fit
    - .predict
    - joblib save/load
    Still abstract because get_model() is not implemented here.
    """

    def train_regressor(self, x_train: np.ndarray, y_train: np.ndarray) -> None:
        self.model.fit(x_train, y_train)

    def predict(self, x: np.ndarray) -> np.ndarray:
        return self.model.predict(x)

    def save_model(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)

    def load_model(self, path: str | Path) -> None:
        self.model = joblib.load(path)
