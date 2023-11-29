# CIL-DTHE-Reader

## Installation

### Use on a GNU/Linux personal computer

1. Download [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/):
    ```bash
    mkdir -p ~/miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    rm -rf ~/miniconda3/miniconda.sh
    ```
2. Initialise the Conda environment:
    - For Bourne shell (sh) or Bourne Again Shell (bash), use:
    ```bash
    ~/miniconda3/bin/conda init bash
    ```
    - For the Z shell (zsh), use:
    ```bash
    ~/miniconda3/bin/conda init zsh
    ```
3. Close the terminal then open a new terminal.
4. Update Conda:
```bash
conda update -n base conda
```
5. Use libmamba as a Conda solver (so muuuuuuch faster):
```bash
conda install -n base conda-libmamba-solver
conda config --set solver libmamba
```

### Use on a Supercomputer

This procedure has been tested on SCARF and Hawk, STFC and Wales' supercomputers respectively.

1. Log on one of the supercomputer's login hosts.
2. Download [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/):
    ```bash
    mkdir -p ~/miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    rm -rf ~/miniconda3/miniconda.sh
    ```
3. Initialise the Conda environment:
    - For Bourne shell (sh) or Bourne Again Shell (bash), use:
    ```bash
    ~/miniconda3/bin/conda init bash
    ```
    - For the Z shell (zsh), use:
    ```bash
    ~/miniconda3/bin/conda init zsh
    ```
4. Log out then log back in.
5. Update Conda:
```bash
conda update -n base conda
```
6. Use libmamba as a Conda solver (so muuuuuuch faster):
```bash
conda install -n base conda-libmamba-solver
conda config --set solver libmamba
```

### For any computer

1. Regardless of the operating system and type of computers, you must download the code using Git:
```bash
git clone git@github.com:effepivi/CIL-DTHE-Reader.git
cd CIL-DTHE-Reader
```
2. Create the Conda environment that will use CIL, Tigre, Astra-toolkit and CUDA:
```bash
conda env create -f environment.yml 
```

## How to use

### Use on a Windows or GNU/Linux personal computer

1. Activate the Conda environment:
```bash
conda activate DTHE2CIL
```
2. Use the executable script:
```bash
./FDK.py PATH_TO/unireconstruction.xml WHERE_TO_SAVE_RECONSTRUCTION

