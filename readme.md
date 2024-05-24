# foorse

**foorse** is a tool designed to help researchers parse Russian government statistical forms about education, particularly forms like ВПО-1 (higher education), СПО-1 (professional education), and 1-ПК (additional education), etc. The tool automates the extraction, analysis, and storage of statistical data from HTML files into a structured SQLite database, leveraging AI for enhanced data interpretation.

This project is supported by [https://uni.hse.ru](Laboratory for University Development) of [https://ioe.hse.ru](HSE Institute of Education).

If you're planning to use this code for some other forms, it might require some tinkering with the code ;)

## Features

- **Automated Data Extraction**: Parses HTML files containing statistical data tables.
- **AI Integration**: Uses OpenAI to analyze and generate metadata about the tables.
- **Database Storage**: Stores extracted data in a structured SQLite database.
- **Logging**: Provides detailed logging using the `logging` module and `rich` for enhanced console logging.

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/foorse.git
    cd foorse
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Configure the project**:
    - Update the `config.py` file with your OpenAI API key and other necessary configurations.

2. **Run the main script**:
    ```bash
    python main.py
    ```

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details (warning: it's in Russian).
