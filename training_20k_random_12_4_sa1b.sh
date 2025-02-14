n=${1:-8}
export SAM_JSON="/sam_dataset"
export SAM_DATASETS="/sam_dataset"
export DATASET="/datasets"
export WANDB_API_KEY=f773908953fc7bea7008ae1cf3701284de1a0682

python train_net.py --resume --num-gpus $n --config-file configs/semantic_sam_only_sa-1b_swinT_20k_random_12_1.yaml COCO.TEST.BATCH_SIZE_TOTAL=$n SAM.TEST.BATCH_SIZE_TOTAL=$n SAM.TRAIN.BATCH_SIZE_TOTAL=$n