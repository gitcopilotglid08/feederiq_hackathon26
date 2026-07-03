class RecommendationAgent:
    """Merges NWA and capex results, ranks, and generates decision narrative."""

    def run(self, nwa_scored: list, capex_scored: list, base_summary: dict, assumptions: dict) -> dict:
        # Merge and rank all portfolios
        all_scored = nwa_scored + capex_scored
        all_scored.sort(key=lambda x: x["final_score"], reverse=True)

        # Remove internal summary from output
        ranking = []
        for s in all_scored:
            row = {k: v for k, v in s.items() if k != "alt_summary"}
            ranking.append(row)

        top = ranking[0] if ranking else None
        second = ranking[1] if len(ranking) > 1 else None

        # Check if NWA-only resolved all violations
        nwa_resolved = False
        if nwa_scored:
            best_nwa = nwa_scored[0]
            if "alt_summary" in best_nwa and best_nwa["alt_summary"]["grid_stress_score"] == 0:
                nwa_resolved = True

        memo = self._generate_memo(top, second, base_summary, assumptions, nwa_resolved)

        return {
            "ranking": ranking,
            "top_recommendation": top,
            "second_best": second,
            "nwa_resolved_all": nwa_resolved,
            "memo": memo,
        }

    def _generate_memo(self, top, second, base_summary, assumptions, nwa_resolved):
        lines = []
        lines.append("# FeederIQ Decision Memo")
        lines.append("")
        lines.append("## Scenario")
        lines.append(f"- Planning horizon: {assumptions['horizon_years']} years")
        lines.append(f"- Peak EV demand: {assumptions['peak_ev_mw']:.2f} MW")
        lines.append(f"- Peak solar generation: {assumptions['peak_solar_mw']:.2f} MW")
        lines.append(f"- Data center: {'Active' if assumptions['dc_active'] else 'Not yet online'} ({assumptions['dc_mw']} MW)")
        lines.append("")
        lines.append("## Baseline Assessment")
        lines.append(f"- Grid stress score: {base_summary['grid_stress_score']:.0f}")
        lines.append(f"- Undervoltage events: {base_summary['total_undervoltage_buses']}")
        lines.append(f"- Overvoltage events: {base_summary['total_overvoltage_buses']}")
        lines.append(f"- Line overloads: {base_summary['total_line_overloads']}")
        lines.append(f"- Transformer overloads: {base_summary['total_transformer_overloads']}")
        lines.append("")
        lines.append("## Recommendation")

        if nwa_resolved:
            lines.append("**Non-wires alternatives fully resolve all violations.** No capex required.")
        elif top and top.get("TransformerUpgrade", 0) == 0:
            lines.append("**Best option is NWA-only**, though some residual violations may remain.")
        else:
            lines.append("**A hybrid NWA + capex approach is recommended** to fully address violations.")

        if top:
            lines.append("")
            lines.append(f"### Top Recommendation: {top['portfolio_name']}")
            lines.append(f"- Final score: {top['final_score']}")
            lines.append(f"- Technical improvement: {top['technical_improvement_pct']}%")
            lines.append(f"- Cost score: {top['cost_score']}/10")
            lines.append(f"- Feasibility: {top['feasibility_score']}/10")
            lines.append(f"- Deployment speed: {top['deployment_score']}/10")

        if second:
            lines.append("")
            lines.append(f"### Second Best: {second['portfolio_name']}")
            lines.append(f"- Final score: {second['final_score']}")
            lines.append(f"- Technical improvement: {second['technical_improvement_pct']}%")

        return "\n".join(lines)
