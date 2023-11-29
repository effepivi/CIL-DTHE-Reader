#!/usr/bin/bash

#SBATCH --job-name=recons     # Job name
#SBATCH --output recons-%j.out     # Job name
#SBATCH --error  recons-%j.err     # Job name
#
# Number of tasks per node
#SBATCH --ntasks-per-node=1
#
# Number of cores per task
#SBATCH --cpus-per-task=30
#
# Use one node
#SBATCH --nodes=1
# Use GPU
#SBATCH --partition=gpu
#SBATCH --gres=gpu:3
#
# Runtime of this jobs is less than 5 minutes.
#SBATCH --time=00:05:00
#SBATCH --mem=5G

module load CUDA/11.5.0

export MPLBACKEND=pdf

source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate DTHE2CIL

# Edit the path below
DATA_PATH=$HOME/CIL-DTHE-Reader/data/

./FDK.py \
    --backend tigre \
    --save_geometry $DATA_PATH/geometry.pdf \
    $DATA_PATH/unireconstruction.xml \
    $DATA_PATH/CIL-recons-tigre

# Tested, it works, but slower than Tigre
./FDK.py \
    --backend astra \
    $DATA_PATH/unireconstruction.xml \
    $DATA_PATH/CIL-recons-astra

