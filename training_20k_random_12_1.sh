export SAM_JSON="/tmp_dataset"
export DATASET="/datasets"
n=8
python train_net.py --resume --num-gpus $n --config-file configs/semantic_sam_only_sa-1b_swinT_my_model.yaml COCO.TEST.BATCH_SIZE_TOTAL=$n SAM.TEST.BATCH_SIZE_TOTAL=$n SAM.TRAIN.BATCH_SIZE_TOTAL=$n