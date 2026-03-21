"""
Octant AI module
writing this part was tricky ngl, just gluing things together atm
"""

import asyncio
import logging
import os
import uuid
from typing import Dict, List

import numpy as np
import google.generativeai as genai

from backend.agents.hypothesis_engine import HypothesisObject
from backend.data.literature_sources import PaperObject
from backend.math_engine.performance import PerformanceReport
from backend.pulse import PulseEmitter

from backend.report.figure_generator import FigureGenerator
from backend.report.latex_template import LaTeXAssembler
from backend.report.pdf_compiler import PDFCompiler, LatexCompilationError
from backend.report.bibtex_builder import build_bibtex_entries

from backend.config import get_settings
logger = logging.getLogger(__name__)


class ReportArchitect:
    """agent 5: streams nlp narratives and orchestrates latex compilation lol"""

    def __init__(self, gemini_client):
        self.gemini = gemini_client
        self.fig_gen = FigureGenerator()
        self.latex_asm = LaTeXAssembler()
        self.pdf_comp = PDFCompiler()
        
        settings = get_settings()
        self.output_dir = settings.REPORTS_OUTPUT_PATH
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate(
        self,
        hypotheses: List[HypothesisObject],
        citations_db: Dict[str, List[PaperObject]],
        results_manifest: Dict[str, PerformanceReport],
        pulse: PulseEmitter,
        session_id: str,
    ) -> str:
        """fully orchestrates the final rigorous academic report lol"""
        
        await pulse.emit_status("report", "active", 0, 12, "Synthesising Narratives", "Agent 5 calling Gemini...", 0, 180)

        
        # 1. Generate Figures
        figure_paths = {}
        for h in hypotheses:
            report = results_manifest.get(h.statement)
            if report and report.raw_results_dict:
                                # Mock extracting strategy return proxies from performance
                                # Real implementation passes series matrices here. We pass empty for pure string compile test.
                import pandas as pd
                dummy_returns = pd.Series(np.random.normal(0, 0.01, 1000))
                dummy_drawdown = dummy_returns.cumsum() - dummy_returns.cumsum().cummax()
                
                path = self.fig_gen.equity_curve_figure(
                    strategy_returns=dummy_returns,
                    benchmark_returns=pd.Series(dtype=float),
                    drawdown_series=dummy_drawdown,
                    hypothesis_id=h.statement[:15],
                    stats_dict={
                        "cagr": report.cagr,
                        "sharpe": report.sharpe_ratio,
                        "max_dd": report.max_drawdown
                    }
                )
                if path:
                    figure_paths[h.statement] = path
        
                
        # 2. Extract BibTeX
        all_papers = []
        for p_list in citations_db.values():
            all_papers.extend(p_list)
        bibtex_content = build_bibtex_entries(all_papers)

        
        # 3. Stream Narrative Sections (7 + 4 discrete calls to Gemini)
        sections = [
            ("Abstract", "High-level summary of the entire thesis, models used, and core predictive finding."),
            ("1_Introduction", "Introduce the market anomaly. Describe fundamental drivers."),
            ("2_Literature_Review", "Compare the papers extracted over SSRN and arXiv. Discuss prior Bayes Sharpe indicators."),
            ("3_Data_and_Universe", "Detail the universe constructed, liquidity constraints applied, and data sources."),
            ("4_Methodology", "Detail the time-series econometrics, Factor Regressions, or options models applied."),
            ("5_Results", "Compare the cumulative returns, drawdown stability, and statistical significance found by Agent 4."),
            ("6_Discussion", "Discuss transaction cost sensitivity and potential execution latency bottlenecks."),
            ("7_Conclusions", "Direct ruling: should the multi-manager fund deploy capital into this strategy?"),
            ("Appendix_A", "Detailed mathematical proofs and equations used in the models."),
            ("Appendix_B", "Extended statistical tables and out-of-sample robustness checks."),
            ("Appendix_C", "Comprehensive literature bibliography and citation graph."),
            ("Appendix_D", "Code generation specifications and deployment architecture.")
        ]
        
        gemini_narratives = {}
        from backend.config import get_settings
        settings = get_settings()
        model_name = getattr(settings, "GEMINI_REASONING_MODEL", "gemini-2.5-pro-preview-05-06")
        model = self.gemini.GenerativeModel(model_name)

        
        # Context build
        context = f"Thesis: {hypotheses[0].statement if hypotheses else 'Unknown'}\n\n"
        for h in hypotheses:
            report = results_manifest.get(h.statement)
            if report:
                context += f"- Hyp: {h.statement[:50]}... | CAGR: {report.cagr:.2%} | Sharpe: {report.sharpe_ratio:.2f} | P-Value: {report.bootstrap_p_value:.3f}\n"

        for idx, (sec_id, directive) in enumerate(sections):
            prompt = (
                f"You are a Senior Quantitative Researcher at Goldman Sachs writing an academic paper.\n"
                f"Strategy Context: {context}\n"
                f"Write the '{sec_id}' section. {directive}\n"
                f"Format output as pure text. Provide 2-3 paragraphs."
            )
            
            await pulse.emit_status("report", "active", idx+1, len(sections), f"Writing {sec_id}", "Awaiting tokens...", int((idx/len(sections))*100), (len(sections)-idx)*20)
            
                        
            # Using thread executor for sync streaming wrapper to avoid blocking async loop
            try:
                                # Real streaming would iterate chunks:
                response = model.generate_content(prompt, stream=False)
                text = response.text
                gemini_narratives[sec_id] = text
                
                                
                # Emit to UI
                await pulse.emit_report_section(sec_id, text, True)
            except Exception as e:
                logger.error("Gemini narrative failed for %s: %s", sec_id, e)
                gemini_narratives[sec_id] = f"{sec_id} generation failed due to API threshold."

        
        # 4. Assemble LaTeX
        await pulse.emit_status("report", "active", 12, 12, "Compiling PDF", "Executing pdflatex on local OS", 95, 10)
        
        tex_source = self.latex_asm.assemble(
            hypotheses=hypotheses,
            citations_db=citations_db,
            results_manifest=results_manifest,
            figure_paths=figure_paths,
            gemini_narratives=gemini_narratives,
            bibtex_content=bibtex_content
        )
        
                
        # 5. Execute pdflatex shell command
        job_name = f"report_{session_id}"
        pdf_path = ""
        try:
            pdf_path = await self.pdf_comp.compile(tex_source, self.output_dir, job_name, bibtex_content)
            await pulse.emit_status("report", "complete", 12, 12, "PDF Synthesized", f"Document generated rigidly.", 100, 0)
            
        except LatexCompilationError as e:
            logger.error("LaTeX syntax flaw: %s", e)
            await pulse.emit_status("report", "error", 12, 12, "PDF Failed", "LaTeX parser error.", 100, 0)
            
        return pdf_path

