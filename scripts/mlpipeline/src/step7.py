"""
Summary:
This script processes Markdown (.md) files in a specified folder, counts the tokens in each file, and generates both a CSV report and visualizations of the token distributions.
The key functionalities include token counting, saving the results to a CSV file, and generating a histogram and boxplot of the token counts.
The script reads files from the input directory (`step7_input`) and saves the analysis outputs to the output directory (`step7_output`).

Key functionalities:
1. **File Processing**:
    - The script processes Markdown files in the `step7_input` folder to count the number of tokens in each file using the `tiktoken` library.
    - It compiles the token count for each file into a list.

2. **Data Output**:
    - The token counts and associated filenames are saved to a CSV file (`token_count.csv`).

3. **Data Visualization**:
    - A **histogram** (`token_hist.png`) is generated to display the distribution of token counts across the files.
    - A **boxplot** (`token_boxplot.png`) is created to visualize the statistical distribution (including potential outliers) of the token counts.

### Difference from step6.py:
- **Step7.py focuses on token analysis and visualization**:
    - Step6.py is centered on filtering files based on token count (deleting files with more than 1000 tokens or fewer than 40) and uploading them to Azure Blob Storage.
    - Step7.py, on the other hand, focuses on **analyzing** the token distribution of the files by generating statistical plots (histogram and boxplot) and saving token counts to a CSV file.

- **No file deletion or Azure Blob upload in step7.py**:
    - Unlike step6.py, step7.py does not delete files based on token count thresholds, nor does it upload the files to Azure Blob Storage.
      Its main role is to **analyze and visualize** the token counts.
"""

import argparse
import csv
import os

import matplotlib.pyplot as plt
import tiktoken

parser = argparse.ArgumentParser()
parser.add_argument("--step7_input", type=str)
parser.add_argument("--step7_output", type=str)
print("Hello...\nI'm step7 :-)")

args = parser.parse_args()
arr = os.listdir(args.step7_input)
print(f"files in input path: {arr}")


def count_tokens(text, encoding_name="cl100k_base"):
    """Function to count tokens in the text."""
    # Logic to count tokens goes here
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text, disallowed_special=())
    return len(tokens)


def process_markdown_files(folder_path):
    """Process Markdown files in the folder and return token counts as a list."""
    data = []

    # Check all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            print(f"processing <{filename}> ・・・")
            file_path = os.path.join(folder_path, filename)

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                token_count = count_tokens(content)

            data.append((filename, token_count))

    return data


def save_to_csv(data, output_csv):
    """Save token count data to CSV."""
    # Sort data by token count in descending order
    sorted_data = sorted(data, key=lambda x: x[1], reverse=True)

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["File Name", "Token Count"])
        csvwriter.writerows(sorted_data)


def plot_histogram(token_counts, hist_output_png):
    """Plot a histogram of token counts."""
    min_token = min(token_counts)
    max_token = max(token_counts)
    print(min_token, max_token)
    num_bins = 20  # Set the number of bins
    plt.figure(figsize=(10, 6))
    plt.hist(
        token_counts, bins=num_bins, range=(min_token, 1000), edgecolor="black"
    )
    plt.title("Token Count Histogram")
    plt.xlabel("Token Count")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.savefig(hist_output_png)


def plot_boxplot(token_counts, boxplot_output_png):
    """Plot a boxplot of token counts."""
    plt.figure(figsize=(10, 6))
    plt.boxplot(token_counts, vert=False)
    plt.title("Token Count Boxplot")
    plt.xlabel("Token Count")
    plt.grid(True)
    plt.savefig(boxplot_output_png)


if __name__ == "__main__":
    # ===========================================
    # NOTE: Final Result is "Step6 Output"
    # ===========================================
    src_folder = args.step7_input
    dst_folder = args.step7_output

    analysis_output_folder = "./analysis_output"
    output_csv = f"{dst_folder}/token_count.csv"  # Path to the output CSV file
    hist_output_png = f"{dst_folder}/token_hist.png"  # Path to the output token histogram PNG
    boxplot_output_png = (
        f"{dst_folder}/token_boxplot.png"  # Path to the output boxplot PNG
    )

    # Process Markdown files to get token counts
    data = process_markdown_files(src_folder)

    # Save data to CSV
    save_to_csv(data, output_csv)

    # Extract token counts
    token_counts = [count for _, count in data]

    # Plot histogram
    plot_histogram(token_counts, hist_output_png)

    # Plot boxplot
    plot_boxplot(token_counts, boxplot_output_png)
