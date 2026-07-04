# FeederIQ — Future Improvements & Data Roadmap

## Real-World Data Sources (for production deployment)

### Load Profiles

| Source | Description | Access | Status |
|--------|-------------|--------|--------|
| **openEDI (DOE)** | 91 load profiles × 35,040 pts (15-min, 1 year). Already in repo. | Public, BSD-3 | ✅ Available (toggle in app) |
| **NREL End-Use Load Profiles** | 550K+ building simulations covering all US climate zones, building types | Public, free download | 🔲 Integration ready |
| **Pecan Street Dataport** | Real smart meter data from 1000+ homes (Austin, TX; Boulder, CO) | Free academic signup | 🔲 Requires account |
| **EIA Form 861** | Utility-level annual load, customer counts, revenue by state | Public | 🔲 For growth validation |
| **EPRI LoadSEER** | Distribution-level load forecasting data | EPRI membership | 🔲 Requires license |

### EV Charging Data

| Source | Description | Access |
|--------|-------------|--------|
| **NREL EVI-Pro Lite** | EV charging demand by region, time of day, vehicle type | Public API |
| **DOE AFDC** | Charging station locations, utilization data | Public |
| **ChargePoint / Blink** | Real charging session data | Partnership required |

### Solar / DER Data

| Source | Description | Access |
|--------|-------------|--------|
| **NREL NSRDB** | Solar irradiance for any US location (TMY, actual year) | Public API |
| **NREL SAM** | PV system performance modeling | Public, free |
| **Tracking the Sun (LBNL)** | Installed PV system characteristics | Public |

### Grid / Utility Data

| Source | Description | Access |
|--------|-------------|--------|
| **FERC Form 1** | Utility financials, capex, transformer counts | Public |
| **EIA Form 860** | Generator/plant data | Public |
| **GridLAB-D models** | Synthetic but calibrated US feeders (PNNL) | Public |
| **Utility GIS exports** | Real feeder topology from specific utilities | Partnership required |

---

## Technical Improvements

### High Priority (for production)

1. **Real-time AMI integration** — Connect to utility SCADA/AMI for live load data
2. **GIS-based feeder import** — Load actual utility feeder models (CIM/CDPSM format)
3. **Multi-feeder analysis** — Evaluate multiple feeders in parallel, prioritize investment
4. **Stochastic scenarios** — Monte Carlo simulation with weather/EV uncertainty
5. **Financial model** — NPV/IRR calculation with utility cost of capital, depreciation schedules
6. **Regulatory filing support** — Auto-generate IRP/rate-case exhibits from results

### Medium Priority

7. **Weather correlation** — Link load profiles to temperature data for peak-day selection
8. **DER hosting capacity** — Calculate how much more solar/storage each bus can support
9. **Reliability metrics** — SAIDI/SAIFI/CAIDI calculation pre/post intervention
10. **Interconnection queue modeling** — Model multiple pending interconnection requests
11. **Battery degradation** — Account for BESS cycle life in multi-year planning
12. **Dynamic line rating** — Use weather data to adjust thermal limits in real-time

### Lower Priority (future vision)

13. **Digital twin sync** — Real-time model update from field measurements
14. **Automated PUC filing** — Generate regulatory exhibits in required format
15. **Portfolio optimization** — Replace brute-force enumeration with constrained optimization
16. **Multi-objective Pareto** — Show Pareto frontier instead of single weighted score
17. **Peer utility benchmarking** — Compare results against similar utilities (EIA data)

---

## LLM / Agentic Enhancements

### Currently Implemented
- Agent instruction files (markdown) drive agent behavior (configurable without code changes)
- LLM-powered decision memo generation via AWS Bedrock (Claude 3 Sonnet)
- LLM-powered constraint violation interpretation (natural language)
- Real data toggle: openEDI DOE profiles vs synthetic parametric curves
- Before/after grid stress visualization (red→green node map)
- Agent completion summaries showing actual findings
- Fallback to template when LLM unavailable

### Planned
1. **LLM-powered constraint interpretation** — Natural language explanation of violations
2. **LLM portfolio reasoning** — Explain WHY a portfolio was selected over alternatives
3. **Conversational planning** — Chat interface for iterative scenario refinement
4. **LLM-based sensitivity analysis** — Auto-identify which assumptions matter most
5. **Auto-report generation** — Full consulting-grade PDF report from LLM

---

## Data Already in Repository

The following data is available and can be toggled on:

```
ai_synthetic_data/profiles/
├── load_profiles/     ← 91 CSVs, 35040 rows each (15-min, 1 year)
│                        Source: openEDI/oedisi-ieee123 (DOE)
└── pv_profiles/       ← 14 PV + temperature CSVs
                         Source: openEDI/oedisi-ieee123 (DOE)
```

These represent measurement-calibrated load shapes for the IEEE 123-bus feeder.
To use: enable "Real Data Mode" toggle in the frontend sidebar.
