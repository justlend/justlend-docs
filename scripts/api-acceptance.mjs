#!/usr/bin/env node
/**
 * JustLend public-API agent acceptance run.
 *
 * Exercises the anonymous GET read endpoints of https://openapi.just.network
 * end-to-end and asserts the documented contract:
 *   - success + business errors both arrive as HTTP 200,
 *   - V1 success code = 0 / "SUCCESS", V2 success code = 200 / "Success" (+ timestamp),
 *   - decimal quantities are JSON strings,
 *   - key response shapes match docs/developers/apis.md and
 *     docs/developers/apis/justlend_apis.yaml.
 *
 * Usage:  node scripts/api-acceptance.mjs
 * Exit code 0 = all checks passed. Results feed docs/developers/apis/agent-acceptance.md.
 *
 * Requires Node >= 18 (global fetch). Read-only; sends ~8 GET requests once.
 */

const BASE = process.env.JUSTLEND_API_BASE ?? 'https://openapi.just.network';
const DECIMAL_STR = /^-?\d+(\.\d+)?$/;
const HEX32 = /^0x[0-9a-fA-F]{64}$/;

const results = [];

async function probe(name, path, checks) {
  const url = `${BASE}${path}`;
  const failures = [];
  let httpStatus = null;
  let body = null;
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(20_000) });
    httpStatus = res.status;
    body = await res.json();
    for (const [label, fn] of Object.entries(checks)) {
      try {
        if (!fn(body, httpStatus)) failures.push(label);
      } catch (e) {
        failures.push(`${label} (threw: ${e.message})`);
      }
    }
  } catch (e) {
    failures.push(`request failed: ${e.message}`);
  }
  results.push({ name, path, httpStatus, pass: failures.length === 0, failures });
  return body;
}

const isPlainObject = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);

// ---------- V1 anonymous endpoints ----------

await probe('V1 market list', '/lend/jtoken', {
  'HTTP 200': (_b, s) => s === 200,
  'code === 0': (b) => b.code === 0,
  'message === "SUCCESS"': (b) => b.message === 'SUCCESS',
  'tokenList is a non-trivial array': (b) => Array.isArray(b.data?.tokenList) && b.data.tokenList.length >= 20,
  'decimal fields are strings (supplyRate, cash, exchangeRate)': (b) => {
    const t = b.data.tokenList[0];
    return [t.supplyRate, t.cash, t.exchangeRate].every((v) => typeof v === 'string' && DECIMAL_STR.test(v));
  },
  'borrowIndex is an integer string (BigInt-safe)': (b) => {
    const v = b.data.tokenList[0].borrowIndex;
    return typeof v === 'string' && /^\d+$/.test(v) && BigInt(v) >= 0n;
  },
  'underlyingDecimal is a JSON integer': (b) => Number.isInteger(b.data.tokenList[0].underlyingDecimal),
  'no fabricated fields (underlyingPriceInUsd/apy absent)': (b) => {
    const t = b.data.tokenList[0];
    return !('underlyingPriceInUsd' in t) && !('apy' in t);
  },
});

await probe('V1 sTRX + Energy Rental dashboard', '/lend/strx', {
  'HTTP 200': (_b, s) => s === 200,
  'code === 0': (b) => b.code === 0,
  'stakeInfo.reserves present as decimal string (renamed from "reserse")': (b) =>
    typeof b.data?.stakeInfo?.reserves === 'string' && DECIMAL_STR.test(b.data.stakeInfo.reserves),
  'stakeInfo.decimal serialized as string': (b) => b.data.stakeInfo.decimal === '18',
  'rentInfo decimal strings': (b) =>
    typeof b.data?.rentInfo?.priceFor10KEnergByRent === 'string' &&
    DECIMAL_STR.test(b.data.rentInfo.priceFor10KEnergByRent),
});

await probe('V1 mining APY map', '/mining/apy', {
  'HTTP 200': (_b, s) => s === 200,
  'code === 0': (b) => b.code === 0,
  'one key per market (>= 20)': (b) => isPlainObject(b.data) && Object.keys(b.data).length >= 20,
  'values are { USDD: "<decimal string>" }': (b) =>
    Object.values(b.data).every((m) => typeof m?.USDD === 'string' && DECIMAL_STR.test(m.USDD)),
});

await probe('V1 high-risk account list', '/justlend/liquidate/highRiskAccountList', {
  'HTTP 200': (_b, s) => s === 200,
  'code === 0': (b) => b.code === 0,
  'jtokens is a plain object map (not an array)': (b) =>
    isPlainObject(b.data?.jtokens) && Object.values(b.data.jtokens).every((v) => typeof v === 'string'),
  'updateTime is epoch-ms integer': (b) => Number.isInteger(b.data.updateTime) && b.data.updateTime > 1_600_000_000_000,
  'accounts array with string risk/USD fields + integer liquidateStatusStartTime': (b) => {
    if (!Array.isArray(b.data.accounts)) return false;
    if (b.data.accounts.length === 0) return true; // empty snapshot is valid
    const a = b.data.accounts[0];
    return (
      typeof a.borrower === 'string' &&
      typeof a.risk === 'string' && DECIMAL_STR.test(a.risk) &&
      typeof a.totalBorrowUsd === 'string' &&
      Number.isInteger(a.liquidateStatusStartTime) &&
      Array.isArray(a.collateralTokenList) &&
      Array.isArray(a.borrowTokenList)
    );
  },
});

// ---------- V2 anonymous endpoints ----------

await probe('V2 vault list', '/v2/index/vault/list', {
  'HTTP 200': (_b, s) => s === 200,
  'code === 200 (V2 success code)': (b) => b.code === 200,
  'message === "Success"': (b) => b.message === 'Success',
  'top-level timestamp (epoch ms)': (b) => Number.isInteger(b.timestamp) && b.timestamp > 1_600_000_000_000,
  'allVaults.list is an array': (b) => Array.isArray(b.data?.allVaults?.list),
  'vault entry shape (address + string tvl/apy + arrays)': (b) => {
    const v = b.data.allVaults.list[0];
    return (
      typeof v?.vaultAddress === 'string' &&
      typeof v.tvl === 'string' && DECIMAL_STR.test(v.tvl) &&
      typeof v.apy === 'string' &&
      Array.isArray(v.tags) && Array.isArray(v.markets) && Array.isArray(v.allocations)
    );
  },
  'user-scoped fields null without address': (b) => {
    const v = b.data.allVaults.list[0];
    return v.userSupplyUsd === null && v.userSupplyAmount === null;
  },
});

await probe('V2 market list', '/v2/index/market/list', {
  'HTTP 200': (_b, s) => s === 200,
  'code === 200 (V2 success code)': (b) => b.code === 200,
  'allMarkets is an array (key is allMarkets, not allMarket)': (b) => Array.isArray(b.data?.allMarkets),
  'market id is 0x…bytes32 and lltv a decimal string': (b) => {
    const m = b.data.allMarkets[0];
    return HEX32.test(m?.id ?? '') && typeof m.lltv === 'string' && DECIMAL_STR.test(m.lltv);
  },
  'user-scoped fields null without address (ltv/risk/loanAmount)': (b) => {
    const m = b.data.allMarkets[0];
    return m.ltv === null && m.risk === null && m.loanAmount === null;
  },
});

// ---------- error-contract probes ----------

await probe('V1 error contract (unknown path)', '/lend/nonExistentXYZ', {
  'HTTP 200 even for business errors': (_b, s) => s === 200,
  'code === 404 in body': (b) => b.code === 404,
  'message explains the error': (b) => typeof b.message === 'string' && b.message.length > 0,
  'data omitted on V1 errors': (b) => !('data' in b),
});

await probe('V2 error contract (missing params)', '/v2/vault/position', {
  'HTTP 200 even for business errors': (_b, s) => s === 200,
  'code !== 200 (e.g. 202 invalid parameters)': (b) => Number.isInteger(b.code) && b.code !== 200,
  'data is null on V2 errors': (b) => b.data === null,
  'timestamp still present': (b) => Number.isInteger(b.timestamp),
});

// ---------- report ----------

const pad = (s, n) => String(s).padEnd(n);
let failed = 0;
console.log(`\nJustLend API agent acceptance — ${new Date().toISOString()} — base ${BASE}\n`);
for (const r of results) {
  const status = r.pass ? 'PASS' : 'FAIL';
  if (!r.pass) failed++;
  console.log(`${pad(status, 5)} ${pad(r.name, 42)} ${pad(`HTTP ${r.httpStatus ?? '—'}`, 9)} ${r.path}`);
  for (const f of r.failures) console.log(`      ✗ ${f}`);
}
console.log(`\n${results.length - failed}/${results.length} endpoint probes passed.`);
process.exit(failed === 0 ? 0 : 1);
