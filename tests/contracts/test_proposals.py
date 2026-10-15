import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("verify_proposals", ROOT / "scripts/verify-proposals.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class ProposalIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "proposal"
        shutil.copytree(ROOT / "evidence/reference-proposals/desktop-20261012", self.directory)

    def test_proposal_cannot_self_approve(self):
        path = self.directory / "proposal.json"
        data = json.loads(path.read_text())
        data["accepted"] = True
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(AssertionError, "self-approve"):
            verifier.verify(self.directory)

    def test_changed_pixels_fail_checksums(self):
        path = next(self.directory.glob("*.png"))
        data = bytearray(path.read_bytes())
        data[-1] ^= 1
        path.write_bytes(data)
        with self.assertRaises(AssertionError):
            verifier.verify(self.directory)

    def test_false_environment_dpr_fails_even_with_new_manifest_checksum(self):
        captures = self.directory / "captures.json"
        data = json.loads(captures.read_text())
        data["captures"][0]["environmentDisplayScale"] = 9
        captures.write_text(json.dumps(data))
        path = self.directory / "proposal.json"
        proposal = json.loads(path.read_text())
        proposal["files"]["captures.json"] = hashlib.sha256(captures.read_bytes()).hexdigest()
        path.write_text(json.dumps(proposal))
        with self.assertRaises(AssertionError):
            verifier.verify(self.directory)

    def test_discovered_card_variant_cannot_be_omitted_from_valid_capture_matrix(self):
        captures_path = self.directory / "captures.json"
        captures = json.loads(captures_path.read_text())
        removed = [c for c in captures["captures"] if c["api"] == "BleeckerCard" and c["variant"] == "outlined"]
        removed_paths = {c["path"] for c in removed}
        captures["captures"] = [c for c in captures["captures"] if c["path"] not in removed_paths]
        captures_path.write_text(json.dumps(captures))
        fixtures_path = self.directory / "fixtures.json"
        fixtures = json.loads(fixtures_path.read_text())
        fixtures["fixtures"] = [f for f in fixtures["fixtures"] if not (f["api"] == "BleeckerCard" and f["variant"] == "outlined")]
        fixtures_path.write_text(json.dumps(fixtures))
        index_path = self.directory / "api-index.json"
        index = json.loads(index_path.read_text())
        index["BleeckerCard"]["captures"] = [p for p in index["BleeckerCard"]["captures"] if p not in removed_paths]
        index["BleeckerCard"]["fixtures"] = [f for f in index["BleeckerCard"]["fixtures"] if f not in {c["fixture"] for c in removed}]
        index_path.write_text(json.dumps(index))
        path = self.directory / "proposal.json"
        proposal = json.loads(path.read_text())
        proposal["captures"] = len(captures["captures"])
        proposal["fixtureDefinitions"] = len(fixtures["fixtures"])
        for name in removed_paths:
            (self.directory / name).unlink()
            del proposal["files"][name]
        for modified in [captures_path, fixtures_path, index_path]:
            proposal["files"][modified.name] = hashlib.sha256(modified.read_bytes()).hexdigest()
        path.write_text(json.dumps(proposal))
        with self.assertRaisesRegex(AssertionError, "Missing discovered contract combinations"):
            verifier.verify(self.directory)

    def test_empty_grid_cannot_be_reclassified_as_a_nonempty_fixture(self):
        self.temp.cleanup()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "proposal"
        shutil.copytree(ROOT / "evidence/reference-proposals/composition-20261012-v1", self.directory)
        path = self.directory / "captures.json"
        manifest = json.loads(path.read_text())
        case = next(c for c in manifest["captures"] if c.get("expectedEmpty"))
        case["componentSize"]["height"] = 20
        path.write_text(json.dumps(manifest))
        proposal_path = self.directory / "proposal.json"
        proposal = json.loads(proposal_path.read_text())
        proposal["files"]["captures.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
        proposal_path.write_text(json.dumps(proposal))
        with self.assertRaisesRegex(AssertionError, "Invalid empty fixture geometry"):
            verifier.verify(self.directory)

    def test_composition_scope_cannot_drop_an_api(self):
        self.temp.cleanup()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "proposal"
        shutil.copytree(ROOT / "evidence/reference-proposals/composition-20261012-v1", self.directory)
        path = self.directory / "captures.json"
        manifest = json.loads(path.read_text())
        manifest["captures"] = [c for c in manifest["captures"] if c["api"] != "BleeckerFeedItem"]
        path.write_text(json.dumps(manifest))
        proposal_path = self.directory / "proposal.json"
        proposal = json.loads(proposal_path.read_text())
        proposal["captures"] = len(manifest["captures"])
        proposal["files"]["captures.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
        proposal_path.write_text(json.dumps(proposal))
        with self.assertRaisesRegex(AssertionError, "Missing composition API"):
            verifier.verify(self.directory)


class CheckboxProposalIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "proposal"
        shutil.copytree(ROOT / "evidence/reference-proposals/checkbox-20261013", self.directory)

    def remove_cases_with_updated_checksums(self, predicate):
        paths = {name: self.directory / name for name in ["captures.json", "fixtures.json", "api-index.json", "proposal.json"]}
        captures = json.loads(paths["captures.json"].read_text())
        removed = [case for case in captures["captures"] if predicate(case)]
        names = {case["path"] for case in removed}
        identifiers = {case["fixture"] for case in removed}
        captures["captures"] = [case for case in captures["captures"] if case["path"] not in names]
        fixtures = json.loads(paths["fixtures.json"].read_text())
        fixtures["fixtures"] = [fixture for fixture in fixtures["fixtures"] if fixture["fixture"] not in identifiers]
        index = json.loads(paths["api-index.json"].read_text())
        for entry in index.values():
            entry["captures"] = [name for name in entry["captures"] if name not in names]
            entry["fixtures"] = [name for name in entry["fixtures"] if name not in identifiers]
        proposal = json.loads(paths["proposal.json"].read_text())
        proposal["captures"] = len(captures["captures"])
        proposal["fixtureDefinitions"] = len(fixtures["fixtures"])
        for name in names:
            (self.directory / name).unlink()
            del proposal["files"][name]
        for name, value in [("captures.json", captures), ("fixtures.json", fixtures), ("api-index.json", index)]:
            paths[name].write_text(json.dumps(value))
            proposal["files"][name] = hashlib.sha256(paths[name].read_bytes()).hexdigest()
        paths["proposal.json"].write_text(json.dumps(proposal))

    def test_scope_cannot_drop_checkbox_api(self):
        self.remove_cases_with_updated_checksums(lambda case: case["api"] == "BleeckerCheckbox")
        with self.assertRaisesRegex(AssertionError, "Missing checkbox API"):
            verifier.verify(self.directory)

    def test_discovered_size_cannot_be_omitted_from_valid_capture_matrix(self):
        self.remove_cases_with_updated_checksums(lambda case: case["api"] == "BleeckerCheckbox" and case["size"] == "lg")
        with self.assertRaisesRegex(AssertionError, "Missing discovered contract combinations"):
            verifier.verify(self.directory)


class SecureFieldProposalIntegrity(unittest.TestCase):
    remove_cases_with_updated_checksums = CheckboxProposalIntegrity.remove_cases_with_updated_checksums

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "proposal"
        shutil.copytree(ROOT / "evidence/reference-proposals/secure-field-20261014", self.directory)

    def test_scope_cannot_drop_secure_field_api(self):
        self.remove_cases_with_updated_checksums(lambda case: case["api"] == "BleeckerSecureField")
        with self.assertRaisesRegex(AssertionError, "Missing secure-field API"):
            verifier.verify(self.directory)

    def test_revealed_disabled_state_cannot_be_omitted(self):
        self.remove_cases_with_updated_checksums(lambda case: case["variant"] == "revealed-disabled")
        with self.assertRaisesRegex(AssertionError, "Missing secure-field state combinations"):
            verifier.verify(self.directory)

    def test_false_reveal_state_is_rejected_with_updated_checksums(self):
        path = self.directory / "captures.json"
        manifest = json.loads(path.read_text())
        case = next(c for c in manifest["captures"] if c["api"] == "BleeckerSecureField")
        case["revealed"] = not case["revealed"]
        path.write_text(json.dumps(manifest))
        proposal_path = self.directory / "proposal.json"
        proposal = json.loads(proposal_path.read_text())
        proposal["files"]["captures.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
        proposal_path.write_text(json.dumps(proposal))
        with self.assertRaisesRegex(AssertionError, "Invalid source reveal/value state"):
            verifier.verify(self.directory)


class SearchFieldProposalIntegrity(unittest.TestCase):
    remove_cases_with_updated_checksums = CheckboxProposalIntegrity.remove_cases_with_updated_checksums

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "proposal"
        shutil.copytree(ROOT / "evidence/reference-proposals/search-field-20261014", self.directory)

    def test_scope_cannot_drop_search_wrapper(self):
        self.remove_cases_with_updated_checksums(lambda c: c['api'] == 'BleeckerSearchField')
        with self.assertRaisesRegex(AssertionError, 'Missing search-field API'):
            verifier.verify(self.directory)

    def test_clear_case_cannot_be_omitted_with_updated_checksums(self):
        self.remove_cases_with_updated_checksums(lambda c: c['variant'] == 'cleared')
        with self.assertRaisesRegex(AssertionError, 'Missing search-field state combinations'):
            verifier.verify(self.directory)

    def test_false_cleared_value_is_rejected_with_updated_checksums(self):
        path = self.directory / 'captures.json'
        manifest = json.loads(path.read_text())
        next(c for c in manifest['captures'] if c['variant'] == 'cleared')['sourceValueAfterAction'] = 'uncleared'
        path.write_text(json.dumps(manifest))
        proposal_path = self.directory / 'proposal.json'
        proposal = json.loads(proposal_path.read_text())
        proposal['files']['captures.json'] = hashlib.sha256(path.read_bytes()).hexdigest()
        proposal_path.write_text(json.dumps(proposal))
        with self.assertRaisesRegex(AssertionError, 'Invalid source clear value'):
            verifier.verify(self.directory)


class CollectionFilterProposalIntegrity(unittest.TestCase):
    remove_cases_with_updated_checksums = CheckboxProposalIntegrity.remove_cases_with_updated_checksums

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "proposal"
        shutil.copytree(ROOT / "evidence/reference-proposals/collection-filters-20261014", self.directory)

    def test_scope_cannot_drop_chip(self):
        self.remove_cases_with_updated_checksums(lambda c: c['api'] == 'BleeckerFilterChip')
        with self.assertRaisesRegex(AssertionError, 'Missing collection-filter API'):
            verifier.verify(self.directory)

    def test_action_case_cannot_be_omitted(self):
        self.remove_cases_with_updated_checksums(lambda c: c['variant'] == 'removed')
        with self.assertRaisesRegex(AssertionError, 'Missing collection-filter state combinations'):
            verifier.verify(self.directory)

    def test_false_caller_state_rejected(self):
        path = self.directory / 'captures.json'
        manifest = json.loads(path.read_text())
        next(c for c in manifest['captures'] if c['variant'] == 'activated')['sourceSelectedAfterAction'] = False
        path.write_text(json.dumps(manifest))
        proposal_path = self.directory / 'proposal.json'
        proposal = json.loads(proposal_path.read_text())
        proposal['files']['captures.json'] = hashlib.sha256(path.read_bytes()).hexdigest()
        proposal_path.write_text(json.dumps(proposal))
        with self.assertRaisesRegex(AssertionError, 'Invalid collection selected state'):
            verifier.verify(self.directory)


class SliderProposalIntegrity(unittest.TestCase):
    remove_cases_with_updated_checksums = CheckboxProposalIntegrity.remove_cases_with_updated_checksums

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "proposal"
        shutil.copytree(ROOT / "evidence/reference-proposals/slider-20261014-v2", self.directory)

    def test_source_pointer_case_cannot_be_omitted(self):
        self.remove_cases_with_updated_checksums(lambda c: c['variant'] == 'clicked-disabled')
        with self.assertRaisesRegex(AssertionError, 'Missing slider state combinations'):
            verifier.verify(self.directory)

    def change_manifest(self, mutate):
        path = self.directory / 'captures.json'
        manifest = json.loads(path.read_text());mutate(manifest)
        path.write_text(json.dumps(manifest))
        proposal_path = self.directory / 'proposal.json';proposal = json.loads(proposal_path.read_text())
        proposal['files']['captures.json'] = hashlib.sha256(path.read_bytes()).hexdigest()
        proposal_path.write_text(json.dumps(proposal))

    def test_fractional_endpoint_cannot_be_rounded_away(self):
        self.change_manifest(lambda m: next(c for c in m['captures'] if c['variant'] == 'clicked-decimal-upper').update(sourceValueAfterAction=0.3))
        with self.assertRaisesRegex(AssertionError, 'Invalid source slider value'):
            verifier.verify(self.directory)

    def test_pending_keyboard_gate_cannot_be_closed(self):
        self.change_manifest(lambda m: m.update(sourceKeyboardStatus='passed'))
        with self.assertRaisesRegex(AssertionError, 'Source keyboard gate cannot be self-approved'):
            verifier.verify(self.directory)


class TabsProposalIntegrity(unittest.TestCase):
    remove_cases_with_updated_checksums = CheckboxProposalIntegrity.remove_cases_with_updated_checksums
    change_manifest = SliderProposalIntegrity.change_manifest
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / 'proposal'
        shutil.copytree(ROOT / 'evidence/reference-proposals/tabs-20261014', self.directory)

    def test_source_pointer_case_cannot_be_omitted(self):
        self.remove_cases_with_updated_checksums(lambda c: c['variant'] == 'external')
        with self.assertRaisesRegex(AssertionError, 'Missing tabs state combinations'):
            verifier.verify(self.directory)

    def test_external_binding_state_cannot_be_falsified(self):
        self.change_manifest(lambda m: next(c for c in m['captures'] if c['variant'] == 'external').update(sourceSelectionAfterAction='c'))
        with self.assertRaisesRegex(AssertionError, 'Invalid source tab selection'):
            verifier.verify(self.directory)

    def test_disabled_callback_count_cannot_be_falsified(self):
        self.change_manifest(lambda m: next(c for c in m['captures'] if c['variant'] == 'disabled-click').update(sourceActivations=1))
        with self.assertRaisesRegex(AssertionError, 'Invalid source tab activation count'):
            verifier.verify(self.directory)

    def test_scope_cannot_drop_tabs(self):
        self.remove_cases_with_updated_checksums(lambda c: c['api'] == 'BleeckerTabs')
        with self.assertRaisesRegex(AssertionError, 'Missing tabs API'):
            verifier.verify(self.directory)


class PaginationProposalIntegrity(unittest.TestCase):
    remove_cases_with_updated_checksums = CheckboxProposalIntegrity.remove_cases_with_updated_checksums
    change_manifest = SliderProposalIntegrity.change_manifest

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / 'proposal'
        shutil.copytree(ROOT / 'evidence/reference-proposals/pagination-20261014', self.directory)

    def test_scope_cannot_drop_icon_button(self):
        self.remove_cases_with_updated_checksums(lambda c: c['api'] == 'BleeckerIconButton')
        with self.assertRaisesRegex(AssertionError, 'Missing pagination API'):
            verifier.verify(self.directory)

    def test_pressed_icons_cannot_be_omitted(self):
        self.remove_cases_with_updated_checksums(lambda c: c.get('sourceAction') == 'pressed')
        with self.assertRaisesRegex(AssertionError, 'Missing icon action cases'):
            verifier.verify(self.directory)

    def test_caller_ownership_cannot_be_falsified(self):
        self.change_manifest(lambda m: next(c for c in m['captures'] if c.get('sourceAction') == 'no-handler').update(sourcePageAfterAction=5))
        with self.assertRaisesRegex(AssertionError, 'Invalid source caller page'):
            verifier.verify(self.directory)

    def test_zero_count_cannot_be_silently_repaired(self):
        self.change_manifest(lambda m: next(c for c in m['captures'] if c['variant'] == 'zero-count').update(sourcePageCountAfterAction=1))
        with self.assertRaisesRegex(AssertionError, 'Invalid source page count'):
            verifier.verify(self.directory)


class ExactPaginationProposalIntegrity(unittest.TestCase):
    remove_cases_with_updated_checksums = CheckboxProposalIntegrity.remove_cases_with_updated_checksums
    change_manifest = SliderProposalIntegrity.change_manifest

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / 'proposal'
        shutil.copytree(ROOT / 'evidence/reference-proposals/pagination-integers-20261014', self.directory)

    def test_source_endpoint_case_cannot_be_omitted(self):
        self.remove_cases_with_updated_checksums(lambda c: c['variant'] == 'next-upper')
        with self.assertRaisesRegex(AssertionError, 'Missing full integer pagination cases'):
            verifier.verify(self.directory)

    def test_rounded_requested_page_cannot_pass(self):
        self.change_manifest(lambda m: next(c for c in m['captures'] if c['variant'] == 'next-beyond').update(sourceRequestedPageDecimal='9007199254740992'))
        with self.assertRaisesRegex(AssertionError, 'Invalid exact requested page'):
            verifier.verify(self.directory)

    def test_count_clamping_cannot_pass(self):
        self.change_manifest(lambda m: next(c for c in m['captures'] if c['variant'] == 'negative-count').update(sourcePageCountAfterActionDecimal='1'))
        with self.assertRaisesRegex(AssertionError, 'Invalid exact page count'):
            verifier.verify(self.directory)
