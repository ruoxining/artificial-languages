"""Visualize perplexity scores from fairseq test outputs."""
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def visualize_perplexity(df, output_folder, model_name):
    """Visualize perplexity scores from fairseq test outputs."""
    # NOTE: the csv title should be [setting,div,grammar,perplexity]

    # Average perplexity over divs for each (grammar, setting)
    avg_df = df.groupby(['grammar', 'setting'])['perplexity'].mean().reset_index()

    # Extract group from setting like '1' from '1-1'
    avg_df['group'] = avg_df['setting'].str.extract(r'^(\d+)-')

    # Separate base rows
    base_df = avg_df[avg_df['setting'] == 'base']
    non_base_df = avg_df[avg_df['setting'] != 'base']
    groups = non_base_df['group'].dropna().astype(str).unique()

    # PDF output
    with PdfPages(os.path.join(output_folder, f"{model_name}_perplexity_visualize.pdf")) as pdf:
        for group in sorted(groups):
            group_df = non_base_df[non_base_df['group'] == group]
            combined_df = pd.concat([group_df, base_df], ignore_index=True)

            # Setup consistent x-axis
            grammar_order = sorted(combined_df['grammar'].unique())
            grammar_to_x = {g: i for i, g in enumerate(grammar_order)}
            x_ticks = list(grammar_to_x.values())
            x_labels = grammar_order

            # Prepare color map
            color_map = plt.get_cmap('tab10')  # up to 10 colors
            other_settings = sorted(group_df['setting'].unique())
            color_dict = {setting: color_map(i % 10) for i, setting in enumerate(other_settings)}

            # Plot
            plt.figure(figsize=(14, 6))
            for setting in combined_df['setting'].unique():
                subset = combined_df[combined_df['setting'] == setting]
                x = [grammar_to_x[g] for g in subset['grammar']]

                if setting == 'base':
                    plt.scatter(x, subset['perplexity'], label='base',
                                color='black', marker='^', s=50, alpha=0.6)  # consistent base style
                else:
                    plt.scatter(x, subset['perplexity'], label=setting,
                                color=color_dict[setting])

            plt.xticks(ticks=x_ticks, labels=x_labels, rotation=90)
            plt.xlabel("Grammar")
            plt.ylabel("Average Perplexity")
            plt.title(f"{model_name} Perplexity by Grammar for Settings Group '{group}-*' + base")
            plt.legend(title="Setting", bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()

            # Save current figure to PDF
            pdf.savefig()
            plt.close()

    print("PDF saved with consistent coloring for 'base' and group-specific settings.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser('Visualize perplexity scores from fairseq test outputs.')
    parser.add_argument('--input_file', type=str, required=True, help='input file')
    parser.add_argument('--output_folder', type=str, required=True, help='output folder', default='vis')
    args = parser.parse_args()

    df = pd.read_csv(args.input_file, dtype={"grammar": str})
    model_name = args.input_file.split('-')[0]
    visualize_perplexity(df, args.output_folder, model_name)
