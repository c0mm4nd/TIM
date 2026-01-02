# LLM4Intent

<img width="555" height="444" alt="website_preview" src="https://github.com/user-attachments/assets/5e159702-580c-4208-bd7e-873a5c5e631c" />

## Overview

**LLM4Intent** is an advanced blockchain transaction analysis system that leverages Large Language Models (LLMs) to automatically identify and categorize user intents from Ethereum transactions. By combining multi-agent AI systems with comprehensive blockchain data analysis, it provides deep insights into transaction purposes, patterns, and behaviors.

## 🎯 Key Features

- **Multi-Agent Analysis System**: Utilizes specialized AI agents (MetaController, DomainExpert, QuestionSolver, Checker, Scorer) working in parallel to analyze transactions from multiple perspectives
- **Hierarchical Intent Classification**: Categorizes transactions into a comprehensive taxonomy of DeFi activities including:
  - Investment and Trading (Speculation, HODLing, Arbitrage)
  - Liquidity Mining and Yield Farming
  - Staking (ETH Liquid Staking, Governance Token Staking)
  - Early Project Participation (Airdrops, Presales)
  - Risk Management and Asset Security
- **Comprehensive Data Collection**: Integrates multiple data sources:
  - Transaction details and receipts
  - Smart contract analysis (code, ABI, storage)
  - Token transfers and balance tracking
  - Address labeling and historical patterns
  - Web search for contextual information
- **Flexible Deployment Options**: Supports CLI, FastAPI server, and Gradio demo interface

## 🏗️ Architecture

The system follows a sophisticated multi-stage analysis workflow:

1. **Meta Planning**: MetaController analyzes the transaction and creates perspectives for analysis
2. **Parallel Expert Analysis**: Multiple DomainExpert agents analyze the transaction from different angles:
   - Each expert breaks down their perspective into specific questions
   - QuestionSolver agents gather facts and data using available tools
   - Experts synthesize findings into intent classifications
3. **Cross-Validation**: StatelessChecker validates findings across different perspectives
4. **Final Scoring**: StatelessScorer aggregates all analyses and produces final intent classification

```
Transaction Hash
       ↓
  MetaController (Plan Generation)
       ↓
  ┌────┴────┬────────┬────────┐
  ↓         ↓        ↓        ↓
Expert1  Expert2  Expert3  Expert4  (Parallel Analysis)
  ↓         ↓        ↓        ↓
  └────┬────┴────────┴────────┘
       ↓
  StatelessChecker (Validation)
       ↓
  StatelessScorer (Final Report)
```

## 📋 Prerequisites

- Python >= 3.11, < 3.13
- Poetry (Python dependency management)
- API keys for:
  - OpenAI (or compatible LLM provider)
  - Etherscan (for blockchain data)
  - Web3Research (for historical blockchain data)
  - Optional: Groq, Google AI

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/c0mm4nd/TIM.git
   cd TIM
   ```

2. **Install dependencies with Poetry**:
   ```bash
   poetry install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

   Required environment variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ETHERSCAN_API_KEY=your_etherscan_api_key
   W3R_API_KEY=your_web3research_api_key
   W3R_BACKEND=your_web3research_backend_url
   
   # Optional
   GROQ_API_KEY=your_groq_api_key
   GOOGLE_API_KEY=your_google_api_key
   ```

## ⚙️ Configuration

Edit `config.json` to specify transactions to analyze:

```json
{
  "txs": [
    "0x88d0857df80bfba03c8274252dbde965ff3651357196e7d906cfb030c3b5de5c"
  ]
}
```

The `intent_cat.json` file contains the hierarchical intent taxonomy used for classification.

## 📖 Usage

### CLI Mode (Analyze transactions from config)

```bash
poetry run start --config config.json --pwd ./output
```

Options:
- `--config`: Path to configuration file (default: `config.json`)
- `--pwd`: Working directory for output files (default: `.`)
- `--openai-api-key`: Override OpenAI API key
- `--openai-base-url`: Override OpenAI base URL (for compatible APIs)

### Sample Mode (Analyze random transactions from a contract)

```bash
poetry run sample --contract 0xYourContractAddress --txs 100 --tfs 100 --final 5
```

Options:
- `--contract`: Contract address to sample transactions from
- `--txs`: Number of regular transactions to sample (default: 100)
- `--tfs`: Number of token transfer transactions to sample (default: 100)
- `--final`: Final number of transactions to analyze (default: 5)

### FastAPI Server Mode

```bash
poetry run serve
```

Starts a FastAPI server on port 58000 with endpoints:
- `GET /`: Health check
- `GET /start`: Trigger analysis

### Gradio Demo Mode

```bash
poetry run demo
```

Launches an interactive web interface for transaction analysis.

## 📁 Project Structure

```
LLM4Intent/
├── __main__.py           # Entry points and workflow orchestration
├── roles/                # AI agent definitions
│   ├── meta_controller.py      # Planning and perspective generation
│   ├── domain_expert.py        # Expert analysis agents
│   ├── question_solver.py      # Data gathering and question answering
│   ├── stateless_checker.py   # Cross-validation of findings
│   └── stateless_scorer.py    # Final scoring and classification
├── tools/                # Data collection and analysis tools
│   ├── annotated.py            # Annotated tool definitions
│   ├── jsonrpc.py              # Direct RPC calls to Ethereum nodes
│   ├── etherscan.py            # Etherscan API integration
│   ├── web3research.py         # Historical blockchain data queries
│   └── web2.py                 # Web search and information extraction
└── common/               # Shared utilities
    ├── utils.py                # Logging and utilities
    ├── state.py                # State management
    └── intent_defination.py    # Intent classification definitions
```

## 🔧 Available Tools

The system provides agents with various tools to analyze transactions:

**Blockchain Data**:
- `get_transaction()`: Fetch transaction details
- `get_transaction_receipt()`: Get transaction execution results
- `get_transaction_trace()`: Internal transaction traces
- `get_contract_code_at_block_number()`: Smart contract bytecode
- `get_contract_source_code()`: Verified contract source code
- `get_contract_ABI()`: Contract interface definitions

**Historical Analysis**:
- `get_address_transactions_within_block_number_range()`: Transaction history
- `get_address_token_transfers_within_block_number_range()`: Token movement patterns
- `get_address_eth_balance_at_block_number()`: Balance at specific blocks

**Contextual Information**:
- `get_address_label()`: Known address labels
- `search_webpages()`: Search for relevant information
- `extract_webpage_info_by_urls()`: Extract data from web pages

## 📊 Output

Analysis results are saved to the working directory in markdown format:
- `score_reports/{transaction_hash}.output.md`: Detailed analysis report including:
  - Perspective-based analyses
  - Validation results
  - Final intent classification with confidence scores

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the terms specified by the repository owner.

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain) and [AutoGen](https://github.com/microsoft/autogen)
- Blockchain data provided by [Web3Research](https://github.com/njublockchain/web3research-py)
- Contract information from [Etherscan](https://etherscan.io/)

## 📮 Contact

For questions or support, please open an issue on the [GitHub repository](https://github.com/c0mm4nd/TIM).
