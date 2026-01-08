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
B_S=16
RUN_NAME=minitrain_bs16_vis_all_aug

echo "Running with: DATASET=$DATASET D_C=$D_C B_S=$B_S RUN_NAME=$RUN_NAME"

# ===== 运行 =====
python3 -u ./local_pipeline/train_4cor.py \
  --dataset_name ${DATASET} \
  --val_positive_dist_threshold ${D_C} \
  --batch_size ${B_S} \
  --num_steps 10000 --val_freq 1000 --lr 1e-4 \
  --database_size 1536 --corr_level 4 \
  --run_name ${RUN_NAME} \
  --vis_all \
  --augment img --perspective_max 16 --rotate_max 0.523599 --resize_max 0.3 \
  1> ${RUN_NAME}.out \
  2> >(tee ${RUN_NAME}.err >&2)