# backend/app/agents/data_agent.py
import logging

from langchain_core.runnables import RunnableConfig

from app.agents.state import MarketAnalysisState, MarketData
from app.services.yahoo_finance import YahooFinanceService

logger = logging.getLogger(__name__)


async def data_agent_node(state: MarketAnalysisState, config: RunnableConfig) -> dict:
    """LangGraph node: collect market data from Yahoo Finance."""
    logger.info("Data Agent: collecting market data (batch=%s)", state["batch_type"])

    service = YahooFinanceService()

    try:
        indices = await service.fetch_indices()
        sectors = await service.fetch_sector_etfs()

        try:
            economic_indicators = await service.fetch_economic_indicators()
        except Exception as e:
            logger.warning("Failed to fetch economic indicators: %s", e)
            economic_indicators = []

        momentum = {}
        relative_strength = {}
        for sector in sectors:
            symbol = sector["symbol"]
            try:
                m = await service.calculate_momentum(symbol)
                momentum[symbol] = m
            except Exception as e:
                logger.warning("Failed to calculate momentum for %s: %s", symbol, e)
                momentum[symbol] = {"momentum_1w": 0, "momentum_1m": 0, "momentum_3m": 0, "momentum_6m": 0, "momentum_1y": 0}
            try:
                rs = await service.calculate_relative_strength(symbol)
                relative_strength[symbol] = rs
            except Exception as e:
                logger.warning("Failed to calculate RS for %s: %s", symbol, e)
                relative_strength[symbol] = 0.0
            try:
                w52 = await service.calculate_52week_range(symbol)
                sector["week_52_low"] = w52["week_52_low"]
                sector["week_52_high"] = w52["week_52_high"]
            except Exception as e:
                logger.warning("Failed to calculate 52-week range for %s: %s", symbol, e)
                sector["week_52_low"] = 0
                sector["week_52_high"] = 0

        # Collect sector history (sparklines) and sector stocks (treemap)
        sector_history: list[dict] = []
        sector_stocks: list[dict] = []

        from app.services.sector_stocks import SECTOR_CONSTITUENTS

        for sector in sectors:
            symbol = sector["symbol"]
            try:
                hist = await service.fetch_historical(symbol, limit=30)
                for pt in hist:
                    sector_history.append({
                        "etf_symbol": symbol,
                        "trade_date": pt["date"],
                        "close": pt["close"],
                        "volume": pt.get("volume", 0),
                    })
            except Exception as e:
                logger.warning("Failed to fetch history for %s: %s", symbol, e)

        # Fetch sector stocks per sector (smaller batches for reliability)
        for sector in sectors:
            sym = sector["symbol"]
            constituents = SECTOR_CONSTITUENTS.get(sym, [])[:15]
            if not constituents:
                continue
            try:
                stocks = await service.fetch_sector_stocks(constituents)
                for st in stocks:
                    st["etf_symbol"] = sym
                sector_stocks.extend(stocks)
                logger.info("Fetched %d stocks for %s", len(stocks), sym)
            except Exception as e:
                logger.warning("Failed to fetch stocks for %s: %s", sym, e)

        market_data = MarketData(
            indices=indices,
            sectors=sectors,
            economic_indicators=economic_indicators,
            momentum=momentum,
            relative_strength=relative_strength,
            sector_history=sector_history,
            sector_stocks=sector_stocks,
        )
        logger.info("Data Agent: collected %d indices, %d sectors, %d indicators, %d history pts, %d stocks",
                     len(indices), len(sectors), len(economic_indicators),
                     len(sector_history), len(sector_stocks))
        return {"market_data": market_data}
    except Exception as e:
        logger.error("Data Agent failed: %s", e)
        return {"market_data": MarketData()}
    finally:
        await service.close()
