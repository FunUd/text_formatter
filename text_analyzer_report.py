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
    lx.data.ExampleData(
        text=textwrap.dedent("""
                                作成日: 2024-06-15
                                最終更新日: 2024-06-20
                                山田太郎
                                オートメーション機器市場の概要
        """),
        extractions=[
            lx.data.Extraction(
                extraction_class="レポート情報",
                extraction_text="作成日: 2024-06-15",
                attributes={
                    "creation_date": "2024-06-15",
                    "last_updated_date": "2024-06-20",
                    "author": "山田太郎",
                    "title": "オートメーション機器市場の概要",
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
                extraction_text="市場はやや寡占的で、上位5社が世界シェアの約45～60%を占めています",
                attributes={
                    "company": "上位5社",
                    "rate": "約45～60%",
                    "application": "N/A",
                    "year": "N/A",
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
                extraction_class="ニーズ",
                extraction_text="創薬・バイオ研究分野（ドラッグディスカバリー、ゲノミクス、プロテオミクスなど）や\n臨床診断（臨床化学分析や遺伝子検査）における自動化ニーズが高まっています",
                attributes={
                    "application": "創薬・バイオ研究分野",
                    "needs": "自動化ニーズ",
                    "trends": "高まっている",
                }
            ),
            lx.data.Extraction(
                extraction_class="ニーズ",
                extraction_text="創薬・バイオ研究分野（ドラッグディスカバリー、ゲノミクス、プロテオミクスなど）や\n臨床診断（臨床化学分析や遺伝子検査）における自動化ニーズが高まっています",
                attributes={
                    "application": "臨床診断",
                    "needs": "自動化ニーズ",
                    "trends": "高まっている",
                }
            ),
            lx.data.Extraction(
                extraction_class="シェア",
                extraction_text="特に臨床診断分野は2024年に市場シェア約27%を占め、",
                attributes={
                    "company": "上位5社",
                    "rate": "約27%",
                    "application": "臨床診断分野",
                    "year": "2024年",
                }
            ),
            lx.data.Extraction(
                extraction_class="ニーズ",
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
                extraction_class="市場規模",
                extraction_text="市場規模は2024年に約500億円、前年比10%増加。",
                attributes={"年": "2024年", "規模": "約500億円", "成長率": "前年比10%増加"}
            ),
            lx.data.Extraction(
                extraction_class="企業",
                extraction_text="競合主要企業はA社、B社、C社で、A社のシェアが約35%。",
                attributes={"企業名": "A社、B社、C社", "シェア": "A社約35%","関係": "競合"}
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
                extraction_class="製品情報",
                extraction_text="スマートライトX100(SL-X100)を新規発売しました。\n販売価格は12,000円（税込）です。\nX100は、音声操作に対応しており、消費電力10W、省エネモードを搭載する",
                attributes={
                    "製品名": "スマートライトX100",
                    "モデル名": "SL-X100",
                    "価格": "12,000円（税込）",
                    "特徴": "音声操作対応、消費電力10W、省エネモード搭載",
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