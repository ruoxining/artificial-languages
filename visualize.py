"""Visualize the perplexity scores."""
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def visualize(input_file: str):
    """Visualize the perplexity scores."""
    # read the csv file
    df = pd.read_csv(input_file)

    # average perplexity across divs
    avg_df = df.groupby(["grammar", "model"], as_index=False)["ppl-10-epochs"].mean()

    # drop empty grammars and make sure they're strings
    avg_df = avg_df[avg_df["grammar"] != ""]
    avg_df["grammar"] = avg_df["grammar"].astype(str)

    # get grammar list in the order they appear
    grammar_list = avg_df["grammar"].unique().tolist()

    # plot
    plt.figure(figsize=(15, 6))
    for model in avg_df["model"].unique():
        subset = avg_df[avg_df["model"] == model]
        plt.scatter(subset["grammar"], subset["ppl-10-epochs"], label=model)

    plt.xlabel("Grammar")
    plt.ylabel("Average Perplexity (over divs)")
    plt.xticks(ticks=range(len(grammar_list)), labels=grammar_list, rotation=90)
    plt.legend()
    plt.savefig("perplexity_plot.pdf")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize the perplexity scores.")
    parser.add_argument("-i", "--input_file", type=str, required=True,
        help="Path to input folder containing .out files")
    args = parser.parse_args()

    visualize(args.input_file)
