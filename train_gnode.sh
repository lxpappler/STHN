# 选择 GPU（例如 0 号 GPU）
export CUDA_VISIBLE_DEVICES=1

# 初始化 conda
eval "$(/Share/data/liuxp/anaconda3/bin/conda shell.bash hook)"
conda activate py310-sthn

# 禁用 wandb
export WANDB_MODE=offline

# 运行训练脚本
python3 ./local_pipeline/train_4cor.py --dataset_name satellite_0_thermalmapping_135 2>train_ori.err | tee train_ori.out
