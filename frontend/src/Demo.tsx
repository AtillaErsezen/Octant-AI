import { useState, useEffect } from 'react';
import LeftPanel from './components/LeftPanel/index';
import CenterPanel from './components/CenterPanel/index';
import RightPanel from './components/RightPanel/index';
import './index.css';

export default function Demo() {
    const [pipelineStatus, setPipelineStatus] = useState<string>("idle");
    const [hypotheses, setHypotheses] = useState<any[]>([]);
    const [citations, setCitations] = useState<any[]>([]);
    const [tickers, setTickers] = useState<any[]>([]);
    const [metricsMatrix, setMetricsMatrix] = useState<any[]>([]);
    const [activityLog, setActivityLog] = useState<any[]>([]);
    const [agentStatuses, setAgentStatuses] = useState<any>({});

    const runDemo = async () => {
        setPipelineStatus("active");
        setHypotheses([]);
        setCitations([]);
        setTickers([]);
        setMetricsMatrix([]);
        setActivityLog([]);
        setAgentStatuses({});

        const log = (msg: string, type: string = "status", agent: string = "orchestrator", payload: any = {}) => {
            const event = {
                type: "PULSE",
                payload_type: type,
                agent: agent,
                payload: payload,
                message: { title: msg, subtitle: "Simulating high-performance compute..." },
                timestamp: new Date().toISOString()
            };
            setActivityLog(prev => [...prev, event]);
            if (type === "status") {
                setAgentStatuses((prev: any) => ({ ...prev, [agent]: payload }));
            }
            return event;
        };

        // 1. Initializing
        log("Initializing Pipeline...", "status", "orchestrator", { status: "active" });
        await new Promise(r => setTimeout(r, 1500));

        // 2. Hypothesis
        log("Generating Hypothesis...", "status", "hypothesis_engine", { status: "active" });
        await new Promise(r => setTimeout(r, 1000));
        const h1 = {
            id: "H-DEMO",
            statement: "Post-earnings drift exploitation on high-volume technology gaps.",
            null_hypothesis: "Prices follow a random walk with no significant drift recovery.",
            math_badge: "OU-Process",
            direction: "LONG",
            key_variables: ["Volatility (30d)", "Earnings Surprise %", "Volume Spike"],
            relevant_math_models: ["OU-Process", "Kalman Filter"],
            geographic_scope: "US Equities",
            asset_class: "Equities"
        };
        setHypotheses([h1]);
        log("Hypothesis Locked", "hypothesis_card", "hypothesis_engine", h1);
        await new Promise(r => setTimeout(r, 1000));

        // 3. Citations
        log("Literature Search...", "status", "literature", { status: "active" });
        await new Promise(r => setTimeout(r, 2000));
        const p1 = { 
            title: "Yield Curve Inversions and Equity Risk Premia", 
            authors: "D. Smith", 
            year: 2023, 
            journal: "Journal of Financial Economics",
            relevance: "High",
            supports: true,
            abstract_summary: "A deep dive into cross-sectional return predictability.",
            novelty_score: 94 
        };
        setCitations([p1]);
        log("Citation Found", "citation_card", "literature", p1);

        // 4. Universe
        log("Screening Universe...", "status", "universe", { status: "active" });
        await new Promise(r => setTimeout(r, 1500));
        const t1 = { 
            symbol: "NVDA", 
            name: "Nvidia", 
            exchange: "NASDAQ",
            sector: "Technology",
            mktcap: "2.2T", 
            sentiment_z_score: 2.8 
        };
        setTickers([t1]);
        log("Ticker Qualified", "ticker_card", "universe", t1);

        // 5. Backtest
        log("Running Backtest...", "status", "backtest", { status: "active" });
        await new Promise(r => setTimeout(r, 3000));
        const m1 = { 
            sharpe_ratio: 3.12, 
            sortino_ratio: 3.45,
            cagr: 0.42, 
            max_drawdown: -0.08,
            win_rate: 0.68,
            volatility: 0.15
        };
        setMetricsMatrix([m1]);
        log("Backtest Complete", "metric_result", "backtest", { hypothesis_id: "H-DEMO", ...m1 });

        // Final
        setPipelineStatus("complete");
        log("Analysis Complete", "status", "orchestrator", { status: "complete" });
    };

    return (
        <div className="h-screen w-full bg-[#0a0a0c] text-slate-200 overflow-hidden flex flex-col font-outfit">
            {/* Header */}
            <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-[#0a0a0c]/80 backdrop-blur-md z-50">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-white shadow-[0_0_20px_rgba(37,99,235,0.4)]">O</div>
                    <span className="text-xl font-bold tracking-tight text-white">Octant <span className="text-blue-500">AI</span></span>
                    <span className="ml-4 px-2 py-0.5 rounded border border-yellow-500/50 text-yellow-500 text-[10px] font-bold uppercase tracking-widest">Demo Mode (Offline)</span>
                </div>
                <button 
                    onClick={runDemo}
                    disabled={pipelineStatus === "active"}
                    className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-6 py-2 rounded-lg font-bold transition-all shadow-lg shadow-blue-600/20 flex items-center gap-2"
                >
                    {pipelineStatus === "active" ? "Calculating..." : "🚀 Deploy Analytics"}
                </button>
            </header>

            <main className="flex-1 flex overflow-hidden">
                <LeftPanel 
                    activityLog={activityLog} 
                    agentStatuses={agentStatuses} 
                />
                <CenterPanel 
                    hypotheses={hypotheses}
                    citations={citations}
                    tickers={tickers}
                />
                <RightPanel 
                    metricsMatrix={metricsMatrix}
                    reportOutline={[]}
                    pdfUrl={null}
                />
            </main>
        </div>
    );
}
