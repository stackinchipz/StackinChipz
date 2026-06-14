/**
 * Self-contained HTML report with embedded Chart.js (via CDN) and a colorized
 * sensitivity table. No build step — open the file in any browser.
 */
import { writeFileSync } from 'fs';
import {
  AnalysisResult,
  SensitivityTable,
} from '../types';

const pct = (n: number): string => (isFinite(n) ? `${(n * 100).toFixed(2)}%` : 'n/a');
const usd = (n: number): string => `$${Math.round(n).toLocaleString('en-US')}`;
const usdSf = (n: number): string => `$${n.toFixed(2)}`;
const esc = (s: string): string =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function sensitivityTableHtml(table: SensitivityTable): string {
  const values = table.cells.map((c) => c.npvAdvantageOfBuying);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const color = (v: number): string => {
    // Red (buy worse) -> white -> green (buy better).
    if (v >= 0) {
      const t = max > 0 ? v / max : 0;
      const g = Math.round(120 + 80 * t);
      return `rgba(40, ${g}, 70, ${0.15 + 0.5 * t})`;
    }
    const t = min < 0 ? v / min : 0;
    return `rgba(200, 60, 60, ${0.15 + 0.5 * t})`;
  };

  const header =
    `<tr><th>Exit Cap \\ Disc</th>` +
    table.discountRates.map((d) => `<th>${pct(d)}</th>`).join('') +
    `</tr>`;

  const rows = table.exitCapRates
    .map((ec) => {
      const cells = table.discountRates
        .map((dr) => {
          const cell = table.cells.find(
            (c) =>
              Math.abs(c.exitCapRate - ec) < 1e-9 &&
              Math.abs(c.discountRate - dr) < 1e-9
          );
          const v = cell ? cell.npvAdvantageOfBuying : 0;
          return `<td style="background:${color(v)}">${usd(v)}</td>`;
        })
        .join('');
      return `<tr><th>${pct(ec)}</th>${cells}</tr>`;
    })
    .join('');

  return `
  <h3>Tax Growth ${pct(table.taxGrowthRate)} — NPV Advantage of Buying</h3>
  <table class="sens">${header}${rows}</table>`;
}

export class HtmlReporter {
  generate(result: AnalysisResult): string {
    const { subject, comparison, market, assumptions, sensitivity } = result;
    const { buy, lease } = comparison;

    const years = buy.cashFlows.map((c) => c.year);
    const buyNetCf = buy.cashFlows.map((c) => Math.round(c.netCashFlow));
    const buyNoi = buy.cashFlows.map((c) => Math.round(c.noi));
    const leasePayments = lease.cashFlows.map((c) => Math.round(c.leasePayment));
    const buyCum: number[] = [];
    buy.annualOwnershipCost.reduce((acc, v) => {
      const val = acc + v;
      buyCum.push(Math.round(val));
      return val;
    }, 0);
    const leaseCum: number[] = [];
    lease.annualLeaseCost.reduce((acc, v) => {
      const val = acc + v;
      leaseCum.push(Math.round(val));
      return val;
    }, 0);

    const recColor =
      comparison.recommendation === 'BUY'
        ? '#1f9d55'
        : comparison.recommendation === 'LEASE'
        ? '#2563eb'
        : '#b45309';

    const saleRows = market.normalizedSales
      .map(
        (s) => `<tr>
        <td>${esc(s.comp.id)}</td><td>${s.comp.buildingSqFt.toLocaleString()}</td>
        <td>${usdSf(s.pricePerSqFt)}</td><td>${pct(s.reportedCapRate)}</td>
        <td><b>${pct(s.adjustedCapRate)}</b></td><td>${usd(s.oldAnnualTax)}</td>
        <td>${usd(s.newProjectedTax)}</td></tr>`
      )
      .join('');

    const leaseRows = market.normalizedLeases
      .map(
        (l) => `<tr>
        <td>${esc(l.comp.id)}</td><td>${esc(l.comp.leaseType)}</td>
        <td>${usdSf(l.comp.leaseRatePerSqFtYr)}</td><td>${usdSf(l.nnnEquivalentRent)}</td>
        <td><b>${usdSf(l.subjectAdjustedRent)}</b></td><td>${usdSf(l.compTaxPerSqFt)}</td>
        <td>${usdSf(l.subjectTaxPerSqFt)}</td></tr>`
      )
      .join('');

    const sensHtml = sensitivity.map(sensitivityTableHtml).join('');

    return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>CRE Lease vs Buy — ${esc(subject.address)}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  :root { font-family: -apple-system, Segoe UI, Roboto, sans-serif; }
  body { margin: 0; background: #f6f7f9; color: #1a202c; }
  header { background: #0f172a; color: #fff; padding: 24px 32px; }
  header h1 { margin: 0 0 4px; font-size: 22px; }
  header p { margin: 2px 0; opacity: .85; font-size: 14px; }
  main { max-width: 1100px; margin: 0 auto; padding: 24px 32px 64px; }
  .rec { display:inline-block; padding:8px 16px; border-radius:8px; color:#fff;
         font-weight:700; background:${recColor}; margin: 8px 0; }
  .cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin:16px 0; }
  .card { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:14px 16px; }
  .card .label { font-size:12px; color:#64748b; text-transform:uppercase; letter-spacing:.04em; }
  .card .value { font-size:20px; font-weight:700; margin-top:4px; }
  table { border-collapse: collapse; width:100%; background:#fff; margin:10px 0 24px; font-size:14px; }
  th, td { border:1px solid #e2e8f0; padding:7px 10px; text-align:right; }
  th:first-child, td:first-child { text-align:left; }
  thead th, table.sens tr:first-child th { background:#f1f5f9; }
  h2 { margin-top:32px; border-bottom:2px solid #e2e8f0; padding-bottom:6px; }
  .chart-wrap { background:#fff; border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin:12px 0; }
  .rationale { background:#fffbeb; border:1px solid #fcd34d; border-radius:8px; padding:12px 16px; }
  footer { color:#64748b; font-size:12px; text-align:center; padding:24px; }
</style>
</head>
<body>
<header>
  <h1>Commercial Real Estate — Lease vs. Buy</h1>
  <p>${esc(subject.address)}</p>
  <p>${subject.buildingSqFt.toLocaleString()} SF ${esc(subject.propertyType)} · built ${subject.yearBuilt}
     · current tax ${usdSf(subject.taxContext.taxRatePerSqFt)}/SF
     · projected post-purchase tax ${usdSf(subject.taxContext.estimatedPostTransactionTax / subject.buildingSqFt)}/SF</p>
  <p>Generated ${esc(result.generatedAt)} · All cash flows are tax-inclusive.</p>
</header>
<main>
  <div class="rec">RECOMMENDATION: ${comparison.recommendation}</div>
  <div class="rationale">${esc(comparison.rationale)}</div>

  <div class="cards">
    <div class="card"><div class="label">Buy NPV Cost</div><div class="value">${usd(comparison.buyNpvCost)}</div></div>
    <div class="card"><div class="label">Lease NPV Cost</div><div class="value">${usd(comparison.leaseNpvCost)}</div></div>
    <div class="card"><div class="label">NPV Advantage of Buying</div><div class="value">${usd(comparison.npvAdvantageOfBuying)}</div></div>
    <div class="card"><div class="label">Differential IRR</div><div class="value">${pct(comparison.differentialIrr)}</div></div>
    <div class="card"><div class="label">Levered Buy IRR</div><div class="value">${pct(buy.irr)}</div></div>
    <div class="card"><div class="label">Break-Even Year</div><div class="value">${
      comparison.breakEvenYear ?? '>' + assumptions.holdingPeriodYears
    }</div></div>
  </div>

  <h2>Tax-Normalized Sale Comps</h2>
  <table>
    <thead><tr><th>ID</th><th>SF</th><th>$/SF</th><th>Reported Cap</th><th>Adjusted Cap</th><th>Old Tax</th><th>New Tax</th></tr></thead>
    <tbody>${saleRows}</tbody>
  </table>

  <h2>Tax-Normalized Lease Comps (NNN-equivalent)</h2>
  <table>
    <thead><tr><th>ID</th><th>Type</th><th>Base</th><th>NNN-equiv</th><th>Subj-adj</th><th>Comp Tax</th><th>Subj Tax</th></tr></thead>
    <tbody>${leaseRows}</tbody>
  </table>

  <h2>Cash Flows</h2>
  <div class="chart-wrap"><canvas id="cfChart" height="110"></canvas></div>
  <div class="chart-wrap"><canvas id="cumChart" height="110"></canvas></div>

  <h2>Sensitivity Tables</h2>
  ${sensHtml}
</main>
<footer>Generated by cre-analyzer with Claude Code. Estimates only — not investment advice.</footer>
<script>
  const years = ${JSON.stringify(years)};
  new Chart(document.getElementById('cfChart'), {
    type: 'bar',
    data: { labels: years, datasets: [
      { label: 'Buy Net Cash Flow', data: ${JSON.stringify(buyNetCf)}, backgroundColor: 'rgba(31,157,85,.7)' },
      { label: 'Buy NOI', data: ${JSON.stringify(buyNoi)}, backgroundColor: 'rgba(37,99,235,.5)' },
      { label: 'Lease Payment', data: ${JSON.stringify(leasePayments)}, backgroundColor: 'rgba(220,60,60,.6)' }
    ]},
    options: { responsive: true, plugins: { title: { display: true, text: 'Annual Cash Flows ($)' } } }
  });
  new Chart(document.getElementById('cumChart'), {
    type: 'line',
    data: { labels: years, datasets: [
      { label: 'Cumulative Ownership Cost', data: ${JSON.stringify(buyCum)}, borderColor: 'rgba(31,157,85,1)', fill:false },
      { label: 'Cumulative Lease Cost', data: ${JSON.stringify(leaseCum)}, borderColor: 'rgba(220,60,60,1)', fill:false }
    ]},
    options: { responsive: true, plugins: { title: { display: true, text: 'Cumulative Cost of Occupancy ($)' } } }
  });
</script>
</body>
</html>`;
  }

  write(result: AnalysisResult, path: string): void {
    writeFileSync(path, this.generate(result), 'utf-8');
  }
}
