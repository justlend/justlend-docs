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
    def test_ai_copy_distinguishes_product_and_governance_brands(self):
        paths = [
            "docs/ai_support/ai_llms.md", "docs/ai_support/index.md",
            "docs/ai_support/justlend_skills.md", "docs/ai_support/mcp_server.md",
            "docs/developers/apis/agent-acceptance.md",
            "docs/documents/aidocs/mcp_tools.md", "docs/documents/aidocs/quickstart.md",
            "docs/llms-full.txt", "docs/llms.txt",
        ]
        for path in paths:
            with self.subTest(path=path):
                source = read(path)
                self.assertNotIn("JustLend DAO", source)
                self.assertNotRegex(source, r"JUST DAO is (?:a decentralized|the largest) lending protocol")
        self.assertIn("JustLend is a decentralized lending protocol", read("docs/documents/aidocs/quickstart.md"))
        skills = read("docs/ai_support/justlend_skills.md")
        self.assertIn("Participate in JUST DAO governance proposals.", skills)
        for identifier in ["justlend-governance-v1", "@justlend/justlend-skills"]:
            self.assertIn(identifier, skills)
        self.assertIn("`@justlend/mcp-server-justlend`", read("docs/ai_support/mcp_server.md"))
        self.assertIn("Get the list of JUST DAO governance proposals.", read("docs/documents/aidocs/mcp_tools.md"))

    def test_catalog_reimport_preserves_governance_brand_and_identifiers(self):
        script = (ROOT / "scripts/normalize-mcp-catalog.mjs").as_uri()
        source = (
            "### `get_proposal_list`\n\n"
            "- **Description**: Get the list of JustLend DAO governance proposals. Returns proposals.\n"
            "- Package: `@justlend/mcp-server-justlend`\n"
            "- Source: https://github.com/justlend/mcp-server-justlend\n"
            "### `get_vote_info`\n\nUnchanged neighboring tool.\n"
        )
        result = run_js(f"import {{normalizeMcpCatalog}} from {json.dumps(script)};"
                        f"const once = normalizeMcpCatalog({json.dumps(source)});"
                        "console.log(JSON.stringify({once, stable:normalizeMcpCatalog(once) === once}));")
        self.assertEqual(result["once"], source.replace(
            "Get the list of JustLend DAO governance proposals.",
            "Get the list of JUST DAO governance proposals.",
        ))
        self.assertTrue(result["stable"])

    def test_abi_catalog_named_entries_exist_in_downloads(self):
        catalog = read("docs/developers/abis/index.md").split("## Catalog", 1)[1].split("## Decoding events", 1)[0]
        checked = 0
        for line in catalog.splitlines():
            match = re.match(r"\| \[`([^`]+\.json)`\]\([^)]+\) \|[^|]+\| (.*?) \|", line)
            if not match:
                continue
            filename, purpose = match.groups()
            abi = json.loads(read("docs/developers/abis/" + filename))
            names = {entry.get("name") for entry in abi}
            positive_claims = re.sub(r"\bno `\w+`", "", purpose)
            for entry in re.findall(r"`([A-Za-z_]\w*)(?:\([^`]*\))?`", positive_claims):
                if entry != "callValue":  # TRON transaction property, not an ABI function.
                    self.assertIn(entry, names, f"{filename} does not declare {entry}")
            checked += 1
        self.assertEqual(checked, len([p for p in (ROOT / "docs/developers/abis").glob("*.json")
                                      if isinstance(json.loads(p.read_text()), list)]))

    def test_annual_block_count_matches_documented_formula(self):
        expected = int(365.25 * 86400 / 3)
        glossary = read("docs/resources/glossary.md")
        actual = re.search(r"blocksPerYear ≈ ([\d,]+)", glossary).group(1)
        self.assertEqual(int(actual.replace(",", "")), expected)
        self.assertIn(f"**{expected:,}** (`365.25 × 86400 / 3`)", read("docs/llms-full.txt"))

    def test_abi_directory_labels_do_not_link_to_single_download(self):
        for path in (ROOT / "docs").rglob("*.md"):
            for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", path.read_text()):
                if label.strip("`").endswith("abis/"):
                    self.assertTrue(target == "abis/index.md" or target.endswith("/abis/index.md") or target.endswith("/abis/"),
                                    f"{path}: directory label links to {target}")

    def test_selected_abis_match_dated_verification_evidence(self):
        evidence = json.loads((FIXTURES / "abi-provenance-20261014.json").read_text())
        manifest = json.loads(read("docs/developers/abis/manifest.json"))
        published = {item["file"]: item for item in manifest["interfaces"]}

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
        self.assertEqual(manifest["checked_at"], evidence["checked_at"])
        self.assertEqual(set(published), {item["file"] for item in evidence["abi_interfaces"]})
        self.assertEqual(evidence["abi_entries_checked"],
                         sum(len(item["entries"]) for item in evidence["abi_interfaces"]))
        for item in evidence["abi_interfaces"]:
            with self.subTest(file=item["file"]):
                source = ROOT / "docs/developers/abis" / item["file"]
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), item["download_sha256"])
                metadata = published[item["file"]]
                self.assertEqual(metadata["download_sha256"], item["download_sha256"])
                self.assertEqual(metadata["verification_basis"], item["basis"])
                self.assertEqual(metadata["checked_entry_count"], len(item["entries"]))
                self.assertEqual(metadata.get("implementation", metadata["target"]), item["target"])
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
                    cross_check = metadata["supplied_artifact_cross_check"]
                    self.assertEqual(cross_check["matched_selected_entry_count"], len(entries))
                    self.assertEqual(cross_check["entry_count"], sum(cross_check["entry_counts"].values()))
                    self.assertGreater(cross_check["entry_count"], len(entries))
                    self.assertRegex(cross_check["artifact_sha256"], r"^[0-9a-f]{64}$")
                    # Full supplied artifacts stay local; this is a manifest
                    # consistency check, not a replay of the full-ABI comparison.
        self.assertEqual(published["governor-alpha.json"]["tuple_source"], evidence["tuple_source"]["github_url"])

    def test_pointer_and_decimal_evidence_matches_registry(self):
        evidence = json.loads((FIXTURES / "abi-provenance-20261014.json").read_text())
        reads = {item["label"]: item for item in evidence["constant_reads"]}
        pointers = json.loads(read("docs/developers/abis/manifest.json"))["address_verification"]
        self.assertEqual(pointers["checked_at"], evidence["checked_at"])
        self.assertFalse(pointers["atomic_block_snapshot"])
        for pointer in pointers["calls"]:
            observation = reads[pointer["label"]]
            self.assertTrue(observation["result"]["result"])
            self.assertEqual(pointer["contract_address"], observation["request"]["contract_address"])
            self.assertEqual(pointer["function_selector"], observation["request"]["function_selector"])
            self.assertEqual(pointer["returned_address"], observation["decoded"])
            self.assertIn("| `{}` | `{}` | `{}` |".format(
                pointer["contract_address"], pointer["function_selector"], pointer["returned_address"]),
                read("docs/developers/deployed_contracts.md"))
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
        extra = json.loads((FIXTURES / "abi-provenance-20261014.json").read_text())["additional_constant_reads"]
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
            columns = None
            for line in section.splitlines():
                if line.startswith("| Param |"):
                    columns = 5
                elif line.startswith("| Field |"):
                    columns = 4
                if line.startswith("| `"):
                    cells = re.split(r"(?<!\\)\|", line)[1:-1]
                    self.assertIsNotNone(columns, (tool, line))
                    self.assertEqual(len(cells), columns, (tool, line))
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

    def test_governance_documented_boundary_expressions(self):
        # Execute the documented predicates, not an independently rewritten helper.
        # This checks documentation examples, not EVM execution of the contract.
        evidence = json.loads((FIXTURES / "contract-review-boundaries-20261014.json").read_text())
        page = read("docs/developers/supply_and_borrow_market/governance.md")
        values = {}
        for observation in evidence["governor_constant_reads"]:
            self.assertTrue(observation["response"]["result"]["result"])
            name = observation["request"]["function_selector"]
            values[name] = int(observation["response"]["constant_result"][0], 16)
        self.assertEqual(values["proposalThreshold()"], 200_000_000 * 10**18)
        self.assertEqual(values["quorumVotes()"], 600_000_000 * 10**18)
        self.assertEqual(values["votingDelay()"], 1)
        expressions = {}
        for label in ["Proposal balance gate", "Approval vote gate", "Pending block condition", "Active block condition"]:
            expressions[label] = re.search(r"\*\*" + label + r":\*\* `([^`]+)`", page)[1]
        # Tie the balance predicate to the recorded official source, including the
        # whitelist exception; the vote predicate is the inverse of Defeated.
        balance = evidence["governor_conditions"][0].replace(
            "wjst.getPriorVotes(msg.sender, sub256(block.number, 1))", "availableVotes").replace(
            "isWhitelisted(msg.sender)", "isWhitelisted")
        self.assertEqual(expressions["Proposal balance gate"], balance)
        self.assertIn("proposal.forVotes <= proposal.againstVotes || proposal.forVotes < quorumVotes",
                      evidence["governor_conditions"])
        self.assertIn(evidence["sources"][0]["github_url"], page)
        result = run_js(f"""
const proposalThreshold = {values['proposalThreshold()']}n;
const quorumVotes = {values['quorumVotes()']}n;
const proposal = (availableVotes, isWhitelisted) => {expressions['Proposal balance gate']};
const approval = (forVotes, againstVotes) => {expressions['Approval vote gate']};
const startBlock = 100n + {values['votingDelay()']}n;
const endBlock = startBlock + {values['votingPeriod()']}n;
const pending = blockNumber => {expressions['Pending block condition']};
const active = blockNumber => {expressions['Active block condition']};
console.log(JSON.stringify({{
  propose: [proposal(proposalThreshold - 1n, false), proposal(proposalThreshold, false),
    proposal(proposalThreshold + 1n, false), proposal(0n, true)],
  approve: [approval(quorumVotes - 1n, 0n), approval(quorumVotes, 0n),
    approval(quorumVotes, quorumVotes), approval(quorumVotes + 1n, quorumVotes)],
  states: [100n, 101n, 102n, endBlock, endBlock + 1n].map(n => [pending(n), active(n)])
}}));
""")
        self.assertEqual(result, {
            "propose": [False, False, True, True],
            "approve": [False, True, False, True],
            "states": [[True, False], [True, False], [False, True], [False, True], [False, False]],
        })

    def test_governance_summaries_preserve_strict_and_inclusive_boundaries(self):
        for file in ["docs/developers/supply_and_borrow_market/governance.md",
                     "docs/governance/jips.md", "docs/resources/glossary.md", "docs/llms-full.txt"]:
            with self.subTest(file=file):
                page = read(file)
                self.assertRegex(page, r"For votes >= (?:\*\*)?600,000,000")
                self.assertIn("non-whitelisted", page.lower())
                self.assertNotRegex(page, r"(?:≥|>=)\s*(?:\*\*)?200,000,000")
                self.assertNotRegex(page, r"For votes > (?:\*\*)?600,000,000")
                if file.endswith("/governance.md"):
                    self.assertIn("## Governance boundaries and evidence", page)
                else:
                    self.assertIn("governance-boundaries-and-evidence", page)
                if not file.endswith("glossary.md"):
                    self.assertIn("B+1", page)
                    self.assertIn("B+2", page)
                    self.assertNotRegex(page, r"effectively instant|essentially immediate|very next block|voting active begins immediately")

    def test_strx_query_example_requires_separate_claim_consent(self):
        page = read("docs/ai_support/mcp_server.md")
        example = page.split('**"Do I have any sTRX rewards to claim?"**', 1)[1].split('**"Can I withdraw', 1)[0]
        self.assertIn("reports the result only", example)
        self.assertIn("A query alone never authorizes a transaction", example)
        self.assertIn("Unknown/null data is not zero", example)
        self.assertIn("obtain separate explicit confirmation, then call `claim_strx_rewards`", example)
        self.assertIn("verify the receipt and post-state", example)

    def test_api_risk_snapshot_is_not_execution_eligibility(self):
        spec = yaml.safe_load(read("docs/developers/apis/justlend_apis.yaml"))
        operation = spec["paths"]["/justlend/liquidate/highRiskAccountList"]["get"]
        risk = spec["components"]["schemas"]["highRiskAccount"]["properties"]["risk"]
        page = read("docs/developers/apis.md").split("### 3.3", 1)[1].split("### 3.4", 1)[0]
        for text in [operation["description"], risk["description"], page]:
            self.assertIn("shortfall > 0", text)
            self.assertNotIn("liquidatable now", text)
        self.assertIn("error == 0", operation["description"])
        self.assertIn("unknown or failed reads", operation["description"])
        self.assertIn("not current execution eligibility", risk["description"])
        recovery = read("docs/ai_support/mcp_server.md").split("| `insufficient_allowance`", 1)[1].split("\n", 1)[0]
        self.assertNotIn("approve_for_votes", recovery)
        self.assertIn("approve_jst_for_voting", recovery)
        self.assertIn("do not retry automatically", recovery)

    def test_llm_liquidation_predicate_rejects_equality_and_read_errors(self):
        page = read("docs/llms-full.txt").split("### 2.5 Liquidation", 1)[1].split("### 2.6", 1)[0]
        expression = re.search(r"liquidity read: `([^`]+)`", page)[1]
        result = run_js(f"""
const eligible = (error, shortfall) => {expression};
console.log(JSON.stringify([[0n, 0n], [0n, 1n], [1n, 1n]].map(args => eligible(...args))));
""")
        self.assertEqual(result, [False, True, False])
        self.assertIn("rounded display of 100 is not an execution predicate", page)
        self.assertNotRegex(page, r"Risk Value (?:≥|>=) 100")
        self.assertIn("contracts/Comptroller.sol#L451-L467", page)

    def test_mcp_quote_warning_covers_successful_fallback_responses(self):
        page = read("docs/developers/energy_rental.md")
        warning = page.split('!!! warning "MCP estimate fallback (version-specific)"', 1)[1].split("### 3.", 1)[0]
        evidence = json.loads((FIXTURES / "contract-review-boundaries-20261014.json").read_text())
        self.assertIn(evidence["sources"][-1]["github_url"], warning)
        for text in ["liquidateThreshold = 86400", "feeRatio = 0.05", "minFee = 50", "4e-8",
                     "no per-field fallback/provenance marker", "independently verify both current rates",
                     "If these inputs cannot be verified, stop; do not sign or broadcast"]:
            self.assertIn(text, warning)
        for file in ["docs/getting_started/concepts/energy_rental.md", "docs/llms-full.txt"]:
            with self.subTest(file=file):
                self.assertIn("7d53a6c", read(file))
                self.assertIn("fallback defaults", read(file))
                self.assertIn("cannot be verified", read(file))
        self.assertIn("version-specific fallback warning", read("docs/ai_support/mcp_server.md"))

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
 '| `encoded` | <code>string (pattern /^&#92;d+$/)</code> | ✅ |  | Encoded upstream type |\n' +
 '### `set_network`\n- **Side effect**: 🟡 State-changing (Write)\n';
const once = normalizeMcpCatalog(input);
console.log(JSON.stringify({once, stable:normalizeMcpCatalog(once) === once}));
""")
        self.assertTrue(result["stable"])
        self.assertIn("On-chain transaction", result["once"])
        self.assertIn("Local configuration", result["once"])
        self.assertIn(r"enum(browser \| agent)", result["once"])
        self.assertIn("/^(1&#124;max)$/", result["once"])
        self.assertIn('<code>string (pattern /^&#92;d+$/)</code>', result["once"])

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
                     "developers/abis/strx.json", "developers/abis/energy-market.json"]:
            self.assertEqual((site / path).read_bytes(), (ROOT / "docs" / path).read_bytes())
        # Review reports and offline observations must not leak into published output,
        # including orphan pages, raw Markdown, search results and LLM indexes.
        for path in ["developers/verification_evidence", "developers/verification_evidence.md",
                     "developers/verification-evidence-20261014.json", "scripts/fixtures/docs-verification"]:
            self.assertFalse((site / path).exists(), path)
        forbidden = ["verification_evidence", "verification-evidence-20261014",
                     "contract-review-boundaries-20261014",
                     "abi-provenance-20261014", "original 34 findings", "34-item checklist"]
        for path in site.rglob("*"):
            if path.is_file() and path.suffix in {".html", ".md", ".json", ".txt", ".xml"}:
                content = path.read_text()
                for token in forbidden:
                    self.assertNotIn(token, content, str(path.relative_to(site)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
