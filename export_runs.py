import os
import csv
import re

def align_experiments():
    wandb_dir = "wandb"
    log_dir = "./logs/local_he"
    output_file = "experiment_alignment.csv"

    # 获取所有 W&B 离线文件夹
    wandb_folders = sorted([d for d in os.listdir(wandb_dir) if d.startswith("offline-run")])
    # 获取所有本地 log 文件夹
    log_folders = sorted(os.listdir(log_dir))

    alignment_data = []

    for w_folder in wandb_folders:
        # 提取时间戳 (20251217_044105) 和 ID (tv0abxvt)
        parts = w_folder.split('-')
        if len(parts) < 4: continue
        
        raw_ts = parts[2]  # 20251217_044105
        run_id = parts[3]  # tv0abxvt
        
        # 转换为本地 log 的匹配模式: 2025-12-17_04-41
        # 忽略秒数，只匹配到分钟以处理 1 秒的系统延迟误差
        date_part = f"{raw_ts[:4]}-{raw_ts[4:6]}-{raw_ts[6:8]}"
        time_part = f"{raw_ts[9:11]}-{raw_ts[11:13]}"
        search_pattern = f"{date_part}_{time_part}"
        
        # 在本地 log 列表中寻找匹配
        match = [l for l in log_folders if search_pattern in l]
        matched_log = match[0] if match else "NOT_FOUND"

        alignment_data.append({
            "WandB_Run_ID": run_id,
            "WandB_Folder": w_folder,
            "Local_Log_Folder": matched_log,
            "Sync_Command": f"wandb sync wandb/{w_folder}"
        })

    # 写入 CSV
    keys = ["WandB_Run_ID", "WandB_Folder", "Local_Log_Folder", "Sync_Command"]
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(alignment_data)

    print(f"成功！对齐清单已保存至: {output_file}")
    print(f"共识别到 {len(alignment_data)} 条实验记录。")

if __name__ == "__main__":
    align_experiments()