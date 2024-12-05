n=${1:-8}

export SAM_JSON="/tmp_dataset"
export SAM_DATASETS="/tmp_dataset"
export DATASET="/datasets"
export WANDB_API_KEY=f773908953fc7bea7008ae1cf3701284de1a0682
export SAM_JSON="/sam_dataset"
export SAM_DATASETS="/sam_dataset"
python train_net.py --resume --num-gpus $n --config-file configs/two_stages/stage1_12_3.yaml COCO.TEST.BATCH_SIZE_TOTAL=$n SAM.TEST.BATCH_SIZE_TOTAL=$n SAM.TRAIN.BATCH_SIZE_TOTAL=$n SOLVER.MAX_ITER=20000