# LangExtract JSON統合スクリプト

このスクリプトは、LangExtractの出力JSONファイルを読み込み、統合キーに基づいてオブジェクトをグループ化し、ベクトルDB化用の統合データを作成します。

## 機能概要

- **統合キーによるグループ化**: `product_name`, `model_name`, `category`, `application`, `company_name`などのキーに基づいてオブジェクトを統合
- **attributesのマージ**: 重複キーは値が異なる場合にリスト化、リストは結合してユニーク化
- **summary自動生成**: extraction_textとattributesから短い文章を自動生成
- **個別オブジェクト保持**: 統合キーが全て欠けているオブジェクトは個別に保持

## インストール要件

- Python 3.10以上
- 標準ライブラリのみ使用（追加パッケージ不要）

## 使用方法

### 一括処理（推奨）

```bash
python json_integration.py
```

outディレクトリ内のすべてのJSONLファイルを自動的に処理します。各ファイルに対して `元ファイル名_integrated.json` として出力されます。

### 単一ファイル処理

```bash
python json_integration.py input_file.jsonl
```

指定したファイルのみを処理します。出力ファイルは元ファイルと同じディレクトリに `元ファイル名_integrated.json` として保存されます。

### オプション付きの使用方法

```bash
# 一括処理（詳細情報付き）
python json_integration.py --verbose

# 単一ファイル処理（カスタム出力ファイル名）
python json_integration.py input_file.jsonl -o output_file.json --verbose
```

### コマンドライン引数

- `input_file`: 入力JSONLファイルのパス（省略時は一括処理）
- `-o, --output`: 出力JSONファイルのパス（単一ファイル処理時のみ有効、指定しない場合は元ファイル名に_integratedを追記）
- `--verbose, -v`: 詳細な処理情報を表示

## 出力形式

統合されたオブジェクトは以下の形式で出力されます：

```json
{
  "id": "統合キーの値",
  "classes": ["extraction_class1", "extraction_class2"],
  "text": "統合されたテキスト（重複除去、最大3つまで）",
  "attributes": {
    "キー1": "値1",
    "キー2": ["値2a", "値2b"],
    "キー3": "値3",
    "numeric_data": [
      ["6", "%", "エラー率"],
      ["4.8", "%", "実世界でのエラー率"],
      ["$1.25", "$/1Mトークン", "入力料金", "2024"]
    ]
  }
}
```

### 数値データのタプル形式

数値関連のデータ（`value`, `unit`, `context`, `year`, `target`など）は、`numeric_data`配列内でタプル形式（`[value, unit, context, year, target]`）で保存されます。これにより、どの値がどの単位や文脈に対応するかが明確になります。

例：
- `["6", "%", "エラー率"]` → 値6、単位%、文脈エラー率
- `["$1.25", "$/1Mトークン", "入力料金", "2024"]` → 値$1.25、単位$/1Mトークン、文脈入力料金、年2024

## 統合キー

以下のattributesキーが統合キーとして使用されます：

- `product_name`: 製品名
- `model_name`: モデル名
- `category`: カテゴリ
- `application`: アプリケーション
- `company_name`: 会社名
- `name`: 名前
- `target`: ターゲット
- `market_type`: 市場タイプ

## 処理の詳細

### 1. グループ化

統合キーのいずれかが一致するオブジェクトを同じグループにまとめます。

### 2. attributesのマージ

- 重複キー → 値が違えばリスト化
- リストは結合してユニーク化
- "N/A"は可能なら除外

### 3. summaryの生成

各オブジェクトの`extraction_text`から重要な部分を抽出し、最大5つまで結合します。

### 4. sourcesの保持

元の`extraction_class`と`extraction_text`を保持します。

## 使用例

### 一括処理（推奨）

```bash
python json_integration.py --verbose
```

出力例：
```
Found 9 JSONL files in 'out' directory

============================================================
Processing: report_laboauto_results.jsonl
============================================================
Processing file: out/report_laboauto_results.jsonl
Loaded 113 extractions
Created 55 groups
Found 44 standalone objects
✓ Successfully processed: report_laboauto_results_integrated.json

============================================================
Processing: ticket_results.jsonl
============================================================
Processing file: out/ticket_results.jsonl
Loaded 13 extractions
Created 0 groups
Found 13 standalone objects
✓ Successfully processed: ticket_results_integrated.json

============================================================
Batch processing completed: 9/9 files processed successfully
============================================================
```

### 単一ファイル処理

```bash
python json_integration.py out/report_laboauto_results.jsonl --verbose
```

出力ファイル: `out/report_laboauto_results_integrated.json`

出力例：
```
Processing file: out/report_laboauto_results.jsonl
Loaded 113 extractions
Created 55 groups
Found 44 standalone objects

Integration Summary for report_laboauto_results.jsonl:
- Total integrated objects: 99
- Objects with integration keys: 55
- Standalone objects: 44

Integration Key Usage:
  target: 16
  name: 1
  category: 1
  application: 20
  company_name: 16
  product_name: 1
  standalone: 44
Saved 99 integrated objects to out/report_laboauto_results_integrated.json
```

## 注意事項

- 統合キーが全て欠けているオブジェクトは`standalone_X`のIDで個別に保持されます
- 同じ統合キーを持つ複数のオブジェクトは1つに統合されます
- attributesの値が"N/A"の場合は可能な限り除外されます
- 出力ファイルはUTF-8エンコーディングで保存されます

## エラーハンドリング

- ファイルが見つからない場合はエラーメッセージを表示して終了
- JSONの解析エラーがある場合は警告を表示してスキップ
- その他のエラーが発生した場合は詳細なエラー情報を表示（--verboseオプション使用時）

## ベクトルDB化での活用

統合されたデータは以下の点でベクトルDB化に適しています：

1. **統一されたID**: 統合キーがIDとして使用されるため、重複を避けられる
2. **豊富な属性**: マージされたattributesにより、より多くの情報を含む
3. **要約文**: 自動生成されたsummaryにより、検索精度が向上
4. **出典情報**: sourcesにより元の情報を追跡可能
