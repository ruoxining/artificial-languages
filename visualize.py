"""Visualize the perplexity scores."""
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns

def visualize(input_file: str, output_folder: str):
    """Visualize the perplexity scores."""
    # read the csv file
    df = pd.read_csv(input_file)
    
    # Drop empty columns and duplicates
    df = df.drop(['ppl-10-epochs', 'if_finished'], axis=1)
    df = df.drop_duplicates()
    
    # Convert final_ppl to numeric
    df['final_ppl'] = pd.to_numeric(df['final_ppl'])
    
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # Plot 1: Box plot of perplexity by grammar
    sns.boxplot(data=df, x='grammar', y='final_ppl', ax=ax1)
    ax1.set_xlabel("Grammar")
    ax1.set_ylabel("Perplexity")
    ax1.set_title("Distribution of Perplexity Scores by Grammar")
    ax1.tick_params(axis='x', rotation=90)
    
    # Plot 2: Scatter plot of perplexity by grammar
    sns.scatterplot(data=df, x='grammar', y='final_ppl', ax=ax2)
    ax2.set_xlabel("Grammar")
    ax2.set_ylabel("Perplexity")
    ax2.set_title("Perplexity Scores by Grammar")
    ax2.tick_params(axis='x', rotation=90)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, "perplexity_plot.pdf"))
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize the perplexity scores.")
    parser.add_argument("-i", "--input_file", type=str, required=True,
        help="Path to input CSV file")
    parser.add_argument("-o", "--output_folder", type=str, required=True,
        help="Path to output folder")
    args = parser.parse_args()

    visualize(args.input_file, args.output_folder)
