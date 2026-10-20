/** Pretty-prints an AnalysisResult to the terminal via console.table. */
import { AnalysisResult } from '../types';

const pct = (n: number): string => (isFinite(n) ? `${(n * 100).toFixed(2)}%` : 'n/a');
const usd = (n: number): string =>
  `$${Math.round(n).toLocaleString('en-US')}`;
const usdSf = (n: number): string => `$${n.toFixed(2)}/SF`;

export class ConsoleReporter {
  render(result: AnalysisResult): void {
    const { subject, comparison, market, assumptions } = result;
    const { buy, lease } = comparison;

    console.log('\n=== CRE LEASE vs BUY ANALYSIS ===');
    console.log(`Subject: ${subject.address}`);
    console.log(
      `${subject.buildingSqFt.toLocaleString()} SF ${subject.propertyType}, built ${subject.yearBuilt}`
    );
    console.log(
      `Current tax ${usdSf(subject.taxContext.taxRatePerSqFt)} -> ` +
        `projected post-purchase ${usd(subject.taxContext.estimatedPostTransactionTax)} ` +
        `(${usdSf(subject.taxContext.estimatedPostTransactionTax / subject.buildingSqFt)})`
    );

    console.log('\n--- Tax-Normalized Sale Comps ---');
    console.table(
      market.normalizedSales.map((s) => ({
        id: s.comp.id,
        SF: s.comp.buildingSqFt,
        '$/SF': s.pricePerSqFt,
        'Reported Cap': pct(s.reportedCapRate),
        'Adjusted Cap': pct(s.adjustedCapRate),
        'Old Tax': usd(s.oldAnnualTax),
        'New Tax': usd(s.newProjectedTax),
      }))
    );

    console.log('\n--- Tax-Normalized Lease Comps (NNN-equivalent) ---');
    console.table(
      market.normalizedLeases.map((l) => ({
        id: l.comp.id,
        type: l.comp.leaseType,
        Base: usdSf(l.comp.leaseRatePerSqFtYr),
        'NNN-equiv': usdSf(l.nnnEquivalentRent),
        'Subj-adj': usdSf(l.subjectAdjustedRent),
        'Comp Tax': usdSf(l.compTaxPerSqFt),
        'Subj Tax': usdSf(l.subjectTaxPerSqFt),
      }))
    );

    console.log('\n--- Derived Market ---');
    console.table([
      {
        'Avg Adj $/SF': market.avgAdjustedPricePerSqFt.toFixed(2),
        'Avg Adj Cap': pct(market.avgAdjustedCapRate),
        'Avg All-in Rent': usdSf(market.avgSubjectAdjustedRent),
        'Derived Price': usd(market.derivedPurchasePrice),
      },
    ]);

    console.log('\n--- BUY Scenario ---');
    console.table([
      { Metric: 'Purchase Price', Value: usd(buy.purchasePrice) },
      { Metric: 'Closing Costs', Value: usd(buy.closingCosts) },
      { Metric: 'Loan Amount', Value: usd(buy.loanAmount) },
      { Metric: 'Equity', Value: usd(buy.equity) },
      { Metric: 'Annual Debt Service', Value: usd(buy.annualDebtService) },
      { Metric: 'Entry Cap', Value: pct(buy.entryCapRate) },
      { Metric: 'Exit Cap', Value: pct(buy.exitCapRate) },
      { Metric: 'Terminal Value (Yr 10)', Value: usd(buy.terminalValue) },
      { Metric: 'Net Sale Proceeds', Value: usd(buy.netSaleProceeds) },
      { Metric: 'Levered IRR', Value: pct(buy.irr) },
      { Metric: 'NPV @ disc rate', Value: usd(buy.npv) },
    ]);

    console.log('\n--- BUY Annual Cash Flows ---');
    console.table(
      buy.cashFlows.map((cf) => ({
        Yr: cf.year,
        NOI: usd(cf.noi),
        'Debt Svc': usd(cf.debtService),
        'Tax Shield': usd(cf.taxShield),
        'Prop Tax': usd(cf.propertyTax),
        'Net CF': usd(cf.netCashFlow),
        'Loan Bal': usd(cf.loanBalanceEnd),
      }))
    );

    console.log('\n--- LEASE Scenario ---');
    console.table([
      { Metric: 'Market Rent', Value: usdSf(lease.marketRentPerSqFt) },
      { Metric: 'Upfront Cost', Value: usd(lease.upfrontCost) },
      { Metric: 'NPV of Cost', Value: usd(lease.npvCost) },
    ]);

    console.log('\n--- COMPARISON ---');
    console.table([
      { Metric: 'Buy NPV Cost', Value: usd(comparison.buyNpvCost) },
      { Metric: 'Lease NPV Cost', Value: usd(comparison.leaseNpvCost) },
      { Metric: 'NPV Advantage of Buying', Value: usd(comparison.npvAdvantageOfBuying) },
      { Metric: 'Differential IRR', Value: pct(comparison.differentialIrr) },
      {
        Metric: 'Break-Even Year',
        Value: comparison.breakEvenYear ?? `>${assumptions.holdingPeriodYears}`,
      },
      { Metric: 'RECOMMENDATION', Value: comparison.recommendation },
    ]);
    console.log(`\n${comparison.rationale}\n`);

    if (result.sensitivity.length > 0) {
      const base = result.sensitivity.find(
        (t) => Math.abs(t.taxGrowthRate - assumptions.taxGrowthRate) < 1e-9
      ) ?? result.sensitivity[0];
      console.log(
        `--- Sensitivity: NPV Advantage of Buying (tax growth ${pct(base.taxGrowthRate)}) ---`
      );
      console.log('rows = exit cap, cols = discount rate');
      const grid: Record<string, Record<string, string>> = {};
      for (const cell of base.cells) {
        const rowKey = pct(cell.exitCapRate);
        const colKey = pct(cell.discountRate);
        grid[rowKey] = grid[rowKey] ?? {};
        grid[rowKey][colKey] = usd(cell.npvAdvantageOfBuying);
      }
      console.table(grid);
    }
  }
}
