import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';
import test from 'node:test';

const exec = promisify(execFile);
const script = fileURLToPath(new URL('./api-acceptance.mjs', import.meta.url));
const contracts = JSON.parse(await readFile(
  new URL('../docs/developers/contracts.json', import.meta.url), 'utf8',
));
const symbols = Object.values(contracts.networks.mainnet.jtokens).map(({ symbol }) => symbol);
const timestamp = 1_800_000_000_000;
const v1 = (data) => ({ code: 0, message: 'SUCCESS', data });
const v2 = (data) => ({ code: 200, message: 'Success', timestamp, data });

function fixtures() {
  return {
    '/lend/jtoken': v1({ tokenList: symbols.map((symbol) => ({
      symbol, supplyRate: '0.01', cash: '100', exchangeRate: '1',
      borrowIndex: '1000000000000000000', underlyingDecimal: 18,
    })) }),
    '/lend/account': v1({ list: Array.from({ length: 50 }, () => ({})), totalCount: 100, totalPage: 2 }),
    '/lend/strx': v1({
      stakeInfo: { reserves: '100', decimal: '18' },
      rentInfo: { priceFor10KEnergByRent: '1' },
    }),
    '/mining/apy': v1(Object.fromEntries(symbols.map((symbol) => [symbol, { USDD: '0.01' }]))),
    '/justlend/liquidate/highRiskAccountList': v1({ jtokens: {}, updateTime: timestamp, accounts: [] }),
    '/v2/index/vault/list': v2({ allVaults: { list: [{
      vaultAddress: 'test-vault', tvl: '100', apy: '0.01', tags: [], markets: [], allocations: [],
      userSupplyUsd: null, userSupplyAmount: null,
    }] } }),
    '/v2/index/market/list': v2({ allMarkets: [{
      id: `0x${'ab'.repeat(32)}`, lltv: '0.8', ltv: null, risk: null, loanAmount: null,
    }] }),
    '/lend/nonExistentXYZ': { code: 404, message: 'Not found' },
    '/v2/vault/position': { code: 202, message: 'Invalid parameters', data: null, timestamp },
  };
}

// Run the actual CLI against a loopback server: no production API dependency.
async function run(args, scenario = 'success') {
  const responses = fixtures();
  if (scenario === 'contract-failure') responses['/lend/strx'].data.stakeInfo.reserves = 100;
  const server = createServer((req, res) => {
    if (scenario === 'request-failure') {
      req.socket.destroy();
      return;
    }
    res.setHeader('Content-Type', 'application/json');
    if (scenario === 'invalid-json' && req.url === '/lend/strx') {
      res.end('not JSON');
      return;
    }
    res.statusCode = Object.hasOwn(responses, req.url) ? 200 : 404;
    res.end(JSON.stringify(responses[req.url] ?? {}));
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    const output = await exec(process.execPath, [script, ...args], {
      env: { ...process.env, JUSTLEND_API_BASE: base }, timeout: 10_000,
    }).then(
      (result) => ({ code: 0, ...result }),
      (error) => {
        if (typeof error.code !== 'number') throw error;
        return { code: error.code, stdout: error.stdout, stderr: error.stderr };
      },
    );
    return { ...output, base };
  } finally {
    server.closeAllConnections();
    await new Promise((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
  }
}

function parseReport(output, passed) {
  assert.ok(output.stdout.startsWith('{\n'), 'stdout must start with a JSON object');
  const report = JSON.parse(output.stdout);
  assert.equal(report.schemaVersion, '1.0.0');
  assert.equal(new Date(report.generatedAt).toISOString(), report.generatedAt);
  assert.equal(report.base, output.base);
  assert.equal(report.total, 9);
  assert.equal(report.passed, passed);
  assert.equal(report.success, passed === report.total);
  assert.equal(report.results.length, report.total);
  assert.equal(report.results.filter((result) => result.pass).length, passed);
  assert.equal(output.code, report.success ? 0 : 1);
  return report;
}

test('--json emits only a parseable report when all probes pass', async () => {
  const output = await run(['--json']);
  const report = parseReport(output, 9);
  assert.equal(output.stderr, '');
  for (const result of report.results) {
    assert.equal(result.httpStatus, 200);
    assert.deepEqual(result.failures, []);
  }
});

test('--json keeps contract failures on stderr and exits nonzero', async () => {
  const output = await run(['--json'], 'contract-failure');
  const report = parseReport(output, 8);
  const failure = report.results.find((result) => !result.pass);
  assert.equal(failure.path, '/lend/strx');
  assert.equal(failure.httpStatus, 200);
  assert.equal(failure.failures.length, 1);
  assert.match(failure.failures[0], /stakeInfo.reserves/);
  assert.match(output.stderr, /8\/9 endpoint probes passed/);
  assert.match(output.stderr, /FAIL V1 sTRX.*HTTP 200.*\/lend\/strx/);
  assert.ok(output.stderr.includes(failure.failures[0]));
});

test('--json remains valid when an endpoint returns malformed JSON', async () => {
  const output = await run(['--json'], 'invalid-json');
  const report = parseReport(output, 8);
  const failure = report.results.find((result) => !result.pass);
  assert.equal(failure.path, '/lend/strx');
  assert.equal(failure.httpStatus, 200);
  assert.match(failure.failures[0], /request failed:/);
  assert.ok(output.stderr.includes(failure.failures[0]));
});

test('--json remains valid when every request fails', async () => {
  const output = await run(['--json'], 'request-failure');
  const report = parseReport(output, 0);
  assert.match(output.stderr, /0\/9 endpoint probes passed/);
  assert.equal(output.stderr.match(/^FAIL /gm).length, 9);
  for (const result of report.results) {
    assert.equal(result.httpStatus, null);
    assert.match(result.failures[0], /request failed:/);
    assert.ok(output.stderr.includes(result.path));
  }
});

for (const scenario of ['success', 'contract-failure']) {
  test(`default output preserves human-readable ${scenario} results`, async () => {
    const output = await run([], scenario);
    assert.equal(output.code, scenario === 'success' ? 0 : 1);
    assert.equal(output.stderr, '');
    assert.match(output.stdout, /JustLend API agent acceptance/);
    assert.match(output.stdout, /PASS\s+V1 market list/);
    assert.match(output.stdout, scenario === 'success'
      ? /9\/9 endpoint probes passed/ : /8\/9 endpoint probes passed/);
    if (scenario !== 'success') {
      assert.match(output.stdout, /FAIL\s+V1 sTRX/);
      assert.match(output.stdout, /stakeInfo.reserves/);
    }
  });
}
