"""
Prophet Stock Prediction Service
Pure Prophet (Phương án A): trend + seasonality + VN holidays
No regressors — avoids circular dependency for future prediction
"""

import os
import json
import joblib
import logging
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from prophet import Prophet
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.stock import Ticker, DailyPrice
from src.crud.crud_stock import create_predictions

logger = logging.getLogger(__name__)


def _patch_prophet_for_pandas3() -> None:
    """
    Prophet 1.1.x builds component matrices with duplicated row indexes.
    pandas 3.x is stricter here and raises:
    "cannot reindex on an axis with duplicate labels".

    Resetting indexes during the component concat keeps Prophet compatible
    without changing external dependencies at runtime.
    """
    if getattr(Prophet, "_stockai_pandas3_patch", False):
        return

    def _add_group_component(self, components, name, group):
        new_comp = components[components['component'].isin(set(group))].copy()
        group_cols = new_comp['col'].unique()
        if len(group_cols) > 0:
            new_comp = pd.DataFrame({'col': group_cols, 'component': name})
            components = pd.concat([components, new_comp], ignore_index=True)
        else:
            components = components.reset_index(drop=True)
        return components

    Prophet.add_group_component = _add_group_component
    Prophet._stockai_pandas3_patch = True


_patch_prophet_for_pandas3()

# ============================================================
# Vietnamese Holidays
# ============================================================
def _build_vn_holidays() -> pd.DataFrame:
    """Build Vietnamese holidays DataFrame for Prophet."""
    holidays_list = []

    for year in range(2018, 2030):
        # Tết Dương Lịch
        holidays_list.append({'holiday': 'tet_duong_lich', 'ds': f'{year}-01-01'})
        # Ngày Thống Nhất
        holidays_list.append({'holiday': 'thong_nhat', 'ds': f'{year}-04-30'})
        # Quốc tế Lao Động
        holidays_list.append({'holiday': 'quoc_te_lao_dong', 'ds': f'{year}-05-01'})
        # Quốc Khánh
        holidays_list.append({'holiday': 'quoc_khanh', 'ds': f'{year}-09-02'})

    # Giỗ Tổ Hùng Vương (approx dates - lunar calendar)
    hung_vuong = [
        '2020-04-02', '2021-04-21', '2022-04-10', '2023-04-29',
        '2024-04-18', '2025-04-07', '2026-04-26', '2027-04-16',
        '2028-05-03', '2029-04-22',
    ]
    for d in hung_vuong:
        holidays_list.append({'holiday': 'gio_to_hung_vuong', 'ds': d})

    # Tết Nguyên Đán (7-day blocks per year)
    tet_dates = {
        2020: ('01-23', '01-29'), 2021: ('02-10', '02-16'),
        2022: ('01-29', '02-04'), 2023: ('01-20', '01-26'),
        2024: ('02-08', '02-14'), 2025: ('01-27', '02-02'),
        2026: ('02-15', '02-21'), 2027: ('02-05', '02-11'),
        2028: ('01-25', '01-31'), 2029: ('02-12', '02-18'),
    }
    for year, (start_md, end_md) in tet_dates.items():
        start = pd.Timestamp(f'{year}-{start_md}')
        end = pd.Timestamp(f'{year}-{end_md}')
        current = start
        while current <= end:
            holidays_list.append({
                'holiday': 'tet_nguyen_dan',
                'ds': current.strftime('%Y-%m-%d')
            })
            current += timedelta(days=1)

    df = pd.DataFrame(holidays_list)
    df['ds'] = pd.to_datetime(df['ds'])
    df['lower_window'] = 0
    df['upper_window'] = 0
    return df


VN_HOLIDAYS = _build_vn_holidays()

# Best hyperparameters from notebook grid search
DEFAULT_PARAMS = {
    'changepoint_prior_scale': 0.001,
    'seasonality_prior_scale': 20.0,
    'seasonality_mode': 'multiplicative',
    'n_changepoints': 30,
    'changepoint_range': 0.85,
}

# Directory to save models
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'saved_models', 'prophet')


# ============================================================
# ProphetService
# ============================================================
class ProphetService:
    """Service to train, save, load, and predict with Prophet models."""

    @staticmethod
    def _get_ticker(db: Session, symbol: str) -> Ticker | None:
        stmt = select(Ticker).where(Ticker.symbol == symbol)
        return db.scalars(stmt).first()

    @staticmethod
    def _get_latest_price_date(db: Session, ticker_id: int) -> date | None:
        stmt = (
            select(DailyPrice.date)
            .where(DailyPrice.ticker_id == ticker_id)
            .order_by(DailyPrice.date.desc(), DailyPrice.id.desc())
            .limit(1)
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def _get_model_history_end_date(
        model: Prophet | None,
        metadata: dict | None,
    ) -> date | None:
        if metadata:
            end_date = metadata.get('date_range', {}).get('end')
            if end_date:
                try:
                    return date.fromisoformat(end_date)
                except ValueError:
                    logger.warning("Invalid metadata end date for Prophet model: %s", end_date)

        if model is not None and hasattr(model, 'history') and not model.history.empty:
            model_last_ds = model.history['ds'].max()
            if pd.notna(model_last_ds):
                return pd.Timestamp(model_last_ds).date()

        return None

    @staticmethod
    def _prepare_price_frame(prices: list[DailyPrice], symbol: str) -> pd.DataFrame:
        """
        Normalize raw price rows for Prophet training/prediction.

        Duplicate trading dates can happen after repeated imports. We keep the
        latest row for each day so the forecasting model always sees a clean,
        unique timeline.
        """
        df = pd.DataFrame([{
            'row_id': p.id,
            'ds': p.date,
            'y': p.close,
        } for p in prices])

        if df.empty:
            return pd.DataFrame(columns=['ds', 'y'])

        df['ds'] = pd.to_datetime(df['ds'])
        df.dropna(subset=['y'], inplace=True)
        df.sort_values(['ds', 'row_id'], inplace=True)

        duplicate_mask = df.duplicated(subset=['ds'], keep=False)
        if duplicate_mask.any():
            duplicate_days = int(df.loc[duplicate_mask, 'ds'].nunique())
            duplicate_rows = int(duplicate_mask.sum())
            logger.warning(
                "Detected %s duplicate price rows across %s trading days for %s. "
                "Keeping the latest row per day before forecasting.",
                duplicate_rows,
                duplicate_days,
                symbol,
            )
            df = df.drop_duplicates(subset=['ds'], keep='last')

        return df[['ds', 'y']].reset_index(drop=True)

    @staticmethod
    def _build_future_dataframe(model: Prophet, days: int) -> pd.DataFrame:
        """Build the next N business dates from the model's latest history row."""
        last_date = model.history['ds'].max()
        future_dates = pd.bdate_range(
            start=last_date + timedelta(days=1),
            periods=days,
            freq='B'
        )
        return pd.DataFrame({'ds': future_dates})

    @staticmethod
    def _get_model_dir(symbol: str) -> str:
        path = os.path.join(MODELS_DIR, symbol.upper())
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def train_model(db: Session, symbol: str, params: dict | None = None) -> dict:
        """
        Train a Pure Prophet model for a given ticker symbol.
        Uses ALL available data (no train/test split) for production forecasting.

        Returns metadata dict with training info and metrics.
        """
        symbol = symbol.upper()
        logger.info(f"Training Prophet model for {symbol}...")

        # 1. Fetch ticker
        ticker = ProphetService._get_ticker(db, symbol)
        if not ticker:
            raise ValueError(f"Ticker '{symbol}' not found in database")

        # 2. Fetch all historical prices
        stmt_prices = (
            select(DailyPrice)
            .where(DailyPrice.ticker_id == ticker.id)
            .order_by(DailyPrice.date.asc())
        )
        prices = list(db.scalars(stmt_prices).all())

        # 3. Build a clean training frame
        df = ProphetService._prepare_price_frame(prices, symbol)

        if len(df) < 60:
            raise ValueError(
                f"Not enough unique trading days for {symbol}: {len(df)} rows "
                f"(need at least 60 for reliable prediction)"
            )

        # 4. Train Prophet (Pure — no regressors)
        hp = params or DEFAULT_PARAMS
        model = Prophet(
            changepoint_prior_scale=hp['changepoint_prior_scale'],
            seasonality_prior_scale=hp['seasonality_prior_scale'],
            seasonality_mode=hp['seasonality_mode'],
            n_changepoints=hp['n_changepoints'],
            changepoint_range=hp['changepoint_range'],
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            holidays=VN_HOLIDAYS,
        )
        model.fit(df)

        # 5. Calculate in-sample metrics (last 60 days)
        eval_df = df.tail(60).copy()
        forecast_eval = model.predict(eval_df[['ds']])
        y_true = eval_df['y'].values
        y_pred = forecast_eval['yhat'].values
        mae = float(np.mean(np.abs(y_true - y_pred)))
        rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
        mape = float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)

        # 6. Save model
        model_dir = ProphetService._get_model_dir(symbol)
        model_path = os.path.join(model_dir, 'model.pkl')
        joblib.dump(model, model_path)

        # 7. Save metadata
        metadata = {
            'symbol': symbol,
            'trained_at': datetime.now().isoformat(),
            'data_rows': len(df),
            'date_range': {
                'start': df['ds'].min().strftime('%Y-%m-%d'),
                'end': df['ds'].max().strftime('%Y-%m-%d'),
            },
            'params': hp,
            'metrics': {'mae': round(mae, 4), 'rmse': round(rmse, 4), 'mape': round(mape, 2)},
        }
        meta_path = os.path.join(model_dir, 'metadata.json')
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ Model saved for {symbol} — MAE: {mae:.4f}, MAPE: {mape:.2f}%")
        return metadata

    @staticmethod
    def load_model(symbol: str) -> Prophet | None:
        """Load a trained Prophet model from disk."""
        model_path = os.path.join(
            ProphetService._get_model_dir(symbol.upper()), 'model.pkl'
        )
        if not os.path.exists(model_path):
            return None
        return joblib.load(model_path)

    @staticmethod
    def get_metadata(symbol: str) -> dict | None:
        """Load model metadata from disk."""
        meta_path = os.path.join(
            ProphetService._get_model_dir(symbol.upper()), 'metadata.json'
        )
        if not os.path.exists(meta_path):
            return None
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def predict(
        db: Session,
        symbol: str,
        days: int = 10,
        auto_train: bool = True,
    ) -> dict:
        """
        Predict future stock prices for N trading days.

        If auto_train=True and no model exists, trains one automatically.
        Returns dict with predictions, metrics, and model info.
        """
        symbol = symbol.upper()

        ticker = ProphetService._get_ticker(db, symbol)
        if not ticker:
            raise ValueError(f"Ticker '{symbol}' not found in database")

        latest_history_date = ProphetService._get_latest_price_date(db, ticker.id)
        if latest_history_date is None:
            raise ValueError(f"No historical prices found for {symbol}")

        # 1. Try to load existing model
        model = ProphetService.load_model(symbol)
        metadata = ProphetService.get_metadata(symbol)

        # 2. Auto-train if no model exists
        if model is None:
            if not auto_train:
                raise ValueError(f"No trained model for {symbol}. Train first.")
            logger.info(f"No model found for {symbol}, auto-training...")
            metadata = ProphetService.train_model(db, symbol)
            model = ProphetService.load_model(symbol)

        if model is None:
            raise RuntimeError(f"Failed to load model for {symbol}")

        model_history_end = ProphetService._get_model_history_end_date(model, metadata)
        if model_history_end is None or model_history_end < latest_history_date:
            if not auto_train:
                raise ValueError(
                    f"Stored model for {symbol} is stale. Latest DB date is {latest_history_date.isoformat()}, "
                    f"but the model only knows data through {model_history_end.isoformat() if model_history_end else 'unknown'}."
                )

            logger.info(
                "Model for %s is stale. Re-training with latest DB history (%s > %s).",
                symbol,
                latest_history_date.isoformat(),
                model_history_end.isoformat() if model_history_end else 'unknown',
            )
            metadata = ProphetService.train_model(db, symbol)
            model = ProphetService.load_model(symbol)

        if model is None:
            raise RuntimeError(f"Failed to reload model for {symbol}")

        if model.history['ds'].duplicated().any():
            if not auto_train:
                raise ValueError(
                    f"Stored model for {symbol} has duplicate training dates. Retrain the model first."
                )
            logger.warning(
                "Stored Prophet model for %s has duplicate training dates. Re-training from cleaned price history.",
                symbol,
            )
            metadata = ProphetService.train_model(db, symbol)
            model = ProphetService.load_model(symbol)

        if model is None:
            raise RuntimeError(f"Failed to reload model for {symbol}")

        # 3. Create future dataframe for N business days
        # Prophet's make_future_dataframe includes historical dates too
        # We only want future dates, so we'll build manually
        future_df = ProphetService._build_future_dataframe(model, days)

        # 4. Predict
        try:
            forecast = model.predict(future_df)
        except ValueError as exc:
            if auto_train and 'duplicate labels' in str(exc).lower():
                logger.warning(
                    "Prediction for %s failed because the stored model still had duplicate labels. "
                    "Retrying after re-training from cleaned history.",
                    symbol,
                )
                metadata = ProphetService.train_model(db, symbol)
                model = ProphetService.load_model(symbol)
                if model is None:
                    raise RuntimeError(f"Failed to reload model for {symbol}") from exc
                future_df = ProphetService._build_future_dataframe(model, days)
                forecast = model.predict(future_df)
            else:
                raise

        # 5. Get recent historical prices for chart context (last 60 trading days)
        history_data = []
        if ticker:
            stmt_prices = (
                select(DailyPrice)
                .where(DailyPrice.ticker_id == ticker.id)
                .order_by(DailyPrice.date.asc(), DailyPrice.id.asc())
            )
            prices = list(db.scalars(stmt_prices).all())
            history_df = ProphetService._prepare_price_frame(prices, symbol).tail(60)
            history_data = [{
                'date': row.ds.date().isoformat(),
                'close': float(row.y),
            } for row in history_df.itertuples(index=False)]

        # 6. Build response
        predictions = []
        last_known_price = history_data[-1]['close'] if history_data else None
        
        # Determine exchange price limits
        exchange = ticker.exchange.upper() if ticker and ticker.exchange else 'HOSE'
        if exchange == 'HNX':
            limit_pct = 0.10
        elif exchange == 'UPCOM':
            limit_pct = 0.15
        else:
            limit_pct = 0.07  # HOSE default

        for _, row in forecast.iterrows():
            pred_close = float(row['yhat'])
            lower = float(row['yhat_lower'])
            upper = float(row['yhat_upper'])

            if last_known_price is not None:
                # Apply Vietnamese market rules: ± limits based on previous close price
                floor_price = last_known_price * (1 - limit_pct)
                ceiling_price = last_known_price * (1 + limit_pct)
                
                pred_close = max(floor_price, min(ceiling_price, pred_close))
                lower = max(floor_price, min(ceiling_price, lower))
                upper = max(floor_price, min(ceiling_price, upper))
            
            # Ensure bounds are structurally sound
            lower = min(lower, pred_close)
            upper = max(upper, pred_close)

            # Round for output
            pred_close = round(pred_close, 2)
            lower = round(lower, 2)
            upper = round(upper, 2)

            trend = 'UP'
            if last_known_price is not None:
                trend = 'UP' if pred_close >= last_known_price else 'DOWN'

            predictions.append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'predicted_close': pred_close,
                'lower_bound': lower,
                'upper_bound': upper,
                'trend': trend,
            })
            last_known_price = pred_close  # chain reference price for multi-day forecast

        # 7. Save predictions to database for future improvement
        if ticker:
            try:
                # Use mape as a proxy for confidence if available
                confidence = None
                if metadata and 'metrics' in metadata:
                    confidence = metadata['metrics'].get('mape')
                
                # Add confidence to each dict if we want to save it
                for p in predictions:
                    p['confidence_score'] = confidence

                create_predictions(db, ticker.id, predictions, 'prophet_v2')
                logger.info(f"Saved {len(predictions)} predictions for {symbol} to database.")
            except Exception as e:
                logger.error(f"Error saving predictions for {symbol}: {str(e)}")

        return {
            'symbol': symbol,
            'version': 'prophet_v2',
            'trained_at': metadata.get('trained_at', '') if metadata else '',
            'metrics': metadata.get('metrics', {}) if metadata else {},
            'predictions': predictions,
            'history': history_data,
        }
