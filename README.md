# dtm_tools
Temporary tools to help with comparing decision tree modularized/unmodularized for tedana.

# How to set up
Instructions assume git repositories will be stored in `~/repositories`, and data will be stored in `~/tedana_testing`.
You will need to modify paths if your setup does not accomodate this.

Clone the tedana repository and add my fork as a remote (see [here](https://github.com/jbteves/tedana)) via

```
# if this path does not exist, make it
mkdir ~/repositories
cd ~/repositories
git clone https://github.com/ME-ICA/tedana.git
cd tedana
git remote add jbteves https://github.com/jbteves/tedana.git
git fetch jbteves JT_DTM
```

Install it into your current environment (you may want a different one than the one you have activated!)

```
cd ~/repositories/tedana
pip install -e .
```

Get this tool by running
```
cd ~/repositories
git clone https://github.com/jbteves/dtm_tools.git
```

# How to Use

First, enter the repository for tedana.
```
cd ~/repositories/tedana
```

Change to a branch you'd like to test (most likely main) via

```
git checkout main
```

and then run tedana on a test data set, somewhere other than the repository, for example

```
cd ~/tedana_testing
```

and consider putting your data in a directory called `test_data`, like this:

```
mkdir test_data
cp DATA_FILES test_data/
```

And then run main using a tedana call like this:

```
tedana \
    -d DATA_FILES \
    -e ECHO_TIMES \
    --out-dir main_tedana_results
```

Then, re-enter the repository and change to the modularized branch via

```
cd ~/repositories/tedana
git checkout jbteves/JT_DTM
```

and then run tedana on a test data set.
Use the existing mixing matrix (`main_tedana_results/desc-ICA_mixing.tsv`) with the `--mix` option in order to guarantee the same ICA components and save time.
Use an output directory named `dtm_tedana_results`.
The call should look something like

```
tedana \
    -d DATA_FILES \
    -e ECHO_TIMES \
    --out-dir dtm_tedana_results \
    --mix main_tedana_results/desc-ICA_mixing.tsv
```

After this completes, you can use the dtm tool via

```
python ~/repositories/dtm_tools/dtm_tool.py main_tedana_results/desc-tedana_metrics.tsv dtm_tedana_results/desc-tedana_metrics.tsv
```

For more options see

```
python ~/repositories/dtm_tools/dtm_tool.py -h
```
