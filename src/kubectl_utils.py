import subprocess


def run_kubectl_command(command):
    # Extract the kubectl command from the user input
    if "kubectl" in command:
        kubectl_cmd = command[command.index("kubectl") :]
    else:
        kubectl_cmd = f"kubectl {command}"
    try:
        result = subprocess.check_output(
            kubectl_cmd, shell=True, stderr=subprocess.STDOUT, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        return f"Error running kubectl: {e.output}"
