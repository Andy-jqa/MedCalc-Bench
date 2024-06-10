import re
import os
import argparse
import numpy as np
import pandas as pd

categories = ['lab', 'physical', 'date', 'dosage', 'risk', 'severity', 'diagnosis']

def check_correctness(answer: str, ground_truth, calid, upper_limit, lower_limit):
    if calid in [13, 68]:
        # Output Type: date
        if answer == ground_truth:
            correctness = 1
        else:
            correctness = 0
    elif calid in [69]:
        # Output Type: integer (A, B)
        match = re.search(r"\(?[\"\']?(\d+)\s*(weeks?)?[\"\']?,?\s*[\"\']?(\d+)\s*(days?)?[\"\']?\s*\)?", ground_truth)
        ground_truth = f"({match.group(1)}, {match.group(3)})"
        match = re.search(r"\(?[\"\']?(\d+)\s*(weeks?)?[\"\']?,?\s*[\"\']?(\d+)\s*(days?)?[\"\']?\s*\)?", answer)
        if match:
            weeks = match.group(1)
            days = match.group(3)
            answer = f"({weeks}, {days})"
            if eval(answer) == eval(ground_truth):
                correctness = 1
            else:
                correctness = 0
        else:
            correctness = 0
    elif calid in [4, 15, 16, 17, 18, 20, 21, 25, 27, 28, 29, 32, 33, 36, 43, 45, 48, 51, 69]:
        # Output Type: integer A
        answer = round(eval(answer))
        if answer == eval(ground_truth):
            correctness = 1
        else:
            correctness = 0
    elif calid in [2,  3,  5,  6,  7,  8,  9, 10, 11, 19, 22, 23, 24, 26, 30, 31, 38, 39, 40, 44, 46, 49, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67]:
        # Output Type: decimal
        answer = eval(answer)
        if answer >= eval(lower_limit) and answer <= eval(upper_limit):
            correctness = 1
        else:
            correctness = 0
    else:
        raise ValueError(f"Unknown calculator ID: {calid}")
    return correctness

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Parse arguments')
    parser.add_argument('--fpath', type=str)

    args = parser.parse_args()

    fpath = args.fpath
    
    df = pd.read_csv("ground_truth_data.csv")
    answers = open(fpath).read().splitlines()

    correctness_list = []
    for index in range(len(answers)):
        truth = df.iloc[index]
        try:
            correctness = check_correctness(answers[index], truth["Ground Truth Answer"], truth["Calculator ID"], truth["Upper Limit"], truth["Lower Limit"])
        except Exception as e:
            # print(f"Error at index {index}: {e}")
            correctness = 0
        correctness_list.append(correctness)

    df["correctness"] = correctness_list

    scores = []
    for category in categories:
        df_cat = df[df["Category"] == category]
        acc = df_cat["correctness"].sum()/len(df_cat["correctness"])
        print(f"Category: {category} | Accuracy: {acc*100:.2f}% | Std: {np.sqrt(acc * (1-acc) / len(df_cat)):.2f}")
        scores += df_cat["correctness"].tolist()
    
    print(f"Overall Accuracy: {np.mean(scores)*100:.2f}% | Std: {np.sqrt(np.mean(scores) * (1-np.mean(scores)) / len(scores)):.2f}")
