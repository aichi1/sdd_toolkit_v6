# /eval <iteration_id>

このコマンドは「自己評価（A案）」を実行します。**固定3シナリオ（T1/T2/T3）**を同じ基準で採点し、履歴を保存し、グラフを更新します。

採点ブレを抑えるため、必ず **`eval/SCORING_GUIDE.md`** の手順に従ってください。

## 入力
- iteration_id（例：v6.1, 2026-02-12_1 など）

## 手順

### 0) 準備
- `eval/rubric.json`（評価軸）を確認
- `eval/SCORING_GUIDE.md`（採点手順/アンカー/上限制約）を確認
- （必要なら）`templates/eval_scoring_prompt.md` を参照して、採点時の“型”を守る

### 1) シナリオの確認
`eval/scenarios/` にある3シナリオを読み、各シナリオの「期待成果物」と「チェックリスト」を理解します：
- T1_research
- T2_implement
- T3_proposal

### 2) 各シナリオの採点（0〜5点、整数）
各シナリオごとに、次の軸を 0〜5 点で採点し、根拠とメトリクスを添えて保存してください：

軸（rubric）：`eval/rubric.json` の axes を使用
- correctness
- completeness
- efficiency
- robustness
- maintainability
- usability
- safety

保存先：
`eval/runs/<iteration_id>/<scenario>/score.json`

score.json の必須項目（最低限）：
- scores（各軸 0〜5、整数）
- checklist（各チェック項目の pass/partial/fail と evidence）
- metrics（任意：turns, retries, manifest_fill_rate など。分からない場合は "unknown"）
- evidence_files（参照した主要ファイルパス配列）
- notes（短文で良い：上げられない理由/改善点）

> 採点は **証拠（evidence）ベース**。推測で点を上げない。

### 3) 集計と履歴化（自動ファイル生成）
採点が揃ったら、ターミナルで次を実行してください：

`python3 eval/aggregate.py --iteration <iteration_id>`

これにより：
- `eval/history/<date>_<iteration_id>.json` が作成/更新
- `eval/summary.csv` が更新
- matplotlib があれば `eval/plots/` にPNGが生成

### 4) レポート
最後に `eval/reports/<date>_<iteration_id>.md` を作り、
- overall のレーダー形状の要約
- 前回から上がった/下がった軸（前回との差分）
- 次の改善仮説（最大3つ）
を簡潔に記述してください（根拠のファイルパスも添える）。
