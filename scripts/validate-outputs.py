#!/usr/bin/env python3
"""
validate-outputs.py: Builder 成果物の自動プリチェック

Validator エージェント起動前に実行し、機械的に検証可能な項目を自動チェックする。
手動の Validator レビューの前段として、明らかな欠落を早期検出する。

Usage:
    python3 scripts/validate-outputs.py --phase 1
    python3 scripts/validate-outputs.py --phase 1 --category research_report
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_file_existence(outputs_dir: Path, phase: int):
    """成果物ディレクトリとメタデータの存在チェック"""
    issues = []
    phase_dir = outputs_dir / f"phase-{phase:02d}"

    if not phase_dir.is_dir():
        issues.append({
            "check": "phase_dir_exists",
            "status": "fail",
            "message": f"outputs/phase-{phase:02d}/ ディレクトリが存在しない"
        })
        return issues, phase_dir

    issues.append({
        "check": "phase_dir_exists",
        "status": "pass",
        "message": f"outputs/phase-{phase:02d}/ ディレクトリが存在する"
    })

    metadata_path = phase_dir / ".metadata.json"
    if not metadata_path.is_file():
        issues.append({
            "check": "metadata_exists",
            "status": "fail",
            "message": ".metadata.json が存在しない"
        })
    else:
        issues.append({
            "check": "metadata_exists",
            "status": "pass",
            "message": ".metadata.json が存在する"
        })
        try:
            meta = load_json(metadata_path)
            for field in ["phase", "deliverables"]:
                if field not in meta:
                    issues.append({
                        "check": f"metadata_field_{field}",
                        "status": "fail",
                        "message": f".metadata.json に必須フィールド '{field}' がない"
                    })
        except (json.JSONDecodeError, Exception) as e:
            issues.append({
                "check": "metadata_valid_json",
                "status": "fail",
                "message": f".metadata.json の JSON パースエラー: {e}"
            })

    # 成果物ファイルが1つ以上あるか
    content_files = [f for f in phase_dir.iterdir()
                     if f.is_file() and not f.name.startswith(".")]
    if not content_files:
        issues.append({
            "check": "has_deliverables",
            "status": "fail",
            "message": "成果物ファイルが1つもない（隠しファイル以外）"
        })
    else:
        issues.append({
            "check": "has_deliverables",
            "status": "pass",
            "message": f"成果物ファイル {len(content_files)} 件"
        })

    return issues, phase_dir


def check_skill_quality_criteria(phase_dir: Path, skills_dir: Path, phase: int):
    """SKILL.md の Quality Criteria を成果物と照合"""
    issues = []
    skill_path = skills_dir / f"phase-{phase:02d}" / "SKILL.md"

    if not skill_path.is_file():
        issues.append({
            "check": "skill_md_exists",
            "status": "fail",
            "message": f"skills/phase-{phase:02d}/SKILL.md が存在しない"
        })
        return issues

    skill_text = skill_path.read_text(encoding="utf-8")

    # Quality Criteria セクションを抽出
    criteria_match = re.search(
        r"## Quality Criteria\s*\n(.*?)(?=\n## |\Z)",
        skill_text, re.DOTALL
    )
    if not criteria_match:
        issues.append({
            "check": "has_quality_criteria",
            "status": "warn",
            "message": "SKILL.md に Quality Criteria セクションがない"
        })
        return issues

    criteria_text = criteria_match.group(1)
    criteria_items = re.findall(r"- \[ \] (.+)", criteria_text)

    if not criteria_items:
        issues.append({
            "check": "has_quality_criteria",
            "status": "warn",
            "message": "Quality Criteria にチェック項目がない"
        })
        return issues

    issues.append({
        "check": "has_quality_criteria",
        "status": "pass",
        "message": f"Quality Criteria: {len(criteria_items)} 項目"
    })

    # 成果物テキストを結合して簡易チェック
    all_output_text = ""
    for f in phase_dir.iterdir():
        if f.is_file() and f.suffix == ".md" and not f.name.startswith("."):
            all_output_text += f.read_text(encoding="utf-8") + "\n"

    # 必須セクションキーワードの簡易存在チェック
    section_keywords = {
        "TL;DR": ["tl;dr", "tldr", "エグゼクティブサマリー", "executive summary"],
        "比較軸": ["比較軸", "評価軸", "comparison", "criteria"],
        "出典": ["出典", "参考文献", "references", "sources"],
        "不確実性": ["不確実性", "留意点", "limitation", "caveat", "注意事項"],
        "リスク": ["リスク", "risk"],
        "次アクション": ["次アクション", "next action", "ロードマップ", "roadmap"],
        "選択肢": ["選択肢", "案a", "案b", "option", "alternative"],
        "テスト": ["test", "pytest", "unittest"],
    }

    for criterion in criteria_items:
        criterion_lower = criterion.lower()
        found_keyword = False
        for label, keywords in section_keywords.items():
            if any(kw in criterion_lower for kw in keywords):
                if any(kw in all_output_text.lower() for kw in keywords):
                    found_keyword = True
                    break
        # We don't mark fail here since this is a heuristic;
        # just record what we found for the Validator to use

    return issues


def check_category_required_sections(phase_dir: Path, category: str):
    """カテゴリテンプレートの必須セクション存在チェック"""
    issues = []

    required_sections = {
        "research_report": [
            ("TL;DR", ["tl;dr", "tldr", "エグゼクティブサマリー", "executive summary"]),
            ("比較軸", ["比較軸", "評価軸", "比較の観点"]),
            ("不確実性・留意点", ["不確実性", "留意点", "limitation", "注意事項"]),
            ("出典・参考文献", ["出典", "参考文献", "references", "sources"]),
        ],
        "small_implementation": [
            ("README", []),  # README.md existence check instead
            ("src/", []),    # Directory existence check
            ("tests/", []),  # Directory existence check
        ],
        "internal_proposal": [
            ("目的と成功条件", ["目的", "成功条件", "objective", "success"]),
            ("選択肢比較", ["選択肢", "案a", "案b", "option", "alternative"]),
            ("リスクと対策", ["リスク", "対策", "risk", "mitigation"]),
            ("次アクション", ["次アクション", "next action", "ロードマップ", "roadmap", "担当"]),
        ],
    }

    if category not in required_sections:
        return issues

    # Collect all output text
    all_output_text = ""
    for f in phase_dir.iterdir():
        if f.is_file() and f.suffix == ".md" and not f.name.startswith("."):
            all_output_text += f.read_text(encoding="utf-8") + "\n"
    all_lower = all_output_text.lower()

    for section_name, keywords in required_sections[category]:
        if category == "small_implementation" and not keywords:
            # Special: check directory/file existence
            target = phase_dir / section_name.rstrip("/")
            if section_name == "README":
                target = phase_dir / "README.md"
            exists = target.exists()
            issues.append({
                "check": f"required_section_{section_name}",
                "status": "pass" if exists else "fail",
                "message": f"{'存在' if exists else '欠落'}: {section_name}"
            })
        elif keywords:
            found = any(kw in all_lower for kw in keywords)
            issues.append({
                "check": f"required_section_{section_name}",
                "status": "pass" if found else "warn",
                "message": f"{'検出' if found else '未検出'}: {section_name} (キーワードベースの簡易チェック)"
            })

    return issues


def main():
    ap = argparse.ArgumentParser(description="Builder 成果物の自動プリチェック")
    ap.add_argument("--phase", type=int, required=True, help="対象フェーズ番号")
    ap.add_argument("--category", type=str, default="", help="タスクカテゴリ (research_report, small_implementation, internal_proposal)")
    ap.add_argument("--project-dir", type=str, default=".", help="プロジェクトルート")
    args = ap.parse_args()

    project = Path(args.project_dir).resolve()
    outputs_dir = project / "outputs"
    skills_dir = project / "skills"

    # Auto-detect category from metadata.json if not specified
    category = args.category
    if not category:
        meta_path = project / "metadata.json"
        if meta_path.is_file():
            try:
                meta = load_json(meta_path)
                category = meta.get("category", "")
            except Exception:
                pass

    all_issues = []

    # Check 1: File existence
    file_issues, phase_dir = check_file_existence(outputs_dir, args.phase)
    all_issues.extend(file_issues)

    if not phase_dir.is_dir():
        print_report(all_issues, args.phase, category)
        sys.exit(1)

    # Check 2: SKILL.md Quality Criteria
    skill_issues = check_skill_quality_criteria(phase_dir, skills_dir, args.phase)
    all_issues.extend(skill_issues)

    # Check 3: Category-specific required sections
    if category:
        section_issues = check_category_required_sections(phase_dir, category)
        all_issues.extend(section_issues)

    print_report(all_issues, args.phase, category)

    # Exit code: 1 if any fail, 0 otherwise
    has_fail = any(i["status"] == "fail" for i in all_issues)
    sys.exit(1 if has_fail else 0)


def print_report(issues, phase, category):
    """プリチェック結果を表示"""
    pass_count = sum(1 for i in issues if i["status"] == "pass")
    warn_count = sum(1 for i in issues if i["status"] == "warn")
    fail_count = sum(1 for i in issues if i["status"] == "fail")

    print(f"=== Pre-Validation: Phase {phase} ===")
    if category:
        print(f"Category: {category}")
    print()

    for issue in issues:
        icon = {"pass": "✓", "warn": "⚠", "fail": "✗"}[issue["status"]]
        print(f"  {icon} [{issue['check']}] {issue['message']}")

    print()
    print(f"Result: {pass_count} pass, {warn_count} warn, {fail_count} fail")

    if fail_count > 0:
        print("Status: FAIL - Validator 実行前に修正が必要")
    elif warn_count > 0:
        print("Status: WARN - Validator で詳細確認を推奨")
    else:
        print("Status: PASS - Validator 実行可能")


if __name__ == "__main__":
    main()
