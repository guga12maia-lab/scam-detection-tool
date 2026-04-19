from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout


class EmailInputWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.email_input = QTextEdit()
        self.email_input.setObjectName("inputField")
        self.email_input.setPlaceholderText(
            "Paste raw email content here…\n\n"
            "Accepted formats:\n"
            "  • Full headers + body\n"
            "  • Subject + message body\n"
            "  • Plain email text from your inbox"
        )
        self.email_input.setMinimumHeight(260)
        layout.addWidget(self.email_input)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("secondaryBtn")
        self.clear_btn.setFixedHeight(34)
        self.clear_btn.clicked.connect(self.email_input.clear)
        btn_row.addWidget(self.clear_btn)

        self.sample_btn = QPushButton("Load Example")
        self.sample_btn.setObjectName("secondaryBtn")
        self.sample_btn.setFixedHeight(34)
        self.sample_btn.clicked.connect(self._load_sample)
        btn_row.addWidget(self.sample_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

    def get_email_content(self) -> str:
        return self.email_input.toPlainText()

    def set_email_content(self, text: str):
        self.email_input.setPlainText(text)

    def _load_sample(self):
        self.email_input.setPlainText(
            "From: security@paypa1.com\n"
            "To: user@example.com\n"
            "Subject: URGENT: Your account will be suspended!\n\n"
            "Dear Valued Customer,\n\n"
            "We have detected suspicious activity on your account. "
            "You MUST verify your information within 24 hours or your account "
            "will be permanently suspended.\n\n"
            "Click here immediately: http://bit.ly/verify-paypal-now\n\n"
            "Thank you,\n"
            "PayPal Security Team"
        )
