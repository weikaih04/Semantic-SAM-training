n=${1:-8}
stage1_iter=${2:-10000}
stage2_iter=${3:-10000}

echo "Number of GPUs: $n"
echo "Stage 1 Iterations: $stage1_iter"
echo "Stage 2 Iterations: $stage2_iter"

python image_list_preprocess.py --base_path /tmp_dataset/meta_sa/sa_000000 \
                                --default_path /tmp_dataset/meta_sa/sa_000000 \
                                --output_file image_list.da

python image_list_preprocess.py --base_path /sam_dataset/meta_sa/sa_000000 \
                                --default_path /sam_dataset/meta_sa/sa_000000 \
                                --output_file image_list.da

export SAM_JSON="/tmp_dataset"
export SAM_DATASETS="/tmp_dataset"
export DATASET="/datasets"
export WANDB_API_KEY=f773908953fc7bea7008ae1cf3701284de1a0682
python train_net.py --resume --num-gpus $n --config-file configs/two_stages/stage1_12_3.yaml COCO.TEST.BATCH_SIZE_TOTAL=$n SAM.TEST.BATCH_SIZE_TOTAL=$n SAM.TRAIN.BATCH_SIZE_TOTAL=$n SOLVER.MAX_ITER=$stage1_iter
export SAM_JSON="/sam_dataset"
export SAM_DATASETS="/sam_dataset"
python train_net.py --resume --num-gpus $n --config-file configs/two_stages/stage2_12_3.yaml MODEL.WEIGHT="/output/model_final.pth" COCO.TEST.BATCH_SIZE_TOTAL=$n SAM.TEST.BATCH_SIZE_TOTAL=$n SAM.TRAIN.BATCH_SIZE_TOTAL=$n SOLVER.MAX_ITER=$stage2_iter