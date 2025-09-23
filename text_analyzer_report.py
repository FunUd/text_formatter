import langextract as lx
import textwrap
import os
from pathlib import Path
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# 1. Define the prompt and extraction rules
prompt = textwrap.dedent("""\
                            以下のレポートから、情報を抽出してください。

                            重要：extraction_textには入力からの正確なテキストを使用してください。

                            以下の形式で出力してください:
                            "extractions": [
                                { ... }
                            ]

                            重要：'extractions'キーは出力に必ず含めてください。"""
                        )

# 2. Provide a high-quality example to guide the model
examples = [
    # 市場分析レポートの例
    lx.data.ExampleData(
        text=textwrap.dedent("""
                            市場動向分析レポート：AI・機械学習市場 2025年第2四半期
                            
                            市場規模：
                            - グローバル市場：2,850億米ドル（前年比+18%）
                            - 国内市場：3.2兆円（前年比+15%）
                            
                            成長率予測：
                            - 2025年：+18%
                            - 2026年：+22%
                            - 2027年：+25%
                            
                            主要プレイヤー：
                            1. TechCorp（市場シェア28%）
                            2. AIソリューションズ（市場シェア22%）
                            3. DataMind（市場シェア15%）
                            
                            成長要因：
                            - デジタルトランスフォーメーションの加速
                            - 自動化需要の増加
                            - クラウドAIの普及
                            
                            リスク要因：
                            - 人材不足
                            - データプライバシー規制
                            - 技術標準化の遅れ
                        """),
        extractions=[
            lx.data.Extraction(
                extraction_class="market_size",
                extraction_text="グローバル市場：2,850億米ドル（前年比+18%）",
                attributes={
                    "market_type": "グローバル",
                    "size": "2,850億米ドル",
                    "growth_rate": "+18%",
                    "year": "2025",
                    "currency": "米ドル"
                }
            ),
            lx.data.Extraction(
                extraction_class="market_size",
                extraction_text="国内市場：3.2兆円（前年比+15%）",
                attributes={
                    "market_type": "国内",
                    "size": "3.2兆円",
                    "growth_rate": "+15%",
                    "year": "2025",
                    "currency": "円"
                }
            ),
            lx.data.Extraction(
                extraction_class="growth_forecast",
                extraction_text="2025年：+18%\n2026年：+22%\n2027年：+25%",
                attributes={
                    "forecasts": [
                        {"year": "2025", "rate": "+18%"},
                        {"year": "2026", "rate": "+22%"},
                        {"year": "2027", "rate": "+25%"}
                    ]
                }
            ),
            lx.data.Extraction(
                extraction_class="market_player",
                extraction_text="1. TechCorp（市場シェア28%）",
                attributes={
                    "company_name": "TechCorp",
                    "market_share": "28%",
                    "rank": 1
                }
            ),
            lx.data.Extraction(
                extraction_class="market_player",
                extraction_text="2. AIソリューションズ（市場シェア22%）",
                attributes={
                    "company_name": "AIソリューションズ",
                    "market_share": "22%",
                    "rank": 2
                }
            ),
            lx.data.Extraction(
                extraction_class="market_player",
                extraction_text="3. DataMind（市場シェア15%）",
                attributes={
                    "company_name": "DataMind",
                    "market_share": "15%",
                    "rank": 3
                }
            ),
            lx.data.Extraction(
                extraction_class="factors",
                extraction_text="成長要因：\n- デジタルトランスフォーメーションの加速\n- 自動化需要の増加\n- クラウドAIの普及",
                attributes={
                    "factor_type": "growth",
                    "factors": [
                        "デジタルトランスフォーメーションの加速",
                        "自動化需要の増加",
                        "クラウドAIの普及"
                    ]
                }
            ),
            lx.data.Extraction(
                extraction_class="factors",
                extraction_text="リスク要因：\n- 人材不足\n- データプライバシー規制\n- 技術標準化の遅れ",
                attributes={
                    "factor_type": "risk",
                    "factors": [
                        "人材不足",
                        "データプライバシー規制",
                        "技術標準化の遅れ"
                    ]
                }
            )
        ]
    ),
    lx.data.ExampleData(
        text=textwrap.dedent("""
                                作成日: 2024-06-15
                                最終更新日: 2024-06-20
                                山田太郎
                                オートメーション機器市場の概要
        """),
        extractions=[
            lx.data.Extraction(
                extraction_class="date",
                extraction_text="作成日: 2024-06-15",
                attributes={
                    "category": "作成日",
                    "date": "2024-06-15",
                    "target": "レポート"
                }
            ),
            lx.data.Extraction(
                extraction_class="date",
                extraction_text="最終更新日: 2024-06-20",
                attributes={
                    "category": "最終更新日",
                    "date": "2024-06-20",
                    "target": "レポート"
                }
            ),
            lx.data.Extraction(
                extraction_class="human name",
                extraction_text="作成者: 山田太郎",
                attributes={
                    "category": "作成者",
                    "name": "山田太郎",
                }
            ),
            lx.data.Extraction(
                extraction_class="title",
                extraction_text="オートメーション機器市場の概要",
                attributes={
                    "category": "report title",
                    "content": "オートメーション機器市場の概要",
                }
            ),
        ]
    ),
    lx.data.ExampleData(
        text=textwrap.dedent("""
            市場シェア（企業別・製品セグメント別）
            市場はやや寡占的で、上位5社が世界シェアの約45～60%を占めています
        """),
        extractions=[
            lx.data.Extraction(
                extraction_class="シェア",
                extraction_text="上位5社が世界シェアの約45～60%を占めています",
                attributes={
                    "company": "上位5社",
                    "rate": "約45～60%",
                    "application": "N/A",
                    "year": "N/A",
                }
            ),
            lx.data.Extraction(
                extraction_class="numeric_value",
                extraction_text="上位5社が世界シェアの約45～60%を占めています",
                attributes={
                    "value": "約45～60%",
                    "unit": "%",
                    "context": "世界シェア",
                    "year": "N/A",
                    "target": "上位5社"
                }
            ),
        ]
    ),
    lx.data.ExampleData(
        text=textwrap.dedent("""
            主要アプリケーション別では、創薬・バイオ研究分野（ドラッグディスカバリー、ゲノミクス、プロテオミクスなど）や
            臨床診断（臨床化学分析や遺伝子検査）における自動化ニーズが高まっています
            。特に臨床診断分野は2024年に市場シェア約27%を占め、今後も高齢化や慢性疾患増加に伴い
            検査量増に対応した自動化需要が見込まれます
        """),
        extractions=[
            lx.data.Extraction(
                extraction_class="needs",
                extraction_text="創薬・バイオ研究分野（ドラッグディスカバリー、ゲノミクス、プロテオミクスなど）や\n臨床診断（臨床化学分析や遺伝子検査）における自動化ニーズが高まっています",
                attributes={
                    "application": "創薬・バイオ研究分野",
                    "needs": "自動化ニーズ",
                    "trends": "高まっている",
                }
            ),
            lx.data.Extraction(
                extraction_class="needs",
                extraction_text="創薬・バイオ研究分野（ドラッグディスカバリー、ゲノミクス、プロテオミクスなど）や\n臨床診断（臨床化学分析や遺伝子検査）における自動化ニーズが高まっています",
                attributes={
                    "application": "臨床診断",
                    "needs": "自動化ニーズ",
                    "trends": "高まっている",
                }
            ),
            lx.data.Extraction(
                extraction_class="numeric_value",
                extraction_text="特に臨床診断分野は2024年に市場シェア約27%を占め、",
                attributes={
                    "value": "約27%",
                    "unit": "%",
                    "context": "市場シェア",
                    "year": "2024年",
                    "target": "臨床診断分野"
                }
            ),
            lx.data.Extraction(
                extraction_class="needs",
                extraction_text="特に臨床診断分野は2024年に市場シェア約27%を占め、今後も高齢化や慢性疾患増加に伴い\n検査量増に対応した自動化需要が見込まれます",
                attributes={
                    "application": "臨床診断分野",
                    "needs": "今後も高齢化や慢性疾患増加に伴い\n検査量増に対応した自動化需要が見込まれます",
                    "trends": "自動化需要が見込まれます",
                }
            ),
        ]
    ),
    lx.data.ExampleData(
        text=textwrap.dedent("""
            市場規模は2024年に約500億円、前年比10%増加。
            競合主要企業はA社、B社、C社で、A社のシェアが約35%。
        """),
        extractions=[
            lx.data.Extraction(
                extraction_class="numeric_value",
                extraction_text="市場規模は2024年に約500億円",
                attributes={
                    "value": "500億円",
                    "unit": "円",
                    "context": "市場規模",
                    "year": "2024年",
                    "target": "N/A"
                }
            ),
            lx.data.Extraction(
                extraction_class="numeric_value",
                extraction_text="市場規競合主要企業はA社、B社、C社で、A社のシェアが約35%。",
                attributes={
                    "value": "約35%",
                    "unit": "%",
                    "context": "シェア",
                    "year": "2024年",
                    "target": "A社"
                }
            ),
        ]
    ),
    lx.data.ExampleData(
        text=textwrap.dedent("""
                            スマートライトX100(SL-X100)を新規発売しました。
                            販売価格は12,000円（税込）です。
                            X100は、音声操作に対応しており、消費電力10W、省エネモードを搭載するなど、
                            利便性とエコを追求した製品です。
        """),
        extractions=[
            lx.data.Extraction(
                extraction_class="name",
                extraction_text="スマートライトX100(SL-X100)を新規発売しました。",
                attributes={
                    "product_name": "スマートライトX100",
                    "model_name": "SL-X100",
                    "category": "スマートホーム",
                    "subcategory": "照明",
                    "version": "N/A"
                }
            ),
            lx.data.Extraction(
                extraction_class="price",
                extraction_text="販売価格は12,000円（税込）です。",
                attributes={
                    "base_price": "12,000円（税込）",
                    "subscription": "N/A",
                    "additional_fees": "N/A",
                    "price_type": "one-time"
                }
            ),
            lx.data.Extraction(
                extraction_class="features",
                extraction_text="音声操作に対応しており、消費電力10W、省エネモードを搭載する",
                attributes={
                    "core_features": [
                        "音声操作対応",
                        "省エネモード搭載"
                    ],
                    "premium_features": "N/A",
                    "performance": "消費電力10W"
                }
            ),
            lx.data.Extraction(
                extraction_class="specifications",
                extraction_text="音声操作に対応しており、消費電力10W、省エネモードを搭載する",
                attributes={
                    "technical_specs": {
                        "power": "10W"
                    },
                    "connectivity": "N/A",
                    "standards": "N/A",
                    "dimensions": "N/A"
                }
            ),
        ]
    ),
    lx.data.ExampleData(
        text=textwrap.dedent("""
                            AI画像処理ソフトウェア「ImageAI Pro Version 2.5」をリリースしました。
                            ライセンス料金は、スタンダードプランが月額4,980円（税込）、
                            エンタープライズプランが月額29,800円（税込）となります。
                            
                            主な機能：
                            - AIによる自動画像補正
                            - バッチ処理対応（最大1000枚/分）
                            - クラウドストレージ連携
                            - API提供（エンタープライズプランのみ）
        """),
        extractions=[
            lx.data.Extraction(
                extraction_class="name",
                extraction_text="AI画像処理ソフトウェア「ImageAI Pro Version 2.5」をリリースしました。",
                attributes={
                    "product_name": "ImageAI Pro",
                    "model_name": "N/A",
                    "category": "ソフトウェア",
                    "subcategory": "画像処理",
                    "version": "2.5"
                }
            ),
            lx.data.Extraction(
                extraction_class="price",
                extraction_text="ライセンス料金は、スタンダードプランが月額4,980円（税込）、\nエンタープライズプランが月額29,800円（税込）となります。",
                attributes={
                    "base_price": "月額4,980円（税込）",
                    "subscription": "月額",
                    "additional_fees": {
                        "enterprise": "月額29,800円（税込）"
                    },
                    "price_type": "subscription"
                }
            ),
            lx.data.Extraction(
                extraction_class="features",
                extraction_text="主な機能：\n- AIによる自動画像補正\n- バッチ処理対応（最大1000枚/分）\n- クラウドストレージ連携\n- API提供（エンタープライズプランのみ）",
                attributes={
                    "core_features": [
                        "AIによる自動画像補正",
                        "バッチ処理対応",
                        "クラウドストレージ連携"
                    ],
                    "premium_features": [
                        "API提供"
                    ],
                    "performance": "最大1000枚/分"
                }
            ),
            lx.data.Extraction(
                extraction_class="specifications",
                extraction_text="バッチ処理対応（最大1000枚/分）",
                attributes={
                    "technical_specs": {
                        "processing_speed": "1000枚/分"
                    },
                    "connectivity": "クラウドストレージ連携",
                    "standards": "N/A",
                    "dimensions": "N/A"
                }
            ),
        ]
    ),
    # IoT製品の例
    lx.data.ExampleData(
        text=textwrap.dedent("""
                            スマートホームハブ「HomeConnect Pro (HC-P200)」発売開始のお知らせ
                            
                            本体価格：35,800円（税込）
                            ※クラウドサービス利用料は1年間無料、2年目以降は年額3,600円（税込）
                            
                            特徴：
                            - Wi-Fi 6対応
                            - Matter規格準拠
                            - 最大200台のデバイス接続
                            - AI搭載省エネ制御
                            - バッテリーバックアップ（4時間）
                            
                            対応規格：
                            Zigbee 3.0、Bluetooth 5.2、Thread
        """),
        extractions=[
            lx.data.Extraction(
                extraction_class="name",
                extraction_text="スマートホームハブ「HomeConnect Pro (HC-P200)」発売開始のお知らせ",
                attributes={
                    "product_name": "HomeConnect Pro",
                    "model_name": "HC-P200",
                    "category": "スマートホーム",
                    "subcategory": "ハブ",
                    "version": "N/A"
                }
            ),
            lx.data.Extraction(
                extraction_class="price",
                extraction_text="本体価格：35,800円（税込）\n※クラウドサービス利用料は1年間無料、2年目以降は年額3,600円（税込）",
                attributes={
                    "base_price": "35,800円（税込）",
                    "subscription": "年額3,600円（税込）",
                    "additional_fees": "N/A",
                    "price_type": "hybrid"
                }
            ),
            lx.data.Extraction(
                extraction_class="features",
                extraction_text="特徴：\n- Wi-Fi 6対応\n- Matter規格準拠\n- 最大200台のデバイス接続\n- AI搭載省エネ制御\n- バッテリーバックアップ（4時間）",
                attributes={
                    "core_features": [
                        "AI搭載省エネ制御",
                        "バッテリーバックアップ",
                        "最大200台のデバイス接続"
                    ],
                    "premium_features": "N/A",
                    "performance": "バッテリー駆動4時間"
                }
            ),
            lx.data.Extraction(
                extraction_class="specifications",
                extraction_text="対応規格：\nZigbee 3.0、Bluetooth 5.2、Thread",
                attributes={
                    "technical_specs": {
                        "max_devices": "200台",
                        "backup_time": "4時間"
                    },
                    "connectivity": [
                        "Wi-Fi 6",
                        "Bluetooth 5.2"
                    ],
                    "standards": [
                        "Matter",
                        "Zigbee 3.0",
                        "Thread"
                    ],
                    "dimensions": "N/A"
                }
            ),
        ]
    ),
]

def get_model_config(use_local=True):
    """モデル設定を返す関数"""
    if use_local:
        return {
            'model_id': 'gemma:2b-instruct',
            'api_key': None  # ローカルモデルではAPI keyは不要
        }
    else:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError(
                "APIキーが設定されていません。.envファイルにGEMINI_API_KEYを設定してください。"
            )
        return {
            'model_id': 'gemini-2.5-flash',
            'api_key': api_key
        }

def debug_print(debug_mode, *args, **kwargs):
    """デバッグモードが有効な場合にのみメッセージを表示する"""
    if debug_mode:
        print(*args, **kwargs)

def process_text(text, output_prefix, output_dir, use_local=True, debug_mode=False):
    """Process a single text and save the results with the given prefix"""
    # Get model configuration
    model_config = get_model_config(use_local)
    
    try:
        debug_print(debug_mode, "\n=== Sending request to LLM ===")
        debug_print(debug_mode, f"Using model: {model_config.get('model_id', 'unknown')}")
        
        # Run the extraction
        result = lx.extract(
            text_or_documents=text,
            prompt_description=prompt,
            examples=examples,
            **model_config
        )
        
        # Print the raw response for debugging
        debug_print(debug_mode, "\n=== Raw LLM Response ===")
        debug_print(debug_mode, f"Response type: {type(result)}")
        debug_print(debug_mode, f"Response content: {result}")
        
        if debug_mode and isinstance(result, dict):
            debug_print(debug_mode, "\n=== Response Keys ===")
            debug_print(debug_mode, result.keys())
            
            if 'extractions' not in result:
                debug_print(debug_mode, "\n!!! WARNING: 'extractions' key not found in response !!!")
                if 'error' in result:
                    debug_print(debug_mode, f"Error from API: {result['error']}")
                    
    except Exception as e:
        print(f"\n!!! ERROR during extraction: {str(e)} !!!")
        import traceback
        traceback.print_exc()
        return  # Exit the function if there was an error

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create output filenames
    jsonl_file = output_dir / f"{output_prefix}_results.jsonl"
    html_file = output_dir / f"{output_prefix}_visualization.html"

    # Save the results to a JSONL file
    lx.io.save_annotated_documents([result], output_name=jsonl_file.name, output_dir=str(output_dir))

    # Generate the visualization from the file
    html_content = lx.visualize(str(jsonl_file))
    with open(html_file, "w", encoding='utf-8') as f:
        if hasattr(html_content, 'data'):
            f.write(html_content.data)  # For Jupyter/Colab
        else:
            f.write(html_content)
    
    print(f"Processed and saved results to {output_dir}/{output_prefix}_*")

def main():
    import argparse
    
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='不具合チケット情報抽出ツール')
    parser.add_argument('--online', action='store_true',
                      help='オンラインのLLM (Gemini-2.5)を使用する')
    parser.add_argument('--debug', action='store_true',
                      help='デバッグ情報を表示する')
    args = parser.parse_args()
    
    # Define directories
    input_dir = Path("input")
    output_dir = Path("out")
    
    # Create input directory if it doesn't exist
    input_dir.mkdir(exist_ok=True)
    
    # Process all markdown files in the input directory
    md_files = list(input_dir.glob("*.md"))
    
    if not md_files:
        print(f"No markdown files found in {input_dir}/. Please add some .md files to process.")
        return
    
    # モデルの種類を表示
    model_config = get_model_config(not args.online)
    print(f"Using model: {model_config['model_id']}")
    
    total_files = len(md_files)
    for index, md_file in enumerate(md_files, 1):
        print(f"\n📄 Processing file [{index}/{total_files}]: {md_file.name}")
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use the filename without extension as the output prefix
            output_prefix = md_file.stem
            process_text(content, output_prefix, output_dir, 
                       use_local=not args.online,
                       debug_mode=args.debug)
            
        except Exception as e:
            print(f"Error processing {md_file}: {str(e)}")

if __name__ == "__main__":
    main()