# AI-Powered Phishing Email Detector

An advanced desktop application that uses AI and machine learning to detect phishing emails with detailed threat analysis.

## Features

**AI-Powered Analysis** - LLM-based reasoning for threat detection  
**Multiple Analysis Tools** - Domain verification, URL scanning, urgency detection, spoofing checks  
**Real-time Threat Scoring** - Confidence-based verdicts   
**Dark/Light Theme** - Customizable interface  
**Report Generation** - Detailed analysis reports with copy/export  

## Installation

### Requirements
- Python 3.8+
- OpenAI API key (get one at https://platform.openai.com)

### Setup Steps

1. **Clone or download this project**
   ```bash
   cd phishing-detector
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Key**
   
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   THEME=dark
   LOG_LEVEL=INFO
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## Usage

1. **Paste Email Content**
   - Paste raw email text (with headers) or just the email body
   - Format can be from Outlook, Gmail, or any email client

2. **Click "ANALYZE EMAIL"**
   - The AI agent will analyze the email
   - Multiple security tools run in parallel
   - LLM generates reasoning and verdict

3. **Review Report**
   - Threat level ( Critical / Medium / Safe)
   - Confidence score
   - Detailed reasoning
   - Recommendations

4. **Export Report** (optional)
   - Copy to clipboard
   - Save for records

## How It Works

```
Email Input
    ↓
[Multiple Analysis Tools]
├─ Domain Reputation Check
├─ URL Maliciousness Scan
├─ Urgency Indicator Detection
├─ Sender Spoofing Analysis
└─ Grammar Quality Check
    ↓
[LLM Reasoning Engine (GPT-4)]
    ↓
[Threat Verdict Generation]
```

### Analysis Tools

- **Domain Check** - Verifies if sender domain is legitimate using DNS
- **URL Scanner** - Detects suspicious URL patterns, shorteners, encoding
- **Urgency Analysis** - Flags pressure tactics and emotional manipulation
- **Spoofing Detection** - Identifies lookalike domains and header anomalies
- **Grammar Check** - Detects poor spelling/grammar common in phishing

## Project Structure

```
phishing-detector/
├── main.py                    # Application entry point
├── config.py                  # Configuration & settings
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
│
├── agents/
│   ├── phishing_agent.py      # Main AI agent orchestration
│   └── tools.py               # Analysis tools
│
├── models/
│   └── email_analyzer.py      # Email parsing & extraction
│
├── ui/
│   ├── main_window.py         # Main GUI window
│   ├── styles.py              # Dark/Light themes
│   └── widgets/
│       ├── email_input.py     # Email input widget
│       └── report_display.py  # Report display widget
│
└── utils/
    ├── logger.py              # Logging setup
    └── validators.py          # Validation utilities
```

## Technology Stack

| Component | Technology |
|-----------|-----------|
| GUI Framework | PyQt6 |
| AI/LLM | LangChain + OpenAI GPT-4 |
| Email Parsing | Python email library |
| Domain Checks | dnspython |
| Async | asyncio |
| Validation | email-validator |

## API Costs

## Troubleshooting

**Error: "OPENAI_API_KEY not set"**
- Make sure you created `.env` file with your API key

**Error: "ModuleNotFoundError"**
- Run `pip install -r requirements.txt` again
- Make sure venv is activated

**Slow Analysis**
- First run might be slow as LLM loads
- Subsequent analyses will be faster
- Check your internet connection

**GUI Not Appearing**
- Make sure PyQt6 is installed: `pip install pyqt6`
- Try running from terminal to see error messages


## Disclaimer

This tool is for educational purposes. While it uses advanced AI analysis, no system is 100% accurate. Always verify suspicious emails independently and never click suspicious links.

**Built with ❤️ for cybersecurity enthusiasts**
