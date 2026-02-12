SDD toolkit v6.1（自己改善(A) + 自己評価(A案) + 採点安定化）

# SDD Toolkit（Spec-Driven Development for Claude Code）

Claude Code の `/init-task` を起点に、タスクを **仕様 → 実装（成果物生成）→ 検証 → 完了処理** の流れで進めるための、プロジェクトテンプレートです。

> 目的：Claude に「順序立てて考え、仕様を作り、成果物を生成し、最後に知見を残す」運用を定着させる

---

## 使い方（最短）

1. このリポジトリを作業ディレクトリに配置（git clone / zip 展開など）
2. Claude Code を起動（リポジトリ直下で）
3. `/init-task` を実行して、`docs/` に仕様ファイルを作る
4. 仕様に沿って成果物を作成（通常は `outputs/` 配下に生成）
5. 最後に `/finalize` を実行して、パッケージング＆知見蓄積（`~/.sdd-knowledge/`）

---

## ディレクトリ構成

```text
.claude/
├── agents/                 # サブエージェント（planner / researcher / builder / validator）
├── hooks/                  # hook の実行スクリプト（python）
├── rules/                  # ルール（CLAUDE.md 相当の補助）
├── skills/                 # スキル（/init-task, /finalize など）
└── settings.json           # Claude Code hooks 設定（プロジェクトスコープ）
```

---

## 主なスキル

- `/init-task`（`.claude/skills/init-task/SKILL.md`）
  - タスク分類、仕様ファイル雛形の生成、`metadata.json` の初期化
  - `docs/_manifest.json` も作成（hook での仕様整合チェック用）

- `/finalize`（`.claude/skills/finalize/SKILL.md`）
  - `outputs/` をまとめて成果物パッケージ化
  - `~/.sdd-knowledge/` にアーカイブ／スターター抽出／振り返り準備

- `/lessons`（`.claude/skills/lessons/SKILL.md`）
  - 過去の知見（retrospectives）を検索・参照

- `/run-phase`（`.claude/skills/run-phase/SKILL.md`）
  - Builder / Validator パターンでフェーズを実行・検証

- `/retrospective`（`.claude/skills/retrospective/SKILL.md`）
  - 構造化振り返りを行い、学びを `~/.sdd-knowledge/` に蓄積

- `/update-docs`（`.claude/skills/update-docs/SKILL.md`）
  - docs/ の充実度を診断し、対話的に補完・整合チェック

---

## hooks（自動ガード）

このテンプレートは `.claude/settings.json` に hook を定義しています。

- PreToolUse（Write/Edit の前）  
  `outputs/` に書き込む前に `docs/`（仕様）の存在を軽くチェックし、無い場合は警告します（ブロックはしません）。

- Stop  
  `outputs/` に成果物があるのに `/finalize` が未実行の場合、リマインドします。

- SessionStart  
  `~/.sdd-knowledge/` のスターター／教訓の有無を簡易表示します。

---

## 知識ベース（ローカル）

`~/.sdd-knowledge/` に以下を保存します（ローカル環境にのみ作られます）。

- `starters/` : 再利用できるプロジェクト雛形
- `retrospectives/` : 振り返り（教訓）
- `docs-archive/` : 完了プロジェクトのアーカイブ

---

## 注意

- `.claude/settings.json` は **プロジェクトスコープ** の設定です。個人スコープで hooks を共通化したい場合は `~/.claude/settings.json` も利用できます。
- Windows で zip 展開したファイルに `*:Zone.Identifier` が混ざることがあります。`.gitignore` で除外しています。

---

# v6: Self-Improvement & Evaluation (A案)

このv6では、SDD toolkit 自身を **(A) リポジトリ/テンプレ/ルール/コマンドを改良する** という意味で「自己改善」し、その改善を **同じ土俵で自己評価**できる仕組みを同梱しています（モデルの重み更新はしません）。

## 追加されたもの
- `.claude/commands/`
  - `/init-task` : タスク分類＋専門家エージェント召喚（generated agents）
  - `/eval <iteration_id>` : 固定3シナリオで採点→履歴化→レポート化
  - `/plot` : 履歴からグラフ生成
  - `/improve-toolkit <iteration_id>` : 改良→評価→記録の一連手順
- `templates/team-roster.json` : タスク分類→召喚する専門家の辞書
- `templates/agents/*.md` : 専門家エージェントのテンプレ
- `eval/` : A案評価フレームワーク（履歴JSON/CSV、レーダー/時系列プロット）

## 最短の運用フロー（自己改善ループ）
1. 改良テーマを決める → `/improve-toolkit v6.1`
2. 変更を実装（README/commands/templates/rules 等）
3. `/eval v6.1` で採点（runs を作る）
4. `python3 eval/aggregate.py --iteration v6.1` で履歴化＆プロット生成
5. `eval/reports/YYYY-MM-DD_v6.1.md` に結果を残す（前回比較）

## グラフ
- `eval/plots/radar_latest.png`
- `eval/plots/timeseries_overall.png`

※PNG生成には `matplotlib` が必要です。無い場合でも JSON/CSV は生成されます（`eval/plots/README.md` を参照）。
