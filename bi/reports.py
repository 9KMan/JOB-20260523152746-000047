"""
Scheduled Report Delivery
Email/Slack report scheduling
"""
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class ScheduledReport:
    report_id: str
    name: str
    query: str
    schedule: str  # cron expression
    recipients: List[str]
    format: str  # pdf, csv
    last_run: Optional[datetime] = None
    status: str = "active"

class ReportScheduler:
    """Manage scheduled report delivery"""

    def __init__(self):
        self.reports = {}

    def schedule_report(self, report: ScheduledReport):
        self.reports[report.report_id] = report
        logger.info(f"Scheduled report: {report.name} ({report.schedule})")

    def get_report(self, report_id: str) -> Optional[ScheduledReport]:
        return self.reports.get(report_id)

    def list_reports(self) -> List[ScheduledReport]:
        return list(self.reports.values())

    def execute_report(self, report_id: str) -> str:
        """Execute a report and return output path"""
        report = self.get_report(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        # In production, this would:
        # 1. Execute the query against the Gold layer
        # 2. Generate PDF/CSV
        # 3. Send to recipients
        logger.info(f"Executing report: {report.name}")

        output_path = f"/tmp/reports/{report_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{report.format}"
        return output_path

    def cancel_report(self, report_id: str):
        if report_id in self.reports:
            self.reports[report_id].status = "cancelled"
            logger.info(f"Cancelled report: {report_id}")

class EmailSender:
    """Email delivery for reports"""

    def __init__(self, smtp_host: str, smtp_port: int = 587):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send(self, to: List[str], subject: str, body: str, attachments: Optional[List[str]] = None):
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart()
        msg['From'] = 'data-pipeline@example.com'
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.send_message(msg)

        logger.info(f"Sent email to {len(to)} recipients")

class SlackReporter:
    """Slack delivery for reports"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, channel: str, message: str, file_path: Optional[str] = None):
        import requests
        import json

        payload = {
            "channel": channel,
            "text": message
        }

        if file_path:
            # Upload file first, then send message
            pass

        response = requests.post(self.webhook_url, json=payload)
        response.raise_for_status()
        logger.info(f"Sent Slack message to {channel}")