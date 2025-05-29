import subprocess
import argparse

parser = argparse.ArgumentParser(description="Run all jobs")

parser.add_argument("-s", "--num_splits", type=int, default=10,
    help="Number of splits")
parser.add_argument("-n", "--num_choices", type=int, default=6,
    help="Number of choice points")
parser.add_argument("--submission_command", type=str, default="sbatch", 
    help="Command used to submit jobs to HPC system")
parser.add_argument("--job_name", type=str)

args = parser.parse_args()

# original
for i in range(2 ** args.num_choices):
    grammar = format(i, '0' + str(args.num_choices) + 'b')[::-1]

    for j in range(args.num_splits):
        subprocess.call(args.submission_command 
            + f" script/{args.job_name}.sh " 
            + ' '.join([str(grammar), str(j)]), shell=True)

# # data filtered version
# lang = ['0'] * args.num_choices
# for i in range(args.num_choices):
#     lang[args.num_choices - 1 - i] = '1'
#     grammar = 'g' + ''.join(lang)

#     for j in range(args.num_splits):
#         subprocess.call(args.submission_command 
#             + f" script/{args.job_name}.sh " 
#             + ' '.join([str(grammar), str(j)]), shell=True)
