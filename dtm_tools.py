"""Tools for comparing output component table results"""

from argparse import ArgumentParser
import pandas as pd
import numpy as np

TAG = 'classification_tags'
KUNDU_TAGS = ('Accept borderline', 'No provisional accept')
RATIONALE_TABLE = {
    'I001': 'Manual classification',
    'I002': 'Rho > Kappa',
    'I003': 'More significant voxels S0 vs. R2',
    'I004': 'S0 Dice > R2 Dice AND high varex',
    'I005': 'Noise F-value > Signal F-value AND high varex',
    'I006': 'No good components found',
    'I007': 'Mid-Kappa',
    'I008': 'Low variance',
    'I009': 'Mid-Kappa type A',
    'I010': 'Mid-Kappa type B',
    'I011': 'ign_add0',
    'I012': 'ign_add1',
    'N/A':  'N/A',
}

def get_table_type(table: pd.DataFrame) -> str:
    """Get the table type from the supplied table.
    
    table: the table to check the type of.

    The type should be one of:
    - kundu-main
    - kundu-dtm
    - minimal-dtm
    """
    if "classification_tags" not in table.columns:
        return "kundu-main"
    else:
        has_kundu_tag = False
        for tag_list in table[TAG]:
            for t in KUNDU_TAGS:
                if t in tag_list:
                    has_kundu_tag = True

        if has_kundu_tag:
            return "kundu-dtm"
        else:
            return "minimal-dtm"


def get_classification(row: pd.Series) -> str:
    """Get the classification of a row/component.

    row: the row to get the classification of.

    Returns one of ("A", "R").
    """
    if row["classification"] == "rejected":
        return "R"
    else:
        return "A"


def get_classification_verbose(row: pd.Series) -> str:
    """Get the verbose classification of a row/component.

    row: the row to get the classification of.

    Returns one of ("A", "R").
    """
    if row["classification"] == "rejected":
        return "R"
    elif row["classification"] == "accepted":
        return "A"
    elif row["classification"] == "ignored":
        return "I"


def main():
    parser = ArgumentParser(
        description='Prints the number of component classification changes.'
    )
    parser.add_argument(
        '--verbose', '-v',
        help='Verbose mode; prints all component IDs for each change type',
        required=False,
        action='store_true',
    )
    parser.add_argument('left', help='The left component table')
    parser.add_argument('right', help='The right component table')
    args = parser.parse_args()

    lfile = args.left
    rfile = args.right

    ltable = pd.read_csv(lfile, delimiter='\t')
    rtable = pd.read_csv(rfile, delimiter='\t')

    assert "classification" in ltable.columns
    assert "classification" in rtable.columns

    if len(ltable) != len(rtable):
        raise ValueError(
            f"{lfile} has {len(ltable)} components, but "
            f"{rfile} has {len(rtable)} components."
        )


    ltype = get_table_type(ltable)
    rtype = get_table_type(rtable)

    print(f"{lfile} is of type {ltype}")
    print(f"{rfile} is of type {rtype}")

    total_changes = 0
    change_summary = {}

    for (i, lrow), (_, rrow)  in zip(ltable.iterrows(), rtable.iterrows()):
        # iterate over rows
        lclass = get_classification(lrow)
        rclass = get_classification(rrow)
        # Use for debug
        # print(f"{lclass} -> {rclass}")
        if lclass != rclass:
            total_changes += 1
            change = f"{lclass} -> {rclass}"
            if change in change_summary.keys():
                vx = lrow['variance explained']
                change_summary[change]['components'].append(i)
                change_summary[change]['varex'] += vx
            else:
                change_summary[change] = {
                    'components' : [i],
                    'varex' : lrow['variance explained'],
                }

    if len(change_summary.keys()) == 0:
        print("No differences in classification")
    else:
        print(f"Change\tNumComponents\tVarex\tComponentIndices")

    for k, v in change_summary.items():
        n = len(v['components'])
        vx = v['varex']
        allcomps = v['components']
        summary = f"{k}\t{n:03}\t\t{vx:2.4f}\t{allcomps}"
        print(summary)

    if args.verbose:
        # Print information for each component
        comps = []
        for _, v in change_summary.items():
            for c in v['components']:
                comps.append(c)
        comps.sort()
        if 'dtm' in ltype:
            lcol = TAG
        else:
            lcol = 'rationale'
        if 'dtm' in rtype:
            rcol = TAG
        else:
            rcol = 'rationale'
        rtkeys = RATIONALE_TABLE.keys()
       
        VERB_SUMMARY = "Change"
        LCOMP_SUMMARY = "Left"
        RCOMP_SUMMARY = "Right"
        print(
                f"N  :\t{VERB_SUMMARY:8} {LCOMP_SUMMARY:20}{RCOMP_SUMMARY:20}\tVariance"
        )
        for c in comps:
            lcomp_verb_class = get_classification_verbose(ltable.iloc[c])
            rcomp_verb_class = get_classification_verbose(rtable.iloc[c])
            verbose_summary = lcomp_verb_class + '->' + rcomp_verb_class
            lcomp_val = ltable.iloc[c][lcol]
            rcomp_val = rtable.iloc[c][rcol]
            varex = ltable.iloc[c]["variance explained"]
            if lcomp_val in rtkeys:
                lcomp_val = RATIONALE_TABLE[lcomp_val]
            if rcomp_val in rtkeys:
                rcomp_val = RATIONALE_TABLE[rcomp_val]
            if str(lcomp_val) == "nan":
                lcomp_val = 'N/A'
            if str(rcomp_val) == "nan":
                rcomp_val = 'N/A'
            print(
                    f"{c:03}:\t{verbose_summary:8} {lcomp_val:20}{rcomp_val:20}\t{varex:<4.2}"
            )



if __name__ == '__main__':
    main()
