import os
import shutil

# ベースディレクトリを相対パスで指定（スクリプト実行場所からの相対）
# または、PowerShellでの文字化けを回避するため、カレントディレクトリを使用
base_dir = os.getcwd()

# 作成するフォルダ構造の定義
folders_to_create = {
    "BabyDoll": [
        "00_設定資料",
        "01_陽菜",
        "02_沙耶",
        "03_凛",
        "04_莉愛",
        "05_明日香",
        "99_番外編"
    ],
    "水原愛衣": [],
    "桜井みお": [],
    "短編_その他": []
}

def create_folders():
    print(f"Base Directory: {base_dir}")
    
    for main_folder, sub_folders in folders_to_create.items():
        main_path = os.path.join(base_dir, main_folder)
        if not os.path.exists(main_path):
            os.makedirs(main_path)
            print(f"Created: {main_path}")
        else:
            print(f"Exists: {main_path}")
            
        for sub_folder in sub_folders:
            sub_path = os.path.join(main_path, sub_folder)
            if not os.path.exists(sub_path):
                os.makedirs(sub_path)
                print(f"Created: {sub_path}")
            else:
                print(f"Exists: {sub_path}")

if __name__ == "__main__":
    create_folders()
