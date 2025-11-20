import subprocess
import shlex

total_users = 2
token_native = "C2FLR"
token_underlying = "testXRP"

tasks = [
    "mint_lowest_fee_agent_random_amount"
]
run_time = "30s"

def run_locust():
    # Define the Locust command
    command = (
        f"locust -f src/tasks/tasks.py -u {total_users} -r 1 --run-time {run_time} --host '' "
        f"--token-native {token_native} --token-underlying {token_underlying} "
        f"--user-nums {','.join(map(str, range(total_users)))} "
        f"--tasks {','.join(tasks)} "
    )

    # Use shlex.split to safely split the command into a list
    command_list = shlex.split(command)

    try:
        print("Running Locust with the following command:")
        print(command)
        result = subprocess.run(command_list, check=True, text=True)
        print("Locust Output:")
        print(result.stdout)  # Print Locust's output
    except subprocess.CalledProcessError as e:
        print("Error running Locust:")
        print(e.stderr)  # Print error output if the command fails

if __name__ == "__main__":
    run_locust()
