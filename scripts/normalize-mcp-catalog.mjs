#!/usr/bin/env node
/** Docs-local corrections to apply after importing the upstream generated catalog.
 * This does not modify MCP annotations, tool implementations, or upstream files.
 */
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

const localConfig = new Set(['set_active_wallet', 'set_wallet_mode', 'set_network']);
const chainEffects = {
  transfer_trx: 'Transfers native TRX to the confirmed recipient.',
  transfer_trc20: 'Transfers the selected TRC20 token to the confirmed recipient.',
  enter_market: 'Changes on-chain Comptroller collateral membership for the selected market.',
  approve_underlying: 'Changes the underlying token allowance granted to the jToken contract.',
  claim_rewards: 'Claims mining rewards through an on-chain transaction.',
  approve_jst_for_voting: 'Changes the JST allowance granted to WJST.',
  approve_moolah_vault: 'Changes the token allowance granted to the selected V2 vault.',
  approve_moolah_proxy: 'Changes the token allowance granted to the V2 core contract.',
  approve_liquidator_token: 'Changes the loan-token allowance granted to the public liquidator.',
};

// Markdown consumes escapes such as "\." in plain text, while a backtick span
// preserves the extra "\|" used for table escaping. Encode code text as entities
// instead, so the displayed regex retains both its backslashes and alternation.
const codeText = value => value.replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/\\/g, '&#92;').replace(/\|/g, '&#124;');

export function normalizeMcpCatalog(source) {
  source = source.replace(
    /^(\| `[^`]+` \| )(.+?)( \| (?:✅|—) \| .*)$/gm,
    (_, prefix, type, rest) => prefix + type
      .replace(/\(pattern (\/.*\/)\)/, (_, pattern) => `(pattern <code>${codeText(pattern)}</code>)`)
      .replace(/(?<!\\)\|/g, '\\|') + rest,
  );
  source = source.replace(/^### `([^`]+)`\n([\s\S]*?)(?=^### |$(?![\s\S]))/gm, (_, tool, body) => {
    let label;
    if (localConfig.has(tool)) {
      label = '🟡 Local configuration — changes local wallet/network settings; does not build, sign, or broadcast a chain transaction. Confirm the new configuration before subsequent writes.';
    } else if (tool === 'connect_browser_wallet') {
      label = '🟡 Disabled interaction — returns a safety notice; does not build, sign, or broadcast a transaction. Do not bypass the disabled browser bridge.';
    } else if (chainEffects[tool]) {
      label = `🔴 On-chain transaction — ${chainEffects[tool]} Builds a transaction, requires wallet signing, and may broadcast; explicit confirmation is required before execution.`;
    }
    if (label) body = body.replace(/^- \*\*Side effect\*\*: .*$/m, `- **Side effect**: ${label}`);
    return `### \`${tool}\`\n${body}`;
  });
  source = source.replace(
    '> ⚠️ Tools marked 🔴 **sign and broadcast TRON transactions that move real assets** — the client MUST require human confirmation (HITL) before executing. 🟡 tools only change local wallet/network config or start an interaction. Private keys are managed encrypted by `@bankofai/agent-wallet` and are **never passed as tool arguments**. The legacy unauthenticated browser-wallet bridge is disabled.',
    '> ⚠️ 🔴 identifies on-chain transactions, including transfers, approvals, collateral membership, and claims, whether or not the MCP annotation marks them destructive. They require explicit human confirmation **before** building a signing/broadcast workflow. 🟡 identifies local configuration or the disabled browser interaction, not an on-chain write. `destructiveHint: false` does not mean read-only. Private keys remain encrypted in `@bankofai/agent-wallet` and are never tool arguments. The browser-wallet bridge remains disabled.',
  );
  return source;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const path = new URL('../docs/documents/aidocs/mcp_tools.md', import.meta.url);
  const source = await readFile(path, 'utf8');
  const normalized = normalizeMcpCatalog(source);
  if (process.argv.includes('--check')) {
    if (normalized !== source) {
      console.error('MCP catalog needs table escaping / side-effect normalization.');
      process.exitCode = 1;
    }
  } else if (normalized !== source) {
    await writeFile(path, normalized);
  }
}
