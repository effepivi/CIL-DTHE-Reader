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
# Runtime of this jobs is less than 15 minutes.
#SBATCH --time=00:15:00
#SBATCH --mem=5G

module load CUDA/11.5.0

export MPLBACKEND=pdf

source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate DTHE2CIL

# Edit the path below
DATA_PATH=$HOME/CIL-DTHE-Reader/data/

# Fastest:
# Filtering: CIL
# Projector: Tigre
./FDK.py \
    --backend cil \
    --save_geometry $DATA_PATH/geometry.pdf \
    $DATA_PATH/unireconstruction.xml \
    $DATA_PATH/CIL-recons-cil

# Slower
# Filtering: Tigre
# Projector: Tigre
./FDK.py \
    --backend tigre \
    $DATA_PATH/unireconstruction.xml \
    $DATA_PATH/CIL-recons-tigre

# Slowest
# Filtering: Astra
# Projector: Astra
./FDK.py \
    --backend astra \
    $DATA_PATH/unireconstruction.xml \
    $DATA_PATH/CIL-recons-astra
