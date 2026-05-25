# 2605_DS5111_yaz8bp — VM Setup
## Starting point / prerequisites
This guide assumes you already have:

- A new AWS EC2 VM running **Ubuntu Server 26.04**.
- A GitHub SSH key on the VM that can connect to GitHub.
- Access to this project repository.
- Git available on the VM so you can clone the repo.

This README starts after the VM is running. It does not cover launching the AWS instance.

## Setup steps
### 1. Clone the repo

From the VM home directory, run:

```bash
git clone git@github.com:<your-github-username>/2605_DS5111_yaz8bp.git
cd 2605_DS5111_yaz8bp
```

Replace `<your-github-username>` with your GitHub username.

### 2. Run the bootstrap script

From the repo root, run:

```bash
chmod +x scripts/init.sh
bash scripts/init.sh
```

The script updates the VM package list and installs:

- `make`
- `python3.14-venv`
- `tree`

**Test it worked:**

```bash
tree scripts
```

You should see the `scripts` directory printed in tree form:

```text
scripts
├── init.sh
└── init_git_creds.sh
```

Because `tree` is one of the tools `init.sh` installs, seeing this output instead of `command not found` confirms the script ran successfully.

### 3. Set up git credentials

From the repo root, run:

```bash
chmod +x scripts/init_git_creds.sh
bash scripts/init_git_creds.sh
```

The script sets your global Git email and username so commits are labeled correctly.

**Test it worked:**

```bash
git config --global --list
```

You should see your GitHub email and username:

```text
user.email=your-email@example.com
user.name=your-github-username
```

### 4. Build the Python environment

From the repo root, run:

```bash
make update
```

This creates the `env/` virtual environment, upgrades `pip`, and installs the packages in `requirements.txt`.

**Test it worked:**

```bash
. env/bin/activate
pip list
```

After activating the environment, the terminal prompt should start with `(env)`.

After `pip list`, you should see packages from `requirements.txt`, including:

```text
numpy
pandas
```

At this point, the VM is ready for this project.
