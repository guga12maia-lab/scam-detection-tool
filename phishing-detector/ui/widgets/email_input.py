from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt

class EmailInputWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)

        label = QLabel("Paste the email content below")
        label.setObjectName("sectionLabel")
        layout.addWidget(label)

        self.email_input = QTextEdit()
        self.email_input.setPlaceholderText(
            "Paste raw email content here...\n\n"
            "Example formats:\n"
            "- Full email headers and body\n"
            "- Subject + message body\n"
            "- Email text copied from your inbox"
        )
        self.email_input.setMinimumHeight(280)
        self.email_input.setObjectName("inputField")
        layout.addWidget(self.email_input)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("secondaryButton")
        self.clear_btn.clicked.connect(self.clear_input)
        button_layout.addWidget(self.clear_btn)

        self.sample_btn = QPushButton("Load Example")
        self.sample_btn.setObjectName("secondaryButton")
        self.sample_btn.clicked.connect(self.load_sample)
        button_layout.addWidget(self.sample_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_email_content(self):
        return self.email_input.toPlainText()

    def clear_input(self):
        self.email_input.clear()

    def set_email_content(self, content):
        self.email_input.setPlainText(content)

    def load_sample(self):
        sample_text = (
            "From: security@paypa1.com\n"
            "To: user@example.com\n"
            "Subject: URGENT: Verify Your Account Immediately\n\n"
            "Dear Customer,\n\n"
            "We detected suspicious activity and need you to verify your account now. "
            "Click here to confirm your login information: http://bit.ly/verify-now\n\n"
            "Thank you,\n"
            "Security Team"
        )
        self.set_email_content(sample_text)

