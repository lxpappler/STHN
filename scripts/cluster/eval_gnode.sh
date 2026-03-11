# 选择 GPU
export CUDA_VISIBLE_DEVICES=5

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
MODEL=logs/local_he/20251229_024813_gnode_larger_512_mini_32

# 诊断参数
DIAG_BATCHES=200
DIAG_MAP_BATCHES=8

echo "Running with: DATASET=$DATASET D_C=$D_C MODEL=$MODEL"

# ===== 运行（带性能诊断）=====
python3 ./local_pipeline/myevaluate.py \
    --dataset_name ${DATASET} \
    --eval_model $MODEL/STHN.pth \
    --val_positive_dist_threshold ${D_C} \
    --lev0 --arch IHN --database_size 1536 --corr_level 4 \
    --test \
    --diagnose_corr \
    --diag_batches ${DIAG_BATCHES} \
    --diag_save_map_batches ${DIAG_MAP_BATCHES} \
    1> eval.out \
    2> >(tee eval.err >&2)
