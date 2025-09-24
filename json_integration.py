#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangExtract出力JSON統合スクリプト

このスクリプトは、LangExtractの出力JSONファイルを読み込み、
統合キー（product_name, model_name, category, application, company_nameなど）に基づいて
オブジェクトをグループ化し、ベクトルDB化用の統合データを作成します。
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Set, Optional
from collections import defaultdict


class LangExtractIntegrator:
    """
    LangExtract出力JSONを統合するクラス
    """
    
    # 統合キーとして使用するattributesのキー
    # out配下の既存JSONを走査した結果、以下のキーが同義語として混在
    # - product_name / product name
    # - model_name   / model name
    # 既存のキーは維持しつつ、スペース区切りの別名も受け付ける
    INTEGRATION_KEYS = {
        # 製品・モデル名（表記ゆれ対応）
        'product_name', 'product name',
        'model_name', 'model name',
        # 分類・用途
        'category', 'application',
        # 企業・名称など
        'company_name', 'name',
        # その他既存キー
        'target', 'market_type'
    }
    
    def __init__(self):
        """初期化"""
        self.integrated_objects = []
        self.standalone_objects = []
    
    def load_jsonl(self, file_path: str) -> List[Dict[str, Any]]:
        """
        JSONLファイルを読み込む
        
        Args:
            file_path: JSONLファイルのパス
            
        Returns:
            抽出データのリスト
        """
        extractions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        if 'extractions' in data:
                            extractions.extend(data['extractions'])
                        else:
                            print(f"Warning: Line {line_num} does not contain 'extractions' key")
                    except json.JSONDecodeError as e:
                        print(f"Error parsing line {line_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            sys.exit(1)
            
        return extractions
    
    def extract_integration_keys(self, attributes: Dict[str, Any]) -> Set[str]:
        """
        attributesから統合キーの値を抽出する
        
        Args:
            attributes: オブジェクトのattributes辞書
            
        Returns:
            統合キーの値のセット
        """
        integration_values = set()
        
        for key in self.INTEGRATION_KEYS:
            if key in attributes:
                value = attributes[key]
                if value and value != "N/A":
                    # リストの場合は各要素を追加
                    if isinstance(value, list):
                        for item in value:
                            if item and item != "N/A":
                                integration_values.add(str(item))
                    else:
                        integration_values.add(str(value))
        
        return integration_values
    
    def merge_attributes(self, attributes_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        複数のattributesをマージする
        
        Args:
            attributes_list: マージするattributesのリスト
            
        Returns:
            マージされたattributes辞書
        """
        merged = {}
        
        # 数値データをタプル形式で収集
        numeric_tuples = self._extract_numeric_tuples(attributes_list)
        
        # 通常の属性をマージ
        for attrs in attributes_list:
            for key, value in attrs.items():
                if value == "N/A" or not value:
                    continue
                
                # 数値関連のキーはスキップ（後で処理）
                if key in {'value', 'unit', 'context', 'year', 'target', 'size', 'rate', 'price', 'currency'}:
                    continue
                
                # 通常のマージ処理
                if key not in merged:
                    merged[key] = value
                else:
                    existing = merged[key]
                    
                    # 既存の値と同じ場合はスキップ
                    if existing == value:
                        continue
                    
                    # 異なる値の場合はリスト化
                    if not isinstance(existing, list):
                        merged[key] = [existing]
                    
                    # 新しい値を追加（重複を避ける）
                    if isinstance(value, list):
                        for item in value:
                            if item not in merged[key]:
                                merged[key].append(item)
                    else:
                        if value not in merged[key]:
                            merged[key].append(value)
        
        # 数値データをタプル形式で追加
        if numeric_tuples:
            merged['numeric_data'] = numeric_tuples
        
        return merged
    
    def _extract_numeric_tuples(self, attributes_list: List[Dict[str, Any]]) -> List[List[str]]:
        """
        数値データをタプル形式（[value, unit, context]）で抽出する
        
        Args:
            attributes_list: 属性のリスト
            
        Returns:
            タプル形式の数値データのリスト
        """
        numeric_tuples = []
        
        for attrs in attributes_list:
            # 数値関連のキーを持つオブジェクトをチェック
            numeric_keys = {}
            for key in {'value', 'unit', 'context', 'year', 'target', 'size', 'rate', 'price', 'currency'}:
                if key in attrs and attrs[key] != "N/A" and attrs[key]:
                    numeric_keys[key] = attrs[key]
            
            if numeric_keys:
                # タプルを作成: [value, unit, context, year, target]
                tuple_data = []
                
                # 優先順位に従って値を取得
                tuple_data.append(numeric_keys.get('value', ''))
                tuple_data.append(numeric_keys.get('unit', ''))
                tuple_data.append(numeric_keys.get('context', ''))
                tuple_data.append(numeric_keys.get('year', ''))
                tuple_data.append(numeric_keys.get('target', ''))
                
                # 空でない値のみを保持
                tuple_data = [str(v) for v in tuple_data if v and str(v).strip()]
                
                if tuple_data:
                    numeric_tuples.append(tuple_data)
        
        return numeric_tuples
    
    def generate_summary(self, extractions: List[Dict[str, Any]]) -> str:
        """
        抽出データからsummaryを自動生成する
        
        Args:
            extractions: 統合する抽出データのリスト
            
        Returns:
            生成されたsummary文字列
        """
        summary_parts = []
        
        for extraction in extractions:
            # extraction_textから重要な部分を抽出
            extraction_text = extraction.get('extraction_text', '')
            if extraction_text:
                # 長すぎる場合は切り詰め
                if len(extraction_text) > 100:
                    extraction_text = extraction_text[:97] + "..."
                summary_parts.append(extraction_text)
        
        # 重複を除去して結合
        unique_parts = list(dict.fromkeys(summary_parts))  # 順序を保持しつつ重複除去
        summary = " | ".join(unique_parts[:5])  # 最大5つまで
        
        return summary
    
    def group_extractions(self, extractions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        統合キーに基づいて抽出データをグループ化する
        
        Args:
            extractions: 抽出データのリスト
            
        Returns:
            グループ化された抽出データの辞書
        """
        groups = defaultdict(list)
        
        for extraction in extractions:
            attributes = extraction.get('attributes', {})
            integration_keys = self.extract_integration_keys(attributes)
            
            if integration_keys:
                # 統合キーがある場合は、最初のキーでグループ化
                primary_key = next(iter(integration_keys))
                groups[primary_key].append(extraction)
            else:
                # 統合キーがない場合は個別オブジェクトとして扱う
                self.standalone_objects.append(extraction)
        
        return groups
    
    def integrate_group(self, group_key: str, extractions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        グループ化された抽出データを統合する
        
        Args:
            group_key: グループのキー
            extractions: グループ内の抽出データのリスト
            
        Returns:
            統合されたオブジェクト
        """
        # classesの収集
        classes = list(set(ext.get('extraction_class', '') for ext in extractions))
        classes = [cls for cls in classes if cls]  # 空文字列を除外
        
        # attributesのマージ
        attributes_list = [ext.get('attributes', {}) for ext in extractions]
        merged_attributes = self.merge_attributes(attributes_list)
        
        # 統合されたテキストを作成（重複を避けて）
        unique_texts = []
        seen_texts = set()
        
        for ext in extractions:
            text = ext.get('extraction_text', '').strip()
            if text and text not in seen_texts:
                unique_texts.append(text)
                seen_texts.add(text)
        
        # 統合されたテキストを結合（最大3つまで）
        combined_text = " | ".join(unique_texts[:3])
        
        # ベクトルDB化に適した簡潔な形式
        result = {
            'id': group_key,
            'classes': classes,
            'text': combined_text,
            'attributes': merged_attributes
        }
        
        return result
    
    def process_file(self, input_file: str) -> List[Dict[str, Any]]:
        """
        JSONLファイルを処理して統合データを作成する
        
        Args:
            input_file: 入力ファイルのパス
            
        Returns:
            統合されたオブジェクトのリスト
        """
        print(f"Processing file: {input_file}")
        
        # データの読み込み
        extractions = self.load_jsonl(input_file)
        print(f"Loaded {len(extractions)} extractions")
        
        # グループ化
        groups = self.group_extractions(extractions)
        print(f"Created {len(groups)} groups")
        print(f"Found {len(self.standalone_objects)} standalone objects")
        
        # 各グループを統合
        integrated_objects = []
        for group_key, group_extractions in groups.items():
            integrated_obj = self.integrate_group(group_key, group_extractions)
            integrated_objects.append(integrated_obj)
        
        # 個別オブジェクトも統合データ形式に変換
        for standalone in self.standalone_objects:
            standalone_obj = self.integrate_group(
                f"standalone_{len(self.integrated_objects)}", 
                [standalone]
            )
            integrated_objects.append(standalone_obj)
        
        self.integrated_objects = integrated_objects
        return integrated_objects
    
    def save_json(self, output_file: str, data: List[Dict[str, Any]]) -> None:
        """
        統合データをJSONファイルに保存する
        
        Args:
            output_file: 出力ファイルのパス
            data: 保存するデータ
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(data)} integrated objects to {output_file}")
        except Exception as e:
            print(f"Error saving file {output_file}: {e}")
            sys.exit(1)


def process_single_file(input_file: str, output_file: str, verbose: bool = False) -> bool:
    """
    単一ファイルを処理する
    
    Args:
        input_file: 入力ファイルのパス
        output_file: 出力ファイルのパス
        verbose: 詳細情報を表示するかどうか
        
    Returns:
        処理が成功したかどうか
    """
    integrator = LangExtractIntegrator()
    
    try:
        integrated_data = integrator.process_file(input_file)
        
        if verbose:
            print(f"\nIntegration Summary for {Path(input_file).name}:")
            print(f"- Total integrated objects: {len(integrated_data)}")
            print(f"- Objects with integration keys: {len(integrated_data) - len(integrator.standalone_objects)}")
            print(f"- Standalone objects: {len(integrator.standalone_objects)}")
            
            # 統合キーの使用状況を表示
            key_usage = defaultdict(int)
            for obj in integrated_data:
                if obj['id'].startswith('standalone_'):
                    key_usage['standalone'] += 1
                else:
                    # 統合キーの種類を推定
                    attrs = obj['attributes']
                    for key in integrator.INTEGRATION_KEYS:
                        if key in attrs:
                            key_usage[key] += 1
                            break
                    else:
                        key_usage['other'] += 1
            
            print(f"\nIntegration Key Usage:")
            for key, count in key_usage.items():
                print(f"  {key}: {count}")
        
        # 結果の保存
        integrator.save_json(str(output_file), integrated_data)
        return True
        
    except Exception as e:
        print(f"Error during processing {input_file}: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='LangExtract出力JSONを統合してベクトルDB化用データを作成する'
    )
    parser.add_argument(
        'input_file', 
        nargs='?',
        help='入力JSONLファイルのパス（指定しない場合はoutディレクトリ内の全ファイルを処理）'
    )
    parser.add_argument(
        '-o', '--output', 
        help='出力JSONファイルのパス (単一ファイル処理時のみ有効、指定しない場合は元ファイル名に_integratedを追記)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細な処理情報を表示する'
    )
    
    args = parser.parse_args()
    
    # 単一ファイル処理の場合
    if args.input_file:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: Input file does not exist: {args.input_file}")
            sys.exit(1)
        
        # 出力ファイル名の決定
        if args.output:
            output_file = args.output
        else:
            # 元ファイル名に_integratedを追記し、拡張子を.jsonに変更
            output_file = input_path.with_suffix('').name + '_integrated.json'
            # 元ファイルと同じディレクトリに出力
            output_file = input_path.parent / output_file
        
        success = process_single_file(str(input_path), str(output_file), args.verbose)
        if not success:
            sys.exit(1)
    
    # 一括処理の場合
    else:
        out_dir = Path("out")
        if not out_dir.exists():
            print("Error: 'out' directory does not exist")
            sys.exit(1)
        
        # outディレクトリ内のJSONLファイルを検索
        jsonl_files = list(out_dir.glob("*.jsonl"))
        if not jsonl_files:
            print("No .jsonl files found in 'out' directory")
            sys.exit(1)
        
        print(f"Found {len(jsonl_files)} JSONL files in 'out' directory")
        
        success_count = 0
        total_count = len(jsonl_files)
        
        for jsonl_file in jsonl_files:
            print(f"\n{'='*60}")
            print(f"Processing: {jsonl_file.name}")
            print(f"{'='*60}")
            
            # 出力ファイル名を決定
            output_file = jsonl_file.with_suffix('').name + '_integrated.json'
            output_file = jsonl_file.parent / output_file
            
            success = process_single_file(str(jsonl_file), str(output_file), args.verbose)
            if success:
                success_count += 1
                print(f"✓ Successfully processed: {output_file.name}")
            else:
                print(f"✗ Failed to process: {jsonl_file.name}")
        
        print(f"\n{'='*60}")
        print(f"Batch processing completed: {success_count}/{total_count} files processed successfully")
        print(f"{'='*60}")
        
        if success_count < total_count:
            sys.exit(1)


if __name__ == "__main__":
    main()
