#!/usr/bin/env node
/**
 * JustLend public-API agent acceptance run.
 *
 * Exercises anonymous GET endpoints at https://openapi.just.network and locks
 * the documented response contract, canonical 24-market inventory, account
 * pagination defaults, numeric formats, and V1/V2 business-error envelopes.
 *
 * Usage:
 *   node scripts/api-acceptance.mjs
 *   node scripts/api-acceptance.mjs --json
 *
 * Exit code 0 = every check passed. Node >= 18 is required (global fetch).
 * Read-only; sends nine GET requests once.
 */

import { readFile } from 'node:fs/promises';

const BASE = process.env.JUSTLEND_API_BASE ?? 'https://openapi.just.network';
const JSON_MODE = process.argv.includes('--json');
const DECIMAL_STR = /^-?\d+(\.\d+)?$/;
const HEX32 = /^0x[0-9a-fA-F]{64}$/;
const contracts = JSON.parse(
  await readFile(new URL('../docs/developers/contracts.json', import.meta.url), 'utf8'),
);
const canonicalMarkets = Object.values(contracts.networks.mainnet.jtokens);
const canonicalSymbols = new Set(canonicalMarkets.map((market) => market.symbol));
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
    for (const [label, check] of Object.entries(checks)) {
      try {
        if (!check(body, httpStatus)) failures.push(label);
      } catch (error) {
        failures.push(`${label} (threw: ${error.message})`);
      }
    }
  } catch (error) {
    failures.push(`request failed: ${error.message}`);
  }
  results.push({ name, path, httpStatus, pass: failures.length === 0, failures });
  return body;
}

const isPlainObject = (value) =>
  value !== null && typeof value === 'object' && !Array.isArray(value);

// ---------- V1 anonymous endpoints ----------

await probe('V1 market list', '/lend/jtoken', {
  'HTTP 200': (_body, status) => status === 200,
  'code === 0': (body) => body.code === 0,
  'message === "SUCCESS"': (body) => body.message === 'SUCCESS',
  [`tokenList matches canonical ${canonicalMarkets.length}-market directory`]: (body) =>
    Array.isArray(body.data?.tokenList) && body.data.tokenList.length === canonicalMarkets.length,
  'every canonical symbol is present, including jU': (body) => {
    const actual = new Set(body.data?.tokenList?.map((token) => token.symbol) ?? []);
    return actual.has('jU') && [...canonicalSymbols].every((symbol) => actual.has(symbol));
  },
  'decimal fields are strings (supplyRate, cash, exchangeRate)': (body) => {
    const token = body.data.tokenList[0];
    return [token.supplyRate, token.cash, token.exchangeRate]
      .every((value) => typeof value === 'string' && DECIMAL_STR.test(value));
  },
  'borrowIndex is an integer string (BigInt-safe)': (body) => {
    const value = body.data.tokenList[0].borrowIndex;
    return typeof value === 'string' && /^\d+$/.test(value) && BigInt(value) >= 0n;
  },
  'underlyingDecimal is a JSON integer': (body) =>
    Number.isInteger(body.data.tokenList[0].underlyingDecimal),
  'no fabricated fields (underlyingPriceInUsd/apy absent)': (body) => {
    const token = body.data.tokenList[0];
    return !('underlyingPriceInUsd' in token) && !('apy' in token);
  },
});

await probe('V1 global account pagination', '/lend/account', {
  'HTTP 200': (_body, status) => status === 200,
  'code === 0': (body) => body.code === 0,
  'addresses filter is optional': (body) => Array.isArray(body.data?.list),
  'omitted pageSize defaults to 50 rows': (body) => body.data?.list?.length === 50,
  'pagination totals are positive integers': (body) =>
    Number.isInteger(body.data?.totalCount) && body.data.totalCount > 50 &&
    Number.isInteger(body.data?.totalPage) && body.data.totalPage > 1,
});

await probe('V1 sTRX + Energy Rental dashboard', '/lend/strx', {
  'HTTP 200': (_body, status) => status === 200,
  'code === 0': (body) => body.code === 0,
  'stakeInfo.reserves present as decimal string (renamed from "reserse")': (body) =>
    typeof body.data?.stakeInfo?.reserves === 'string' &&
    DECIMAL_STR.test(body.data.stakeInfo.reserves),
  'stakeInfo.decimal serialized as string': (body) => body.data.stakeInfo.decimal === '18',
  'rentInfo decimal strings': (body) =>
    typeof body.data?.rentInfo?.priceFor10KEnergByRent === 'string' &&
    DECIMAL_STR.test(body.data.rentInfo.priceFor10KEnergByRent),
});

await probe('V1 mining APY map', '/mining/apy', {
  'HTTP 200': (_body, status) => status === 200,
  'code === 0': (body) => body.code === 0,
  'one key per market (>= 20)': (body) =>
    isPlainObject(body.data) && Object.keys(body.data).length >= 20,
  'values are { USDD: "<decimal string>" }': (body) =>
    Object.values(body.data).every((market) =>
      typeof market?.USDD === 'string' && DECIMAL_STR.test(market.USDD)),
});

await probe('V1 high-risk account list', '/justlend/liquidate/highRiskAccountList', {
  'HTTP 200': (_body, status) => status === 200,
  'code === 0': (body) => body.code === 0,
  'jtokens is a plain object map (not an array)': (body) =>
    isPlainObject(body.data?.jtokens) &&
    Object.values(body.data.jtokens).every((value) => typeof value === 'string'),
  'updateTime is epoch-ms integer': (body) =>
    Number.isInteger(body.data.updateTime) && body.data.updateTime > 1_600_000_000_000,
  'accounts array with string risk/USD fields + integer liquidateStatusStartTime': (body) => {
    if (!Array.isArray(body.data.accounts)) return false;
    if (body.data.accounts.length === 0) return true;
    const account = body.data.accounts[0];
    return (
      typeof account.borrower === 'string' &&
      typeof account.risk === 'string' && DECIMAL_STR.test(account.risk) &&
      typeof account.totalBorrowUsd === 'string' &&
      Number.isInteger(account.liquidateStatusStartTime) &&
      Array.isArray(account.collateralTokenList) &&
      Array.isArray(account.borrowTokenList)
    );
  },
});

// ---------- V2 anonymous endpoints ----------

await probe('V2 vault list', '/v2/index/vault/list', {
  'HTTP 200': (_body, status) => status === 200,
  'code === 200 (V2 success code)': (body) => body.code === 200,
  'message === "Success"': (body) => body.message === 'Success',
  'top-level timestamp (epoch ms)': (body) =>
    Number.isInteger(body.timestamp) && body.timestamp > 1_600_000_000_000,
  'allVaults.list is an array': (body) => Array.isArray(body.data?.allVaults?.list),
  'vault entry shape (address + string tvl/apy + arrays)': (body) => {
    const vault = body.data.allVaults.list[0];
    return (
      typeof vault?.vaultAddress === 'string' &&
      typeof vault.tvl === 'string' && DECIMAL_STR.test(vault.tvl) &&
      typeof vault.apy === 'string' &&
      Array.isArray(vault.tags) && Array.isArray(vault.markets) &&
      Array.isArray(vault.allocations)
    );
  },
  'user-scoped fields null without address': (body) => {
    const vault = body.data.allVaults.list[0];
    return vault.userSupplyUsd === null && vault.userSupplyAmount === null;
  },
});

await probe('V2 market list', '/v2/index/market/list', {
  'HTTP 200': (_body, status) => status === 200,
  'code === 200 (V2 success code)': (body) => body.code === 200,
  'allMarkets is an array (key is allMarkets, not allMarket)': (body) =>
    Array.isArray(body.data?.allMarkets),
  'market id is 0x…bytes32 and lltv a decimal string': (body) => {
    const market = body.data.allMarkets[0];
    return HEX32.test(market?.id ?? '') &&
      typeof market.lltv === 'string' && DECIMAL_STR.test(market.lltv);
  },
  'user-scoped fields null without address (ltv/risk/loanAmount)': (body) => {
    const market = body.data.allMarkets[0];
    return market.ltv === null && market.risk === null && market.loanAmount === null;
  },
});

// ---------- error-contract probes ----------

await probe('V1 error contract (unknown path)', '/lend/nonExistentXYZ', {
  'HTTP 200 even for business errors': (_body, status) => status === 200,
  'code === 404 in body': (body) => body.code === 404,
  'message explains the error': (body) =>
    typeof body.message === 'string' && body.message.length > 0,
  'data omitted on V1 errors': (body) => !('data' in body),
});

await probe('V2 error contract (missing params)', '/v2/vault/position', {
  'HTTP 200 even for business errors': (_body, status) => status === 200,
  'code !== 200 (e.g. 202 invalid parameters)': (body) =>
    Number.isInteger(body.code) && body.code !== 200,
  'data is null on V2 errors': (body) => body.data === null,
  'timestamp still present': (body) => Number.isInteger(body.timestamp),
});

// ---------- report ----------

const generatedAt = new Date().toISOString();
const failed = results.filter((result) => !result.pass).length;
const report = {
  schemaVersion: '1.0.0',
  generatedAt,
  base: BASE,
  passed: results.length - failed,
  total: results.length,
  success: failed === 0,
  results,
};

if (JSON_MODE) {
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
} else {
  const pad = (value, length) => String(value).padEnd(length);
  console.log(`\nJustLend API agent acceptance — ${generatedAt} — base ${BASE}\n`);
  for (const result of results) {
    const status = result.pass ? 'PASS' : 'FAIL';
    console.log(
      `${pad(status, 5)} ${pad(result.name, 42)} ` +
      `${pad(`HTTP ${result.httpStatus ?? '—'}`, 9)} ${result.path}`,
    );
    for (const failure of result.failures) console.log(`      ✗ ${failure}`);
  }
  console.log(`\n${report.passed}/${report.total} endpoint probes passed.`);
}

process.exitCode = failed === 0 ? 0 : 1;
