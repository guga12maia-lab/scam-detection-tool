# AI-Powered Phishing Email Detector

An advanced desktop application that uses AI and machine learning to detect phishing emails with detailed threat analysis.

## Features

✅ **AI-Powered Analysis** - LLM-based reasoning for threat detection  
✅ **Multiple Analysis Tools** - Domain verification, URL scanning, urgency detection, spoofing checks  
✅ **Real-time Threat Scoring** - Confidence-based verdicts  
✅ **Professional GUI** - PyQt6 desktop application  
✅ **Dark/Light Theme** - Customizable interface  
✅ **Report Generation** - Detailed analysis reports with copy/export  

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
   - Threat level (🔴 Critical / 🟡 Medium / 🟢 Safe)
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

This application uses OpenAI's API. Typical costs:
- ~$0.03 per email analysis (with GPT-4)
- ~$0.003 per email (with GPT-3.5-turbo)

To save costs, edit `config.py` and change `MODEL_NAME` to `"gpt-3.5-turbo"`.

## Learning Outcomes

By building this project, you'll learn:
- 🤖 LangChain agent architecture
- 🧠 LLM prompting and reasoning chains
- 🔐 Security analysis techniques
- 🖥️ PyQt6 GUI development
- 🔗 API integration (OpenAI)
- 📊 Data analysis and threat modeling
- ⚙️ Async programming in Python

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

## Future Improvementse exact current main window code and am replacing it with the new modern layout.

Updating the input panel with a modern card layout and cleaner controls.

Edited
email_input.py+45-19
Refreshing the app style with modern color palettes, rounded cards, and improved typography.

I’ve updated the GUI files; now I’m verifying the new UI modules for syntax issues.

I’m doing one final import check for the updated UI modules.

Yes — I updated the GUI to a much cleaner, more modern look.

What changed:

new top header and subtitle
modern card-style input/report panels
fresh buttons and status bar
improved layout spacing
updated dark/light theme styles
“Load Example” button added for easy testing
It’s ready to use. Run:

Raptor mini (Preview) • 1x

- [ ] Email file upload (.eml, .msg)
- [ ] Bulk email analysis
- [ ] Phishing statistics dashboard
- [ ] Integration with email clients
- [ ] Local ML models (offline mode)
- [ ] Custom threat rules
- [ ] Email history database

## Disclaimer

This tool is for educational purposes. While it uses advanced AI analysis, no system is 100% accurate. Always verify suspicious emails independently and never click suspicious links.

## License

MIT License - Feel free to use and modify!

## Support

Having issues? 
1. Check the Troubleshooting section
2. Review your API key configuration
3. Check logs in the terminal output
4. Verify all dependencies are installed

---

**Built with ❤️ for cybersecurity enthusiasts**
