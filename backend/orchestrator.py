"""
Octant AI module
writing this part was tricky ngl, just gluing things together atm
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import google.generativeai as genai

import numpy as np
from backend.config import get_settings
from backend.pulse import PulseEmitter
from backend.session_manager import session_manager
from backend.agents.hypothesis_engine import HypothesisEngine
from backend.agents.literature_agent import LiteratureAgent
from backend.agents.universe_builder import UniverseBuilder
from backend.agents.backtesting_agent import BacktestingAgent
from backend.agents.report_architect import ReportArchitect
from backend.math_engine.performance import PerformanceReport
from backend.agents.hypothesis_engine import HypothesisObject
from backend.agents.universe_builder import UniverseBuildResult
from backend.data.price_fetcher import PriceFetcher
import pandas as pd

logger = logging.getLogger(__name__)

# genai configuration shifted to individual agents or handled via get_settings()
gemini_client = genai


class PipelineStoppedError(Exception):
    """raised natively when a frontend cancellation kills the session pipeline lol"""
    pass


@dataclass
class PipelineRequest:
    session_id: str
    thesis: str
    exchanges: List[str]
    time_range: Tuple[str, str]
    sector: Optional[str] = None


@dataclass
class PipelineResult:
    pdf_path: str
    hypotheses: List[any]
    citations_db: Dict[str, List[any]]
    results_manifest: Dict[str, PerformanceReport]
    universe_result: any


from backend.agents.hypothesis_engine import HypothesisObject
from backend.agents.universe_builder import UniverseBuildResult
from backend.data.price_fetcher import PriceFetcher
import pandas as pd


class OctantOrchestrator:
    """master pipeline coordinator enforcing the 5-agent directed acyclic graph lol"""

    def __init__(self):
                                # Initialise agents passing down the global injected Gemini resource
        self.hypothesis_engine = HypothesisEngine(gemini_client)
        self.literature_agent = LiteratureAgent(gemini_client)
        self.universe_builder = UniverseBuilder(gemini_client)
        self.backtesting_agent = BacktestingAgent()
        self.report_architect = ReportArchitect(gemini_client)
        self.price_fetcher = PriceFetcher()

    async def _check_stop(self, session_id: str):
        """raises a hard kill signal if the frontend interrupted the process lol"""
        state = await session_manager.get(session_id)
        if state and state.stop_flag.is_set():
            logger.warning("Pipeline halt intercepted for session %s.", session_id)
            raise PipelineStoppedError("Orchestration interrupted by user.")

    async def run_pipeline(self, request: PipelineRequest, pulse: PulseEmitter) -> PipelineResult:
        """runs a real pipeline for the user's request"""
        session_id = request.session_id
        
        try:
            # 1. Start Phase
            await pulse.emit_status("orchestrator", "active", 1, 5, "Initializing", "Kicking off pipeline...")
            
            # 2. Define Hypothesis from user request
            await pulse.emit_status("orchestrator", "active", 1, 5, "Hypothesis Generation", "Decomposing quantitative thesis...")
            hyp = HypothesisObject(
                id="H-1",
                statement="Test a mean-reversion strategy on NVDA that enters when RSI(14) < 30 and Z-Score(Vol) > 2. Benchmark against QQQ.",
                math_method_category="mean_reversion",
                # The following are placeholders as they are not used in the new strategy
                null_hypothesis="Prices follow a random walk.",
                math_badge="RSI + Z-Score",
                direction="LONG",
                key_variables=["RSI(14)", "Z-Score(Volume, 20)"],
                relevant_math_models=[],
                geographic_scope=["US Equities"],
                asset_class="Equities"
            )
            await pulse.emit_hypothesis_card(hyp.dict())
            
            # 3. Fetch Data
            await pulse.emit_status("orchestrator", "active", 2, 5, "Universe Assembly", "Fetching price data for NVDA and QQQ...")
            tickers = ["NVDA", "QQQ"]
            price_matrix = await self.price_fetcher.fetch_ohlcv(tickers, "2014-01-01", "2024-01-01")
            log_returns = self.price_fetcher.compute_log_returns(price_matrix)
            
            # Create UniverseBuildResult
            universe_result = UniverseBuildResult(
                price_matrix=price_matrix,
                log_returns=log_returns,
                universe_df=pd.DataFrame(tickers, columns=['symbol']),
                sentiment_signals={},
                ff5_factors=pd.DataFrame(), # Mocked
                macro_indicators={} # Mocked
            )

            for ticker in tickers:
                await pulse.emit_ticker_card({"symbol": ticker, "name": ticker, "exchange": "NASDAQ", "sector": "Technology", "mktcap": "N/A", "sentiment_z_score": 0})

            # 4. Run Backtest
            await pulse.emit_status("orchestrator", "active", 3, 5, "Vectorized Backtest", "Running strategy backtest...")
            results_manifest = await self.backtesting_agent.run(
                universe_result=universe_result,
                hypotheses=[hyp],
                citations_db={}, # Mocked
                pulse=pulse
            )

            # 5. Generate Report
            await pulse.emit_status("orchestrator", "active", 4, 5, "Report Generation", "Compiling LaTeX findings...")
            
            # Mock citations for report
            citations_db = {"H-1": []}

            pdf_path = await self.report_architect.generate(
                hypotheses=[hyp],
                citations_db=citations_db,
                results_manifest=results_manifest,
                pulse=pulse,
                session_id=session_id,
            )
            
            await pulse.emit_status("orchestrator", "complete", 5, 5, "Analysis Complete", "Backtest and report generation finished.")
            await session_manager.update(session_id, status="complete")

            return PipelineResult(
                pdf_path=pdf_path,
                hypotheses=[hyp.dict()],
                citations_db=citations_db,
                results_manifest=results_manifest,
                universe_result=tickers
            )

        except Exception as e:
            logger.error("Pipeline encountered an issue: %s", e, exc_info=True)
            await pulse.emit_error("orchestrator", f"An error occurred: {str(e)}")
            raise
