"""
Day 4 — Deep neural network regressor.

HashingVectorizer + PyTorch NN; log-price target; L1 loss; train/val split.
Overfitting risk: high with small data; use val MAE and early stopping or fewer epochs.
"""

from pathlib import Path
from typing import List, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from torch.optim.lr_scheduler import CosineAnnealingLR
from sklearn.feature_extraction.text import HashingVectorizer

from ..curation.items import Item


class ResidualBlock(nn.Module):
    def __init__(self, hidden_size: int, dropout_prob: float):
        super().__init__()
        self.block = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_prob),
            nn.Linear(hidden_size, hidden_size),
            nn.LayerNorm(hidden_size),
        )
        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.relu(x + self.block(x))


class DeepNeuralNetwork(nn.Module):
    def __init__(
        self,
        input_size: int,
        num_layers: int = 10,
        hidden_size: int = 4096,
        dropout_prob: float = 0.2,
    ):
        super().__init__()
        self.input_layer = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_prob),
        )
        self.residual_blocks = nn.ModuleList([
            ResidualBlock(hidden_size, dropout_prob)
            for _ in range(max(0, num_layers - 2))
        ])
        self.output_layer = nn.Linear(hidden_size, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.input_layer(x)
        for block in self.residual_blocks:
            x = block(x)
        return self.output_layer(x)


class DNNRegressor:
    """
    Train and run DNN on item summaries (or full text).
    Log-price normalization; L1 loss; CosineAnnealingLR.
    Data size tradeoff: small train -> overfitting; use val MAE to decide epochs.
    """

    def __init__(
        self,
        train: List[Item],
        val: List[Item],
        n_features: int = 5000,
        num_layers: int = 4,
        hidden_size: int = 512,
        dropout_prob: float = 0.2,
        batch_size: int = 64,
        seed: int = 42,
    ):
        self.train_data = train
        self.val_data = val
        self.n_features = n_features
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.dropout_prob = dropout_prob
        self.batch_size = batch_size
        self.seed = seed
        self.vectorizer: Optional[HashingVectorizer] = None
        self.model: Optional[DeepNeuralNetwork] = None
        self.device: Optional[torch.device] = None
        self.y_mean: Optional[torch.Tensor] = None
        self.y_std: Optional[torch.Tensor] = None

        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)

    def setup(self) -> None:
        self.vectorizer = HashingVectorizer(
            n_features=self.n_features,
            stop_words="english",
            binary=True,
        )
        train_docs = [i.text_for_model or i.full or "" for i in self.train_data]
        val_docs = [i.text_for_model or i.full or "" for i in self.val_data]
        X_train = self.vectorizer.fit_transform(train_docs)
        X_val = self.vectorizer.transform(val_docs)
        self._X_train = torch.FloatTensor(X_train.toarray())
        self._X_val = torch.FloatTensor(X_val.toarray())
        y_train = torch.FloatTensor([float(i.price) for i in self.train_data]).unsqueeze(1)
        self._y_val = torch.FloatTensor([float(i.price) for i in self.val_data]).unsqueeze(1)
        y_train_log = torch.log(y_train + 1)
        y_val_log = torch.log(self._y_val + 1)
        self.y_mean = y_train_log.mean()
        self.y_std = y_train_log.std()
        self._y_train_norm = (y_train_log - self.y_mean) / self.y_std
        self._y_val_norm = (y_val_log - self.y_mean) / self.y_std

        self.model = DeepNeuralNetwork(
            self._X_train.shape[1],
            num_layers=self.num_layers,
            hidden_size=self.hidden_size,
            dropout_prob=self.dropout_prob,
        )
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")
        self.model.to(self.device)
        self._optimizer = optim.AdamW(self.model.parameters(), lr=0.001, weight_decay=0.01)
        self._scheduler = CosineAnnealingLR(self._optimizer, T_max=10, eta_min=0.0)
        self._loss_fn = nn.L1Loss()
        self._train_loader = DataLoader(
            TensorDataset(self._X_train, self._y_train_norm),
            batch_size=self.batch_size,
            shuffle=True,
        )

    def train(self, epochs: int = 3) -> None:
        if self.model is None:
            self.setup()
        for epoch in range(1, epochs + 1):
            self.model.train()
            for batch_x, batch_y in self._train_loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                self._optimizer.zero_grad()
                out = self.model(batch_x)
                loss = self._loss_fn(out, batch_y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self._optimizer.step()
            self.model.eval()
            with torch.no_grad():
                val_out = self.model(self._X_val.to(self.device))
                val_loss = self._loss_fn(val_out, self._y_val_norm.to(self.device))
                val_orig = torch.exp(val_out * self.y_std + self.y_mean) - 1
                mae = (val_orig - self._y_val.to(self.device)).abs().mean().item()
            self._scheduler.step()

    def predict_item(self, item: Item) -> float:
        """Single item -> price. Uses text_for_model (summary or full)."""
        if self.model is None or self.vectorizer is None:
            raise RuntimeError("Call setup() (and optionally train()) first")
        self.model.eval()
        text = item.text_for_model or item.full or ""
        X = self.vectorizer.transform([text])
        x = torch.FloatTensor(X.toarray()).to(self.device)
        with torch.no_grad():
            pred = self.model(x)[0]
        price = (torch.exp(pred * self.y_std + self.y_mean) - 1).item()
        return max(0.0, price)

    def save(self, path: Path) -> None:
        if self.model is None:
            raise RuntimeError("No model to save")
        torch.save(self.model.state_dict(), path)

    def load(self, path: Path) -> None:
        if self.model is None:
            self.setup()
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        self.model.to(self.device)


def dnn_predictor(
    train: List[Item],
    val: List[Item],
    epochs: int = 3,
    num_layers: int = 4,
    hidden_size: int = 512,
):
    """Build a DNN predictor: fit on train/val, return (item) -> price."""
    reg = DNNRegressor(train, val, num_layers=num_layers, hidden_size=hidden_size)
    reg.setup()
    reg.train(epochs=epochs)
    return reg.predict_item
