# 选择 GPU（例如 0 号 GPU）
export CUDA_VISIBLE_DEVICES=1

# 初始化 conda
eval "$(/Share/data/liuxp/anaconda3/bin/conda shell.bash hook)"
conda activate py310-sthn

# 禁用 wandb
export WANDB_MODE=offline

# ===== 实验参数 =====
DATASET=satellite_0_thermalmapping_135
D_C=128

echo "PID=$!"
echo "Running with: DATASET=$DATASET D_C=$D_C"

# ===== 运行 =====
python3 ./local_pipeline/train_4cor.py \
  --dataset_name ${DATASET} \
  --val_positive_dist_threshold ${D_C} \
  --val_freq 2000 \
  1> train_${D_C}.out \
  2> >(tee train_${D_C}.err >&2)