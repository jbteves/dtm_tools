"""Tools for comparing output component table results"""

from argparse import ArgumentParser
import pandas as pd


def get_table_type(table: pd.DataFrame) -> str:
    """Get the table type from the supplied table.
    
    table: the table to check the type of.

    The type should be one of:
    - kundu-main
    - kundu-dtm
    - minimal-dtm
    """
    if "tags" not in table.columns:
        return "kundu-main"
    else:
        has_low_variance = np.any(
            ["Low variance" in tag_list for tag_list in table["tags"]]
        )
        if has_low_variance:
            return "kundu-dtm"
        else:
            return "minimal-dtm"



def get_classification(row: pd.Series) -> str:
    """Get the classification of a row/component.

    row: the row to get the classification of.

    Returns one of ("A", "I", "R").
    """
    if row["classification"] == "rejected":
        return "R"
    elif row["classification"] == "ignored":
        return "I"
    elif row["classification"] == "accepted":
        # tags indicate ignored for kundu DTM
        if "tags" in row and (
            "Low variance" in row["tags"] or
            "Accept borderline" in row["tags"] or 
            "No provisional accept" in row["tags"]
        ):
            return "I"
        else:
            return "A"


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

    ltable = pd.read_csv(lfile)
    rtable = pd.read_csv(rfile)

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
    elif args.verbose:
        print(f"CHANGE\tNC\tVAREX\tCOMPS")
    else:
        print(f"CHANGE\tNC\tVAREX")

    for k, v in change_summary.items():
        n = len(v['components'])
        vx = v['varex']
        summary = f"{k}\t{n:03}\t{vx:2.4f}"
        if args.verbose:
            allcomps = v['components']
            summary += f"\t{allcomps}"
        print(summary)



if __name__ == '__main__':
    main()
