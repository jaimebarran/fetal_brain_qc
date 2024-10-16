def main():
    import argparse
    from fetal_brain_qc.report import generate_report
    from fetal_brain_qc.utils import csv_to_list, print_title

    p = argparse.ArgumentParser()

    p.add_argument(
        "out_path",
        help="Path where the reports will be stored.",
    )

    p.add_argument(
        "bids_csv",
        help="Path where the bids config csv file is located.",
    )

    p.add_argument(
        "--sr",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Whether the reports to be generated are for SR data.",
    )

    p.add_argument(
        "--add-js",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Whether some javascript should be added to the report for interaction with the index file.",
    )

    args = p.parse_args()

    bids_list = csv_to_list(args.bids_csv)
    print_title("Generating reports")
    generate_report(
        bids_list,
        out_folder=args.out_path,
        boundary=30,
        boundary_tp=30,
        ncols_ip=6,
        n_slices_tp=6,
        every_n_tp=4,
        annotate=False,
        cmap="Greys_r",
        do_index=args.add_js,
        is_sr=args.sr,
    )
    """Inspired from MRIQC.
    imp:
        Path to the brain LR T2w image to be plotted
    maskp:
        Path to the brain mask associated with imp
    boundary:
        Boundary to be left around the image when cropping it.
    ncols_ip:
        Number of columns in the in-plane plot
    nslices_tp:
        Number of slices to be displayed in the through-plane views.
    every_n_tp:
        Separation between two slices in the through-plane views.
    annotate:
        Whether the plots should be annotated
    cmap:
        Colormap to be used
    """

    return 0


if __name__ == "__main__":
    main()
