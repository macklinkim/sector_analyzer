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

        market_data = MarketData(
            indices=indices,
            sectors=sectors,
            economic_indicators=economic_indicators,
            momentum=momentum,
            relative_strength=relative_strength,
        )
        logger.info("Data Agent: collected %d indices, %d sectors, %d indicators",
                     len(indices), len(sectors), len(economic_indicators))
        return {"market_data": market_data}
    except Exception as e:
        logger.error("Data Agent failed: %s", e)
        return {"market_data": MarketData()}
    finally:
        await service.close()
