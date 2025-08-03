```
   _____ _    _  ____ _______ _    _
  / ____| |  | |/ __ \__   __| |  | |
 | |    | |__| | |  | | | |  | |  | |
 | |    |  __  | |  | | | |  | |  | |
 | |____| |  | | |__| | | |  | |__| |
  \_____|_|  |_|\____/  |_|   \____/
```

# Chotu - Personal AI Agent

Chotu is a personalized agent that utilizes a local LLM (by default Qwen3 7B, but you can use any compatible model by setting the environment variable) to perform various tasks such as listing GitHub pull requests and executing kubectl commands. The agent is designed to streamline workflows and enhance productivity by automating common tasks.

## Project Structure

```
chotu/
├── src/
│   ├── agent.py           # Main logic for the personalized agent
│   ├── llm_interface.py   # Interface for interacting with the LLM
│   ├── github_utils.py    # Functions for interacting with the GitHub MCP API
│   ├── kubectl_utils.py   # Functions for executing kubectl commands
├── requirements.txt       # Project dependencies
├── Dockerfile             # Instructions for building the Docker image
├── .env                   # Local environment variables (not committed)
├── .env.example           # Template for environment variables
└── README.md              # Project documentation
```

## Environment Setup

Before running the agent, create a `.env` file in the project root. You can copy `.env.example` as a template:

```sh
cp .env.example .env
```

Edit `.env` to set your local LLM endpoint and model:

```
LLM_BASE_URL=http://localhost:12434/
LLM_MODEL=ai/gemma3
```

The agent will automatically read these values from the environment.

## Setup Instructions

1. **Clone the repository:**

   ```
   git clone <repository-url>
   cd chotu
   ```

2. **Install dependencies:**
   You can install the required Python packages using pip:

   ```
   pip install -r requirements.txt
   ```

3. **Build the Docker image:**
   If you prefer to run the application in a Docker container, build the image using:

   ```
   docker build -t chotu .
   ```

4. **Source environment variables:**
   Before running the application, make sure to load the environment variables from your `.env` file:

   ```sh
   source .env
   ```

5. **Run the application:**
   You can run the application directly or through Docker:
   ```
   python src/agent.py
   ```
   Or, if using Docker:
   ```
   docker run chotu
   ```

## Usage

Once the application is running, you can interact with Chotu through the command line. The agent can perform the following tasks:

- **List GitHub Pull Requests:**
  You can ask Chotu to retrieve pull requests from a specified GitHub repository.

- **Run Kubectl Commands:**
  Chotu can execute kubectl commands to manage Kubernetes resources.

## Capabilities

Chotu is designed to be extensible. You can add more functionalities by modifying the `src` directory files. The main components include:

- **Agent Logic:** Located in `src/agent.py`, this file handles user input and coordinates tasks.
- **LLM Interface:** The `src/llm_interface.py` file manages interactions with the Qwen3 7B model.
- **GitHub Utilities:** Functions for GitHub API interactions are defined in `src/github_utils.py`.
- **Kubectl Utilities:** Command execution functions are found in `src/kubectl_utils.py`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
