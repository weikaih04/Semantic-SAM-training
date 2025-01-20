# Variables for dataset paths
tmp_dataset=${1:-"/tmp_dataset"}
sam_dataset=${2:-"/sam_dataset"}
num_tmp_samples=${3:-100000}
num_sam_samples=${4:-100000}
n=${5:-8}
stage1_iter=${6:-10000}

echo "Number of GPUs: $n"
echo "Stage 1 Iterations: $stage1_iter"

python mix_data.py --folder1 /tmp_dataset/meta_sa/sa_000000 \
                   --folder2 /sam_dataset/meta_sa/sa_000000 \
                   --num_from_folder1 $num_tmp_samples \
                   --num_from_folder2 $num_sam_samples \
                   --output_folder /final_dataset/meta_sa/sa_000000


# Preprocessing for tmp_dataset
python image_list_preprocess.py --base_path /final_dataset/meta_sa/sa_000000 \
                                --default_path /final_dataset/meta_sa/sa_000000 \
                                --output_file image_list.da


# Setting environment variables
export SAM_JSON=/final_dataset/
export SAM_DATASETS=/final_dataset/
export DATASET="/datasets"
export WANDB_API_KEY=f773908953fc7bea7008ae1cf3701284de1a0682

# Stage 1 training
python train_net.py --resume --num-gpus $n --config-file configs/two_stages/stage1_12_3.yaml \
                    COCO.TEST.BATCH_SIZE_TOTAL=$n SAM.TEST.BATCH_SIZE_TOTAL=$n \
                    SAM.TRAIN.BATCH_SIZE_TOTAL=$n SOLVER.MAX_ITER=$stage1_iter