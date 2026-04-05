# backend/app/agents/data_agent.py
import logging

from langchain_core.runnables import RunnableConfig

from app.agents.state import MarketAnalysisState, MarketData
from app.services.eodhd import EODHDService
from app.config import Settings

logger = logging.getLogger(__name__)


async def data_agent_node(state: MarketAnalysisState, config: RunnableConfig) -> dict:
    """LangGraph node: collect market data from EODHD API."""
    logger.info("Data Agent: collecting market data (batch=%s)", state["batch_type"])

    settings = None
    try:
        settings = config.get("configurable", {}).get("settings")
    except (AttributeError, TypeError):
        pass
    if settings is None:
        settings = Settings()

    service = EODHDService(settings)

    try:
        indices = await service.fetch_indices()
        sectors = await service.fetch_sector_etfs()

        momentum = {}
        for sector in sectors:
            symbol = f"{sector['symbol']}.US"
            try:
                m = await service.calculate_momentum(symbol)
                momentum[sector["symbol"]] = m
            except Exception as e:
                logger.warning("Failed to calculate momentum for %s: %s", symbol, e)
                momentum[sector["symbol"]] = {"momentum_1w": 0, "momentum_1m": 0, "momentum_3m": 0, "momentum_6m": 0}

        market_data = MarketData(indices=indices, sectors=sectors, economic_indicators=[], momentum=momentum)
        logger.info("Data Agent: collected %d indices, %d sectors", len(indices), len(sectors))
        return {"market_data": market_data}
    except Exception as e:
        logger.error("Data Agent failed: %s", e)
        return {"market_data": MarketData()}
    finally:
        await service.close()
