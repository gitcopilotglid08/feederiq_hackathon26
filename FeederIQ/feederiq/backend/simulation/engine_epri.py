"""
EPRI ckt5 simulation engine.
Full 24-hour QSTS simulation on the real EPRI Test Circuit 5 (981 primary buses, 2998 total buses).
"""
import math
import numpy as np
import opendssdirect as dss
from pathlib import Path

# EPRI ckt5 paths
EPRI_DIR = Path(__file__).resolve().parent.parent.parent.parent / "ai_synthetic_data" / "epri_ckt5"
EPRI_MASTER = EPRI_DIR / "Master_ckt5.dss"

# Asset placement on EPRI ckt5 primary buses
# Selected from 3-phase primary buses suitable for large loads
EV_BUSES_EPRI = ["8163", "8164", "829", "834", "44582", "8160"]
SOLAR_BUSES_EPRI = ["6584", "8113", "8124", "14880", "63707", "63657"]
DATA_CENTER_BUS_EPRI = "8163"

# Voltage thresholds (ANSI C84.1)
VOLTAGE_MIN_PU = 0.95
VOLTAGE_MAX_PU = 1.05
PRIMARY_KV_LN = 7.2  # 12.47 kV line-to-line / sqrt(3)
PRIMARY_KV_LL = 12.47


def compile_epri_feeder():
    """Compile EPRI ckt5 model."""
    if not EPRI_MASTER.exists():
        raise FileNotFoundError(f"EPRI Master DSS not found: {EPRI_MASTER}")
    dss.Basic.ClearAll()
    dss.Text.Command(f"Compile [{EPRI_MASTER.as_posix()}]")
    dss.Solution.Mode(0)
    dss.Solution.MaxIterations(100)


def run_epri_24hr_simulation(modified_profiles, portfolio, cap_mult_line=1.0, cap_mult_xf=1.0):
    """Run 24-hour simulation on EPRI ckt5 feeder."""
    compile_epri_feeder()

    # Capture baseline load values
    baseline_kw = {}
    baseline_kvar = {}
    for load_name in dss.Loads.AllNames():
        dss.Loads.Name(load_name)
        baseline_kw[load_name] = dss.Loads.kW()
        baseline_kvar[load_name] = dss.Loads.kvar()

    # Pre-add EV loads
    for i, bus in enumerate(EV_BUSES_EPRI):
        dss.Text.Command(
            f"New Load.EV_{i+1} Bus1={bus}.1 "
            f"Phases=1 Conn=Wye kV={PRIMARY_KV_LN} kW=0 kvar=0"
        )

    # Pre-add Solar generators
    for i, bus in enumerate(SOLAR_BUSES_EPRI):
        dss.Text.Command(
            f"New Generator.SOLAR_{i+1} Bus1={bus}.1 "
            f"Phases=1 kV={PRIMARY_KV_LN} kW=0 PF=1.0"
        )

    # Pre-add Data Center
    dss.Text.Command(
        f"New Load.DATACENTER Bus1={DATA_CENTER_BUS_EPRI}.1.2.3 "
        f"Phases=3 Conn=Wye kV={PRIMARY_KV_LL} kW=0 kvar=0"
    )

    results = []
    for _, row in modified_profiles.iterrows():
        # Scale existing loads
        mult = row["feeder_mult"]
        for load_name in baseline_kw:
            dss.Loads.Name(load_name)
            dss.Loads.kW(baseline_kw[load_name] * mult)
            dss.Loads.kvar(baseline_kvar[load_name] * mult)

        # Update EV
        ev_kw = (row["ev_mw"] * 1000) / len(EV_BUSES_EPRI) if EV_BUSES_EPRI else 0
        for i in range(len(EV_BUSES_EPRI)):
            dss.Loads.Name(f"EV_{i+1}")
            dss.Loads.kW(ev_kw)
            dss.Loads.kvar(0.20 * ev_kw)

        # Update solar
        solar_kw = (row["solar_mw"] * 1000) / len(SOLAR_BUSES_EPRI) if SOLAR_BUSES_EPRI else 0
        for i in range(len(SOLAR_BUSES_EPRI)):
            dss.Text.Command(f"Generator.SOLAR_{i+1}.kW={solar_kw:.2f}")

        # Update data center
        dc_kw = row["dc_mw"] * 1000
        dss.Loads.Name("DATACENTER")
        dss.Loads.kW(dc_kw)
        dss.Loads.kvar(0.25 * dc_kw)

        # Solve
        dss.Solution.Solve()
        converged = bool(dss.Solution.Converged())

        bus_v = dss.Circuit.AllBusMagPu()
        vmin = min(bus_v) if bus_v else float("nan")
        vmax = max(bus_v) if bus_v else float("nan")
        underv = sum(v < VOLTAGE_MIN_PU for v in bus_v)
        overv = sum(v > VOLTAGE_MAX_PU for v in bus_v)

        # Line overloads
        num_overloaded_lines = 0
        for line_name in dss.Lines.AllNames():
            dss.Lines.Name(line_name)
            dss.Circuit.SetActiveElement(f"Line.{line_name}")
            currents = dss.CktElement.CurrentsMagAng()
            mags = currents[0::2] if currents else []
            max_current = max(mags) if mags else 0.0
            norm_amps = dss.Lines.NormAmps() * cap_mult_line
            if norm_amps > 0 and (100 * max_current / norm_amps) > 100:
                num_overloaded_lines += 1

        # Transformer overloads
        num_overloaded_xf = 0
        for xf_name in dss.Transformers.AllNames():
            dss.Transformers.Name(xf_name)
            dss.Circuit.SetActiveElement(f"Transformer.{xf_name}")
            currents = dss.CktElement.CurrentsMagAng()
            mags = currents[0::2] if currents else []
            max_current = max(mags) if mags else 0.0
            kva = dss.Transformers.kVA()
            kv = dss.Transformers.kV()
            if kva > 0 and kv > 0:
                rated = (kva * 1000) / (math.sqrt(3) * kv * 1000) * cap_mult_xf
                if rated > 0 and (100 * max_current / rated) > 100:
                    num_overloaded_xf += 1

        results.append({
            "time": str(row["time"]),
            "converged": converged,
            "vmin_pu": round(vmin, 5),
            "vmax_pu": round(vmax, 5),
            "undervoltage_buses": underv,
            "overvoltage_buses": overv,
            "num_overloaded_lines": num_overloaded_lines,
            "num_overloaded_transformers": num_overloaded_xf,
        })

    return results
