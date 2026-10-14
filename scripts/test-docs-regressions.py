"""Offline regressions for the 2026-10-12 docs verification.

Run: python -m pip install -r requirements-test.txt
     python scripts/test-docs-regressions.py
No test signs, broadcasts, or queries a live service.
"""

import copy
import hashlib
import json
import os
import re
import subprocess
import unittest
from pathlib import Path

import markdown
import yaml
from jsonschema import Draft202012Validator
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "scripts/fixtures/docs-verification"


def read(path):
    return (ROOT / path).read_text()


def javascript_block(path, function):
    blocks = re.findall(r"```javascript\n(.*?)\n```", read(path), re.S)
    return next(block for block in blocks if f"function {function}(" in block)


def run_js(source):
    return json.loads(subprocess.check_output(["node", "--input-type=module", "-e", source], text=True))


class Tables(HTMLParser):
    def __init__(self, source, rendered=False):
        super().__init__()
        self.rows = []
        self.row = None
        self.cell = None
        self.feed(source if rendered else markdown.markdown(source, extensions=["tables", "fenced_code"]))

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.cell = ""

    def handle_data(self, data):
        if self.cell is not None:
            self.cell += data

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr":
            self.rows.append(self.row)
            self.row = None


class DocumentationRegressions(unittest.TestCase):
    def test_selected_abis_match_dated_verification_evidence(self):
        evidence = json.loads(read("docs/developers/verification-evidence-20261014.json"))

        def types(parameters):
            return [p["type"] + "(" + ",".join(types(p["components"])) + ")"
                    if p["type"].startswith("tuple") and p.get("components") else p["type"]
                    for p in parameters]

        def canonical(entry):
            kind = entry["type"].lower()
            value = {"type": kind, "name": entry["name"], "inputs": types(entry.get("inputs", []))}
            if kind == "function":
                value.update(outputs=types(entry.get("outputs", [])),
                             stateMutability=entry["stateMutability"].lower())
            elif kind == "event":
                value.update(indexed=[bool(p.get("indexed", False)) for p in entry["inputs"]],
                             anonymous=bool(entry.get("anonymous", False)))
            return value

        self.assertEqual(len(evidence["abi_interfaces"]), 7)
        self.assertEqual(evidence["abi_entries_checked"],
                         sum(len(item["entries"]) for item in evidence["abi_interfaces"]))
        for item in evidence["abi_interfaces"]:
            with self.subTest(file=item["file"]):
                source = ROOT / "docs/developers/abis" / item["file"]
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), item["download_sha256"])
                entries = json.loads(source.read_text())
                by_key = {entry["type"].lower() + " " + entry["name"] + "(" +
                          ",".join(types(entry.get("inputs", []))) + ")": entry for entry in entries}
                self.assertEqual(set(by_key), {entry["key"] for entry in item["entries"]})
                for observed in item["entries"]:
                    self.assertEqual(canonical(by_key[observed["key"]]), observed["observed"])
                    self.assertEqual(observed["status"], "matched")
                if item["basis"].startswith("compiler_"):
                    proof = item["compiler_proof"]
                    self.assertEqual(proof["compiled_creation_excluding_metadata_sha256"],
                                     proof["node_creation_excluding_metadata_sha256"])
                    self.assertFalse(proof["full_bytecode_match"])
                    self.assertFalse(proof["source_bundle_publicly_reproducible"])

    def test_pointer_and_decimal_evidence_matches_registry(self):
        evidence = json.loads(read("docs/developers/verification-evidence-20261014.json"))
        reads = {item["label"]: item for item in evidence["constant_reads"]}
        registry = json.loads(read("docs/developers/contracts.json"))["networks"]["mainnet"]
        for label, address in [
            ("governor_implementation", registry["governance"]["governor_delegate"]["address"]),
            ("oracle_proxy", registry["price_oracle"]["proxy"]["address"]),
            ("oracle_backend", registry["price_oracle"]["implementation"]["address"]),
        ]:
            self.assertTrue(reads[label]["result"]["result"])
            self.assertEqual(address["base58"], reads[label]["decoded"])
            self.assertEqual(address["hex_evm"], "0x" + reads[label]["constant_result"][0][-40:])
            self.assertEqual(address["hex_tron"], "0x41" + reads[label]["constant_result"][0][-40:])
        for symbol in ["wstUSDT", "sTRX", "SUN", "BTT", "JST", "HTX", "USD1", "TUSD", "USDJ", "WBTT"]:
            token = registry["jtokens"]["j" + symbol]
            observation = reads["decimals_" + symbol]
            self.assertEqual(observation["request"]["contract_address"], token["underlying"]["address"]["base58"])
            self.assertEqual(int(observation["decoded"]), token["underlying_decimals"])
        ids = {item["id"] for item in evidence["issues"]}
        self.assertEqual(ids, {f"JL-{number:03d}" for number in range(1, 35)})
        self.assertFalse(evidence["all_issues_completed"])
        self.assertEqual(sum(item["hosted_status"] == "already_correct" for item in evidence["issues"]), 11)

    def test_marketg1_tuples_returns_and_documented_events(self):
        abi = json.loads(read("docs/developers/abis/energy-market.json"))
        functions = {item["name"]: item for item in abi if item["type"] == "function"}
        self.assertEqual([p["type"] for p in functions["getRentInfo"]["outputs"]], ["uint256", "uint256", "bool"])
        rental = functions["rentals"]["outputs"]
        self.assertEqual(len(rental), 1)
        self.assertEqual(rental[0]["type"], "tuple")
        self.assertEqual([(p["name"], p["type"]) for p in rental[0]["components"]],
                         [("amount", "uint256"), ("securityDeposit", "uint256"), ("rentIndex", "uint256")])
        self.assertEqual(functions["rentPaused"]["outputs"][0]["type"], "bool")
        for name in ["returnResource", "returnResourceByReceiver"]:
            self.assertEqual([p["type"] for p in functions[name]["outputs"]], ["uint256"])
        self.assertEqual(functions["returnResource"]["inputs"][0]["name"], "receiver")
        for event in [item for item in abi if item["type"] == "event"]:
            declaration = "event " + event["name"] + "(" + ", ".join(
                p["type"] + (" indexed" if p["indexed"] else "") + " " + p["name"]
                for p in event["inputs"]) + ");"
            self.assertIn(declaration, read("docs/developers/energy_rental.md"))
        extra = json.loads(read("docs/developers/verification-evidence-20261014.json"))["additional_constant_reads"]
        for name in ["rent_info_empty_order", "rentals_empty_order"]:
            observed = next(item for item in extra if item["label"] == name)
            self.assertTrue(observed["result"]["result"])
            self.assertEqual(len(observed["constant_result"][0]), 3 * 64)

    def test_staking_quote_handles_fractional_raw_units(self):
        source = javascript_block("docs/developers/staked_trx.md", "quoteStake")
        adapter = """
const STRX = 'read-only-fixture';
const tronWeb = {
  contract: () => ({at: async () => ({exchangeRate: () => ({call: async () => 1250000000000000000n})})}),
  toSun: value => {
    const [whole, fraction = ''] = String(value).split('.');
    if (fraction.length > 6) throw new Error('Too many decimals');
    return (BigInt(whole) * 1000000n + BigInt((fraction + '000000').slice(0, 6))).toString();
  }
};
"""
        observed = run_js(adapter + source + "\nconsole.log(JSON.stringify((await Promise.all([10.5, '10.5', '0.5', '0.000001'].map(quoteStake))).map(String)));")
        self.assertEqual(observed, ["8400000000000000000", "8400000000000000000", "400000000000000000", "800000000000"])

    def test_contract_summary_links_cover_oracle_and_staking_functions(self):
        rows = [line for line in read("docs/developers/contracts_overview.md").splitlines()
                if line.startswith(("| Price Oracle |", "| Staked TRX |"))]
        self.assertEqual(len(rows), 3)
        for row in rows:
            cells = [cell.strip() for cell in row.split("|")[1:-1]]
            with self.subTest(contract=cells[1]):
                methods = {method.split("(", 1)[0] for method in re.findall(r"`([^`]+)`", cells[5])}
                links = re.findall(r"\]\((abis/[^)]+\.json)\)", cells[6])
                self.assertTrue(methods)
                self.assertTrue(links)
                available = {item["name"] for link in links
                             for item in json.loads(read("docs/developers/" + link))
                             if item["type"] == "function"}
                self.assertFalse(methods - available, f"ABI links omit {sorted(methods - available)}")

    def test_settlement_event_abis_decode_observed_receipts(self):
        observed = json.loads((FIXTURES / "settlement-events.json").read_text())
        manifest = json.loads(read("docs/developers/abis/manifest.json"))
        strx_scope = next(item for item in manifest["interfaces"] if item["file"] == "strx.json")
        strx_events = [item["name"] for item in json.loads(read("docs/developers/abis/strx.json"))
                       if item["type"] == "event"]
        self.assertCountEqual(strx_events, strx_scope["implementation_events"])
        self.assertEqual(len(strx_events), strx_scope["implementation_event_count"])
        self.assertEqual({event["name"] for event in observed["events"]},
                         {"Deposit", "Withdraw", "Claim", "RentClaimed"})
        for event in observed["events"]:
            with self.subTest(event=event["name"]):
                file = "energy-market.json" if event["name"] == "RentClaimed" else "strx.json"
                abi = json.loads(read("docs/developers/abis/" + file))
                entries = [item for item in abi if item["type"] == "event" and item["name"] == event["name"]]
                self.assertEqual(len(entries), 1, f"Missing or duplicate {event['name']} ABI")
                entry = entries[0]
                self.assertFalse(entry["anonymous"])
                self.assertEqual(entry["name"] + "(" + ",".join(p["type"] for p in entry["inputs"]) + ")",
                                 event["canonical_signature"])
                declaration = entry["name"] + "(" + ", ".join(
                    p["type"] + (" indexed" if p["indexed"] else "") + " " + p["name"]
                    for p in entry["inputs"]) + ")"
                self.assertEqual(declaration, event["event"])
                if event["name"] != "RentClaimed":
                    self.assertIn("event " + declaration + ";", read("docs/developers/staked_trx.md"))
                log = event["raw_log"]
                topics = iter(log["topics"][1:])
                words = iter(re.findall(r".{64}", log["data"]))
                decoded = {}
                for param in entry["inputs"]:
                    word = next(topics if param["indexed"] else words)
                    self.assertIn(param["type"], ("address", "uint256"))
                    decoded[param["name"]] = ("0x" + word[-40:] if param["type"] == "address"
                                              else str(int(word, 16)))
                self.assertEqual(decoded, event["decoded"])
                self.assertEqual(list(topics), [])
                self.assertEqual(list(words), [])
                if event["name"] == "RentClaimed":
                    transfer = event["trx_transfer"]
                    self.assertFalse(transfer["rejected"])
                    self.assertEqual(transfer["caller_address"][2:], log["address"])
                    self.assertEqual(transfer["callValueInfo"], [{"callValue": int(decoded["add"])}])

    def test_v2_null_business_errors_and_invalid_controls(self):
        spec = yaml.safe_load(read("docs/developers/apis/justlend_apis.yaml"))
        fixtures = json.loads((FIXTURES / "v2-errors.json").read_text())
        self.assertEqual(len(fixtures["responses"]), 5)
        for item in fixtures["responses"]:
            with self.subTest(path=item["path"]):
                schema = copy.deepcopy(spec["paths"][item["path"]]["get"]["responses"]["200"]["content"]["application/json"]["schema"])
                schema["components"] = spec["components"]
                Draft202012Validator.check_schema(schema)
                validator = Draft202012Validator(schema)
                self.assertEqual(list(validator.iter_errors(item["response"])), [])
                for invalid in ([], "not an object", 123):
                    self.assertFalse(validator.is_valid({**item["response"], "data": invalid}))
                # Nullable must not discard required object fields.
                self.assertFalse(validator.is_valid({**item["response"], "data": {}}))

    def test_glossary_decimals_match_observed_mainnet_values(self):
        evidence = json.loads((FIXTURES / "mainnet-reads.json").read_text())
        section = read("docs/resources/glossary.md").split("### underlying decimals", 1)[1].split("\n---", 1)[0]
        rows = Tables(section).rows[1:]
        values = {token.strip(): int(row[1]) for row in rows for token in row[0].split(",")}
        for key, observation in evidence.items():
            if key.startswith("decimals_"):
                token = key.removeprefix("decimals_")
                with self.subTest(token=token):
                    self.assertEqual(values[token], int(observation["constant_result"][0], 16))

    def test_mcp_parameter_tables_preserve_all_columns(self):
        source = read("docs/documents/aidocs/mcp_tools.md")
        for section in re.split(r"^### `", source, flags=re.M)[1:]:
            tool = section.split("`", 1)[0]
            for line in section.splitlines():
                if line.startswith("| `"):
                    cells = re.split(r"(?<!\\)\|", line)[1:-1]
                    self.assertEqual(len(cells), 5, (tool, line))
        mode = next(row for row in Tables(source).rows if row and row[0] == "mode")
        self.assertEqual(mode[1], "enum(browser | agent)")
        self.assertEqual(mode[2], "✅")
        self.assertEqual(mode[3], "")
        repay = source.split('### `repay`', 1)[1].split('\n### ', 1)[0]
        amount = next(row for row in Tables(repay).rows if row and row[0] == 'amount')
        self.assertEqual(amount[1], r'string (pattern /^(\d+(\.\d+)?|max)$/)')

    def test_quotes_do_not_invoke_the_rental_write_tool(self):
        source = read("docs/getting_started/concepts/energy_rental.md")
        self.assertNotIn("--dry-run", source)
        self.assertIn("calculate_energy_rental_price", source)

    def test_governance_call_signatures_match_deployed_abi(self):
        observed = json.loads((FIXTURES / "governor-inputs.json").read_text())
        abi = json.loads(read("docs/developers/abis/governor-alpha.json"))
        by_name = {item.get("name"): item for item in abi}
        for method in observed["functions"]:
            with self.subTest(method=method["name"]):
                self.assertIn(method["name"], by_name)
                self.assertEqual(by_name[method["name"]]["inputs"], method["inputs"])
        receipt = by_name["getReceipt"]["outputs"]
        self.assertEqual(len(receipt), 1)
        self.assertEqual(receipt[0]["type"], "tuple")
        self.assertEqual([(p["name"], p["type"]) for p in receipt[0]["components"]],
                         [("hasVoted", "bool"), ("support", "uint8"), ("votes", "uint96")])

    def test_native_repayment_matches_observed_mainnet_abi(self):
        observed = json.loads((FIXTURES / "jtrx-repayment.json").read_text())
        documented = json.loads(read("docs/developers/abis/jtrx-repay.json"))
        for expected in observed["functions"]:
            actual = next(item for item in documented if item["name"] == expected["name"])
            self.assertEqual(actual["inputs"], expected["inputs"])
            self.assertEqual(actual["stateMutability"], "payable")
        text = read("docs/developers/supply_and_borrow_market/sbm.md")
        self.assertIn("function repayBorrow(uint256 amount) external payable", text)
        self.assertIn("function repayBorrowBehalf(address borrower) external payable", text)
        self.assertIn("function repayBorrowBehalf(address borrower, uint256 repayAmount) external returns (uint256)", text)

    def test_exchange_rate_examples_preserve_raw_units(self):
        source = javascript_block("docs/resources/glossary.md", "underlyingRawFromJTokens")
        result = run_js(source + """
console.log(JSON.stringify([
  underlyingRawFromJTokens('100000000', '200000000000000000000000000').toString(),
  underlyingRawFromJTokens('100000000', '20000000000000000').toString(),
  underlyingRawFromJTokens('1', '1').toString()
]));
""")
        # One jToken: 0.02 of an 18-decimal asset, or 2 of a 6-decimal asset.
        self.assertEqual(result, [str(2 * 10**16), "2000000", "0"])

    def test_prepaid_estimate_covers_higher_stable_rate_and_dynamic_fee(self):
        source = javascript_block("docs/developers/energy_rental.md", "estimatePrepaymentSun")
        result = run_js(source + """
const common = {amountSun:'100000000', rentalRateMantissa:'1000000000000',
 stableRateMantissa:'2000000000000', durationSeconds:'86400',
 liquidateThresholdSeconds:'3600', feeRatioMantissa:'80000000000000', minFeeSun:'20000000'};
console.log(JSON.stringify([
 estimatePrepaymentSun(common).toString(),
 estimatePrepaymentSun({...common, amountSun:'1000000000000', liquidateThresholdSeconds:'0'}).toString(),
 estimatePrepaymentSun({...common, amountSun:'1', rentalRateMantissa:'1', stableRateMantissa:'1',
  durationSeconds:'1', liquidateThresholdSeconds:'0', feeRatioMantissa:'1', minFeeSun:'0'}).toString()
]));
""")
        self.assertEqual(result, ["55280000", "345680000000", "2"])

    def test_prepaid_estimate_rejects_missing_or_unsafe_inputs(self):
        source = javascript_block("docs/developers/energy_rental.md", "estimatePrepaymentSun")
        result = run_js(source + """
const common = {amountSun:'100000000', rentalRateMantissa:'1000000000000',
 stableRateMantissa:'2000000000000', durationSeconds:'86400',
 liquidateThresholdSeconds:'3600', feeRatioMantissa:'80000000000000', minFeeSun:'20000000'};
const rejects = [undefined, -1n, '1.5', Number.MAX_SAFE_INTEGER + 1, 0n].map(amountSun => {
 try { estimatePrepaymentSun({...common, amountSun}); return false; } catch { return true; }
});
try { estimatePrepaymentSun({...common, stableRateMantissa:undefined}); rejects.push(false); }
catch { rejects.push(true); }
console.log(JSON.stringify(rejects));
""")
        self.assertEqual(result, [True] * 6)

    def test_market_lookup_filters_full_list_and_fails_closed(self):
        source = javascript_block("docs/documents/aidocs/market_data.md", "getMarket")
        result = run_js(source + """
const list = [
 {address:'TE2RzoSV3wFK99w6J9UnnZ4vLfXYoxvRwP', symbol:'jTRX'},
 {address:'TXJgMdjVX5dKiQaUi9QobwNxtSQaFqccvd', symbol:'jUSDT'}
];
let body = {code:0, data:{tokenList:list}};
let ok = true;
globalThis.fetch = async url => {
 if (url !== 'https://openapi.just.network/lend/jtoken') throw Error('Unsupported server filter');
 return {ok, status:503, json:async () => body};
};
const results = [(await getMarket(list[1].address)).symbol];
async function fails(address) { try { await getMarket(address); return false; } catch { return true; } }
results.push(await fails('not-in-the-list'));
body = {code:202, message:'unavailable'}; results.push(await fails(list[1].address));
body = {code:0, data:{tokenList:null}}; results.push(await fails(list[1].address));
body = {code:0, data:{tokenList:list}}; ok=false; results.push(await fails(list[1].address));
console.log(JSON.stringify(results));
""")
        self.assertEqual(result, ["jUSDT", True, True, True, True])

    def test_catalog_normalization_is_repeatable_after_import(self):
        script = (ROOT / "scripts/normalize-mcp-catalog.mjs").as_uri()
        result = run_js(f"import {{normalizeMcpCatalog}} from {json.dumps(script)};" + r"""
const input = '### `transfer_trx`\n- **Side effect**: 🟡 State-changing (Write)\n' +
 '| Param | Type | Required | Default | Description |\n' +
 '| `mode` | enum(browser | agent) | ✅ |  | Wallet mode |\n' +
 '| `amount` | string (pattern /^(1|max)$/) | ✅ |  | Amount |\n' +
 '### `set_network`\n- **Side effect**: 🟡 State-changing (Write)\n';
const once = normalizeMcpCatalog(input);
console.log(JSON.stringify({once, stable:normalizeMcpCatalog(once) === once}));
""")
        self.assertTrue(result["stable"])
        self.assertIn("On-chain transaction", result["once"])
        self.assertIn("Local configuration", result["once"])
        self.assertIn(r"enum(browser \| agent)", result["once"])
        self.assertIn("/^(1&#124;max)$/", result["once"])

    def test_contract_registry_remains_schema_valid(self):
        schema = json.loads(read("docs/developers/contracts.schema.json"))
        data = json.loads(read("docs/developers/contracts.json"))
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(data)), [])
        observation = json.loads((FIXTURES / "mainnet-reads.json").read_text())["gov_impl"]
        address = data["networks"]["mainnet"]["governance"]["governor_delegate"]["address"]
        self.assertEqual(address["hex_evm"], "0x" + observation["constant_result"][0][-40:])
        observation = json.loads((FIXTURES / "mainnet-reads.json").read_text())["oracle"]
        address = data["networks"]["mainnet"]["price_oracle"]["proxy"]["address"]
        self.assertEqual(address["hex_evm"], "0x" + observation["constant_result"][0][-40:])

    @unittest.skipUnless(os.environ.get("DOCS_SITE_DIR"), "Set DOCS_SITE_DIR to a fresh strict MkDocs build")
    def test_built_catalog_and_downloads_match_fixed_sources(self):
        site = Path(os.environ["DOCS_SITE_DIR"])
        html = (site / "documents/aidocs/mcp_tools/index.html").read_text()
        mode = next(row for row in Tables(html, rendered=True).rows if row and row[0] == "mode")
        self.assertEqual(mode, ["mode", "enum(browser | agent)", "✅", "", "Wallet mode: 'browser' or 'agent'"])
        repay = html.split('id="repay"', 1)[1].split('</table>', 1)[0] + '</table>'
        amount = next(row for row in Tables(repay, rendered=True).rows if row and row[0] == 'amount')
        self.assertEqual(amount[1], r'string (pattern /^(\d+(\.\d+)?|max)$/)')
        for path in ["developers/apis/justlend_apis.yaml", "developers/abis/governor-alpha.json",
                     "developers/abis/price-oracle-impl.json", "developers/abis/manifest.json",
                     "developers/abis/strx.json", "developers/abis/energy-market.json",
                     "developers/verification-evidence-20261014.json"]:
            self.assertEqual((site / path).read_bytes(), (ROOT / "docs" / path).read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
