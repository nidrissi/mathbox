"""Compare only API-free archived preparation functions with the native helper."""
import argparse
import ast
from contextlib import redirect_stdout
from dataclasses import dataclass
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', required=True, type=Path, help='Trusted archived reviewer.py; selected API-free functions are executed')
    parser.add_argument('--reference-version', default=None)
    parser.add_argument('--archive', type=Path, help='Optional original archive for provenance hashing')
    parser.add_argument('--output', type=Path, help='Write JSON here; otherwise print it')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    reference = args.reference
    functions = {'strip_comment', '_split_comment', 'mask_non_content', '_resolve_reference', '_is_within',
                 'resolve_inputs', '_front_matter', 'chunk_by_section', 'chunk_key',
                 'extract_global_context'}
    constants = {'_LITERAL_ENVS', '_LITERAL_ENV_RE', 'SECTION_RE', '_LATEX_CMD_RE',
                 '_SKIP_SECTIONS', 'INPUT_RE', 'MAX_INPUT_DEPTH', 'FRONT_MATTER_MIN_CHARS',
                 'FRONT_MATTER_NAME', 'ABSTRACT_RE', 'TITLE_RE', 'PREAMBLE_RE',
                 'THEOREM_DEFINITION_RE', 'BEGIN_DOCUMENT_RE'}
    tree = ast.parse(reference.read_text())
    selected = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in functions:
            selected.append(node)
        elif isinstance(node, ast.ClassDef) and node.name == 'Chunk':
            selected.append(node)
        elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in constants for t in node.targets):
            selected.append(node)
    module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), *selected], type_ignores=[])
    namespace = {'re': re, 'Path': Path, 'hashlib': hashlib, 'dataclass': dataclass,
                 'ConfigurationError': ValueError}
    exec(compile(ast.fix_missing_locations(module), str(reference), 'exec'), namespace)
    spec = importlib.util.spec_from_file_location('prepare', repo / 'skills/referee/scripts/prepare_manuscript.py')
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)

    def paper(body, preamble=''):
        return preamble + '\\begin{document}\n' + body + '\\end{document}\n'

    results = []

    def titles(text):
        old = [c.name for c in namespace['chunk_by_section'](text)]
        units, _ = native.extract(text, [])
        new = [u['title'] for u in units if u['reviewable'] and u['kind'] == 'section']
        return old, new

    for label, text in [
        ('ordinary-sections', paper('\\section{One}\na\n\\section{Two}\nb\n')),
        ('commented-section', paper('\\section{Real}\na\n% \\section{Fake}\nb\n\\section{Last}\nc\n')),
        ('verbatim-section', paper('\\section{Real}\n\\begin{verbatim}\n\\section{References}\n\\end{verbatim}\nlast\n')),
        ('bibliography-heading', paper('\\section{Main}\nx\n\\section*{References}\ny\n\\section{Appendix}\nz\n')),
        ('one-nested-title', paper('\\section{The $\\mathbb{Z}$-case}\nx\n')),
    ]:
        old, new = titles(text)
        assert old == new, (label, old, new)
        results.append({'case': label, 'reference': old, 'native': new, 'result': 'preserved'})

    for label, text in [
        ('inline-literal-section', paper('\\section{Real}\n\\verb|\\section{Fake}|\n')),
        ('commented-verbatim-opener', paper('% \\begin{verbatim}\n\\section{Real}\nbody\n% \\end{verbatim}\n')),
        ('balanced-deep-title', paper('\\section{The {nested {deep}} case}\nbody\n')),
    ]:
        old, new = titles(text)
        assert new == (['The {nested {deep}} case'] if label == 'balanced-deep-title' else ['Real'])
        assert old != new
        results.append({'case': label, 'reference': old, 'native': new, 'result': 'intentional-improvement'})

    with TemporaryDirectory(prefix='referee-compare-') as directory:
        root = Path(directory) / 'project'
        root.mkdir()
        main = root / 'paper.tex'
        (root / 'parts').mkdir()
        (root / 'parts/a.tex').write_text('\\section{Included}\nA\n\\input b\n')
        (root / 'parts/b.tex').write_text('B\n')
        main.write_text(paper('\\input{parts/a}\n\\include{parts/b}\n'))
        old = namespace['resolve_inputs'](main)
        manifest, new, _ = native.prepare(main, root)
        assert old == new
        results.append({'case': 'nested-and-repeated-inputs', 'result': 'preserved', 'expanded_sha256': native.digest(new)})

        (root / 'quoted.tex').write_text('QUOTED FILE\n')
        main.write_text(paper('\\section{Main}\n\\begin{verbatim}\n\\input{quoted}\n\\end{verbatim}\n'))
        old = namespace['resolve_inputs'](main)
        manifest, new, _ = native.prepare(main, root)
        assert 'QUOTED FILE' in old and 'QUOTED FILE' not in new
        results.append({'case': 'literal-input-not-expanded', 'reference_expands_literal': True, 'native_expands_literal': False, 'result': 'intentional-improvement'})

        (root / 'boundary.tex').write_text('Text % final comment')
        main.write_text(paper('\\input{boundary}\\section{Real}\nbody\n'))
        old = namespace['resolve_inputs'](main)
        manifest, new, _ = native.prepare(main, root)
        old_titles = [c.name for c in namespace['chunk_by_section'](old)]
        new_titles = [u['title'] for u in manifest['units'] if u['kind'] == 'section']
        assert old_titles == [] and new_titles == ['Real']
        results.append({'case': 'input-eof-comment-boundary', 'reference': old_titles,
                        'native': new_titles, 'result': 'intentional-improvement'})

        for label, text in [('missing-input', paper('\\input{missing}\n')),
                            ('cyclic-input', paper('\\input{paper}\n')),
                            ('out-of-tree-input', paper('\\input{../outside}\n'))]:
            (root.parent / 'outside.tex').write_text('SYNTHETIC OUTSIDE CONTENT\n')
            main.write_text(text)
            with redirect_stdout(io.StringIO()):
                old = namespace['resolve_inputs'](main)
            try:
                native.prepare(main, root)
                raise AssertionError(label + ' unexpectedly accepted')
            except native.PreparationError:
                pass
            assert 'SYNTHETIC OUTSIDE CONTENT' not in old
            results.append({'case': label, 'reference': 'warns and continues', 'native': 'explicit preparation failure', 'result': 'intentional-stricter-coverage'})
            (root.parent / 'outside.tex').unlink()

        base = paper('\\section{A}\na\n\\section{B}\nb\n')
        changed = paper('\\section{A}\na\n\\section{B}\nb\n\\section{New}\nnew\n')
        before = namespace['chunk_by_section'](base)[1]
        after = namespace['chunk_by_section'](changed)[1]
        old_stable = namespace['chunk_key'](before) == namespace['chunk_key'](after)
        new_before = native.extract(base, [])[0][1]
        new_after = native.extract(changed, [])[0][1]
        new_stable = new_before['id'] == new_after['id']
        assert not old_stable and new_stable
        results.append({'case': 'append-section-preserves-former-last-unit', 'reference_stable': old_stable, 'native_stable': new_stable, 'result': 'intentional-improvement'})

    text = paper('Short substantive front matter.\n\\section{Main}\nbody\n')
    old = [c.name for c in namespace['chunk_by_section'](text)]
    new = [u['title'] for u in native.extract(text, [])[0]]
    assert old == ['Main'] and new == ['Front matter', 'Main']
    results.append({'case': 'short-front-matter-retained', 'reference': old, 'native': new, 'result': 'intentional-improvement'})

    text = paper('\\section{Main}\n\\begin{prop}\\label{p:one}Claim\\end{prop}\n',
                 '\\newtheorem{prop}{Proposition}\n')
    old = namespace['extract_global_context'](text)
    new_context = native.extract(text, [])[1]
    assert 'Claim' not in old and new_context['statements'][0]['label'] == 'p:one'
    results.append({'case': 'custom-theorem-context', 'reference_indexes_prop': False, 'native_indexes_prop': True, 'result': 'intentional-improvement'})

    record = {'schema_version': 1, 'scope': 'API-free archived algorithms on synthetic inputs, not model performance',
              'reference_version': args.reference_version,
              'reference_archive_sha256': hashlib.sha256(args.archive.read_bytes()).hexdigest() if args.archive else None,
              'reference_reviewer_sha256': hashlib.sha256(reference.read_bytes()).hexdigest(),
              'native_contract_sha256': native.contract_digest(), 'cases': results,
              'cases_passed': len(results)}
    if args.output is None:
        print(json.dumps(record, indent=2))
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2) + '\n')
        print(json.dumps({'cases': len(results), 'artifact': str(args.output)}))


if __name__ == "__main__":
    main()
