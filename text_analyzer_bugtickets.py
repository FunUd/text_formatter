import langextract as lx
import textwrap
import os
from pathlib import Path
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# 1. Define the prompt and extraction rules
prompt = textwrap.dedent("""\
    以下の不具合チケットから、各項目の情報を抽出してください。
    抽出項目：
    - チケット番号：チケットの番号
    - チケット作成日：日付形式（YYYY-MM-DD）で記載された作成日
    - チケット最終更新日：日付形式（YYYY-MM-DD）で記載された最終更新日
    - タイトル：チケットのタイトル
    - 概要：問題の概要説明。
    - 不具合現象：発生している具体的な問題
    - 再現手順：問題を再現するための手順
    - 再現性：問題の再現確率や条件
    - 不具合現象の備考：現象に関する補足情報
    - 原因：問題が発生した原因
    - 修正方法：問題を修正する方法
    - 水平展開：類似の問題が発生する可能性がある箇所
    - 不具合修正の備考：修正に関する補足情報

    項目が存在しない場合は、空文字列を返してください。
    各項目は必ず一度のみしか出現しません。同じ項目が2つ以上出現することはありません。""")

# 2. Provide a high-quality example to guide the model
examples = [
    lx.data.ExampleData(
        text="""【不具合チケット】
チケット番号: #12345
作成日: 2025-09-10
最終更新日: 2025-09-12
タイトル: ログイン時のパスワードエラー表示不具合

■ 概要
ログイン画面で正しいパスワードを入力しても「無効なパスワード」エラーが表示される問題。

■ 不具合現象
- 正しいユーザーIDとパスワードを入力してもログインできない
- エラーメッセージ「無効なパスワードです。もう一度お試しください。」が表示される
- パスワードリセット後も同様の現象が発生

■ 再現手順
1. ログイン画面を表示する
2. 有効なユーザーIDを入力する
3. 正しいパスワードを入力する
4. ログインボタンをクリックする

■ 再現性
100%再現

■ 不具合現象の備考
- 特定のブラウザに依存せず発生
- モバイルアプリでは発生せず、Web版のみで発生

■ 原因
パスワードのハッシュ化処理で特殊文字が正しく処理されていないことが原因。
具体的には、パスワードに含まれる「@」記号の処理に不具合があった。

■ 修正方法
1. パスワードのバリデーション処理を修正
2. 特殊文字を含むパスワードのハッシュ化処理を改善

■ 水平展開
- 同様のログイン処理を行っている他の画面も確認が必要
- パスワードリセット機能も同様の不具合の可能性あり

■ 不具合修正の備考
- 修正後、パスワードのリセットをユーザーに案内する必要あり
- セキュリティ観点から、パスワードの取り扱いに関するドキュメントの見直しを推奨""",
        extractions=[
            lx.data.Extraction(
                extraction_class="チケット番号",
                extraction_text="#12345"
            ),
            lx.data.Extraction(
                extraction_class="チケット作成日",
                extraction_text="2025-09-10"
            ),
            lx.data.Extraction(
                extraction_class="チケット最終更新日",
                extraction_text="2025-09-12"
            ),
            lx.data.Extraction(
                extraction_class="タイトル",
                extraction_text="ログイン時のパスワードエラー表示不具合"
            ),
            lx.data.Extraction(
                extraction_class="概要",
                extraction_text="ログイン画面で正しいパスワードを入力しても「無効なパスワード」エラーが表示される問題。"
            ),
            lx.data.Extraction(
                extraction_class="不具合現象",
                extraction_text="- 正しいユーザーIDとパスワードを入力してもログインできない\n- エラーメッセージ「無効なパスワードです。もう一度お試しください。」が表示される\n- パスワードリセット後も同様の現象が発生"
            ),
            lx.data.Extraction(
                extraction_class="再現手順",
                extraction_text="1. ログイン画面を表示する\n2. 有効なユーザーIDを入力する\n3. 正しいパスワードを入力する\n4. ログインボタンをクリックする"
            ),
            lx.data.Extraction(
                extraction_class="再現性",
                extraction_text="100%再現"
            ),
            lx.data.Extraction(
                extraction_class="不具合現象の備考",
                extraction_text="- 特定のブラウザに依存せず発生\n- モバイルアプリでは発生せず、Web版のみで発生"
            ),
            lx.data.Extraction(
                extraction_class="原因",
                extraction_text="パスワードのハッシュ化処理で特殊文字が正しく処理されていないことが原因。\n具体的には、パスワードに含まれる「@」記号の処理に不具合があった。"
            ),
            lx.data.Extraction(
                extraction_class="修正方法",
                extraction_text="1. パスワードのバリデーション処理を修正\n2. 特殊文字を含むパスワードのハッシュ化処理を改善"
            ),
            lx.data.Extraction(
                extraction_class="水平展開",
                extraction_text="- 同様のログイン処理を行っている他の画面も確認が必要\n- パスワードリセット機能も同様の不具合の可能性あり"
            ),
            lx.data.Extraction(
                extraction_class="不具合修正の備考",
                extraction_text="- 修正後、パスワードのリセットをユーザーに案内する必要あり\n- セキュリティ観点から、パスワードの取り扱いに関するドキュメントの見直しを推奨"
            )
        ]
    )
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
    
    for md_file in md_files:
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