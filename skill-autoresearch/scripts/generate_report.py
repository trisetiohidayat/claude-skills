#!/usr/bin/env python3
"""Generate HTML report for skill-autoresearch results."""
import json
import csv
from pathlib import Path


def generate_report(workspace: Path):
    state_file = workspace / "state.json"
    results_file = workspace / "results.tsv"
    output_file = workspace / "reports" / "report.html"

    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    rows = []
    if results_file.exists():
        content = results_file.read_text().strip()
        if content:
            lines = content.splitlines()
            header = lines[0].split("\t")
            for line in lines[1:]:
                cols = line.split("\t")
                cols += [''] * (len(header) - len(cols))  # pad short rows
                rows.append(dict(zip(header, cols)))

    best = state.get("best_score", "N/A")
    kept = state.get("improvements_kept", 0)
    discarded = state.get("improvements_discarded", 0)
    crashes = state.get("crashes", 0)
    loop_status = state.get("status", "unknown")
    additions_applied = state.get("additions_applied", [])
    total_additions = 14  # tracked across loop scripts

    status_label = {
        "running": ("RUNNING", "#2196f3", "#e3f2fd"),
        "complete": ("COMPLETE", "#9e9e9e", "#f5f5f5"),
        "optimal": ("OPTIMAL", "#4caf50", "#e8f5e9"),
        "paused": ("PAUSED", "#ff9800", "#fff3e0"),
        "stopped": ("STOPPED", "#f44336", "#ffebee"),
    }.get(loop_status, (loop_status.upper(), "#333", "#f5f5f5"))

    status_text, status_color, status_bg = status_label
    additions_remaining = total_additions - len(additions_applied)

    # Build score data for chart
    score_data = []
    for r in rows:
        cycle = r.get("commit", "?")[:9]
        try:
            score = float(r.get("skill_eval_score", 0))
        except (ValueError, TypeError):
            score = 0.0
        status = r.get("status", "")
        score_data.append(f'{{cycle:"{cycle}", score:{score:.3f}, status:"{status}"}}')

    skill_name = state.get("skill_name", "?")

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="30">
<title>Skill-Autoresearch: {skill_name}</title>
<style>
  body {{ font-family: system-ui; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }}
  h1 {{ border-bottom: 2px solid #333; padding-bottom: .5rem; }}
  h2 {{ margin-top: 2rem; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
  th, td {{ padding: .5rem; border: 1px solid #ccc; text-align: left; }}
  th {{ background: #f5f5f5; }}
  .keep {{ color: #4caf50; font-weight: bold; }}
  .discard {{ color: #f44336; }}
  .crash {{ color: #ff9800; font-weight: bold; }}
  .best {{ background: #e8f5e9; border: 2px solid #4caf50; border-radius: 8px; padding: 1rem; margin: 1rem 0; font-size: 1.2rem; font-weight: bold; }}
  .stats {{ background: #f5f5f5; padding: 1rem; border-radius: 4px; margin: 1rem 0; }}
  details {{ margin: .5rem 0; border: 1px solid #ccc; padding: .5rem; }}
  summary {{ cursor: pointer; font-weight: bold; }}
  pre {{ background: #f0f0f0; padding: .5rem; overflow-x: auto; font-size: .85rem; max-height: 400px; overflow-y: scroll; }}
  canvas {{ border: 1px solid #ccc; display: block; margin: 1rem 0; }}
  .chart-section {{ margin: 2rem 0; }}
  .legend {{ margin: .5rem 0; font-size: .9rem; }}
  .legend span {{ margin-right: 1rem; }}
  .legend .dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 4px; }}
  .loop-status {{
    display: inline-block;
    padding: 0.4rem 1rem;
    border-radius: 2rem;
    font-weight: bold;
    font-size: 0.9rem;
    border: 2px solid {status_color};
    color: {status_color};
    background: {status_bg};
    margin-left: 1rem;
  }}
  .header-row {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }}
  .header-meta {{
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
    font-size: 0.85rem;
    color: #666;
  }}
</style>
</head><body>
<div class="header-row">
  <h1 style="margin:0">Skill-Autoresearch: {skill_name}</h1>
  <span class="loop-status">&#x25CF; {status_text}</span>
</div>
<div class="header-meta">
  Started: {state.get('started_at', '?')[:16] if state.get('started_at') else '?'} &nbsp;|&nbsp;
  Last cycle: {state.get('last_cycle_at', '?')[:16] if state.get('last_cycle_at') else '?'} &nbsp;|&nbsp;
  Additions remaining: {additions_remaining} of {total_additions}
</div>

<div class="best" style="margin-top:1rem">Best skill_eval_score: {best} (cycle {state.get('best_commit', state.get('cycle', '?'))})</div>
<div class="stats">
  Total cycles: {state.get('cycle', 0)} |
  Kept: {kept} |
  Discarded: {discarded} |
  Crashes: {crashes} |
  Time budget: {state.get('time_budget_seconds', 300)}s/cycle
</div>

<div class="chart-section">
  <h2>Score Over Time</h2>
  <div class="legend">
    <span><span class="dot" style="background:#4caf50"></span>keep</span>
    <span><span class="dot" style="background:#f44336"></span>discard</span>
    <span><span class="dot" style="background:#ff9800"></span>crash</span>
  </div>
  <canvas id="chart" width="800" height="300"></canvas>
</div>

<h2>Experiment Log</h2>
<table>
  <thead>
    <tr><th>Commit</th><th>Score</th><th>Pass%</th><th>Coh%</th><th>Status</th><th>Experiment</th><th>Purpose</th></tr>
  </thead>
  <tbody>
"""
    for r in rows:
        status = r.get("status", "")
        cls = status
        html += f"""    <tr>
      <td>{r.get('commit', '')[:9]}</td>
      <td>{r.get('skill_eval_score', '')}</td>
      <td>{r.get('pass_rate', '')}</td>
      <td>{r.get('coherence', '')}</td>
      <td class="{cls}">{r.get('status', '')}</td>
      <td>{r.get('description', '')}</td>
      <td style="color:#555;font-size:0.9em">{r.get('purpose', '')}</td>
    </tr>
"""
    html += """  </tbody>
</table>

<script>
const data = [""" + ",".join(score_data) + """];
const canvas = document.getElementById('chart');
const ctx = canvas.getContext('2d');
const maxScore = 2.0;
const pad = 40;
const w = canvas.width - pad * 2;
const h = canvas.height - pad * 2;

// Draw grid lines
ctx.strokeStyle = '#ddd';
ctx.fillStyle = '#666';
ctx.font = '11px system-ui';
ctx.textAlign = 'right';
for (let i = 0; i <= 4; i++) {
  const y = pad + h * (1 - i / 4);
  ctx.beginPath(); ctx.moveTo(pad, y); ctx.lineTo(pad + w, y); ctx.stroke();
  ctx.fillText((maxScore * i / 4).toFixed(1), pad - 5, y + 4);
}

// Draw lines
for (let i = 0; i < data.length - 1; i++) {
  const x1 = pad + (w / Math.max(data.length - 1, 1)) * i;
  const y1 = pad + h * (1 - data[i].score / maxScore);
  const x2 = pad + (w / Math.max(data.length - 1, 1)) * (i + 1);
  const y2 = pad + h * (1 - data[i+1].score / maxScore);
  ctx.strokeStyle = data[i].status === 'keep' ? '#4caf50' :
                    data[i].status === 'crash' ? '#ff9800' : '#f44336';
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
}
// Draw points
for (let i = 0; i < data.length; i++) {
  const x = pad + (w / Math.max(data.length - 1, 1)) * i;
  const y = pad + h * (1 - data[i].score / maxScore);
  ctx.fillStyle = data[i].status === 'keep' ? '#4caf50' :
                  data[i].status === 'crash' ? '#ff9800' : '#f44336';
  ctx.beginPath(); ctx.arc(x, y, 5, 0, Math.PI*2); ctx.fill();
  ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.arc(x, y, 2, 0, Math.PI*2); ctx.fill();
}
</script>

<details>
  <summary>Metric Formula</summary>
  <pre>skill_eval_score = mean(assertion_pass_rate) + mean(assertion_coherence)

Where:
  assertion_pass_rate = (num_passed_assertions / total_assertions) * 1.0
  assertion_coherence = mean(coherence_scores)  (each 0.0 - 1.0)

skill_eval_score range: 0.0 to 2.0
  0.0 = all assertions failed, no coherence
  2.0 = all assertions passed, perfect coherence
</pre>
</details>

<p><em>Report auto-refreshes every 30 seconds. Last updated by skill-autoresearch loop.</em></p>
</body></html>"""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(html)
    print(f"Report written to {output_file}")
    return output_file


if __name__ == "__main__":
    import sys
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    generate_report(workspace)
