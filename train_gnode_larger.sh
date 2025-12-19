# 选择 GPU
export CUDA_VISIBLE_DEVICES=1

# 初始化 conda
eval "$(/Share/data/liuxp/anaconda3/bin/conda shell.bash hook)"
conda activate py310-sthn

# 禁用 wandb
export WANDB_MODE=offline

# 限制 NumPy/PyTorch 底层运算最多只用 4 个核
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export NUMEXPR_NUM_THREADS=4

# ===== 实验参数 =====
DATASET=satellite_0_thermalmapping_135_train
D_C=512

echo "Running with: DATASET=$DATASET D_C=$D_C"

# ===== 运行 =====
python3 ./local_pipeline/train_4cor.py \
  --dataset_name ${DATASET} \
  --val_positive_dist_threshold ${D_C} \
  --val_freq 2000 \
  --database_size 1536 --num_steps 300000 --corr_level 4 --num_workers 16 \
  1> train_larger_${D_C}.out \
  2> >(tee train_larger_${D_C}.err >&2)