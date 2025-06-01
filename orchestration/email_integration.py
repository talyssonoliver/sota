#!/usr/bin/env python3
"""
Email Integration System - Phase 6 Step 6.6

Automated email distribution for briefings and reports with HTML templates,
recipient management, and delivery scheduling.
"""

import json
import logging
import smtplib
import sys
import asyncio
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Dict, List, Optional, Any
from jinja2 import Template

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class EmailIntegration:
    """
    Email integration system for automated briefing and report distribution.
    """
    
    def __init__(self, config_path: str = "config/daily_cycle.json"):
        """Initialize the email integration system."""
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Email configuration
        self.email_config = self.config.get("email", {})
        self.enabled = self.email_config.get("enabled", False)
        
        # Templates directory
        self.templates_dir = Path("templates/email")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize email templates
        self._create_default_templates()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load config from {config_path}: {e}")
            return self._get_default_email_config()
    
    def _get_default_email_config(self) -> Dict[str, Any]:
        """Get default email configuration."""
        return {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "use_tls": True,
                "username": "",
                "password": "",
                "from_address": "ai-system@company.com",
                "recipients": {
                    "team_leads": [],
                    "stakeholders": [],
                    "developers": []
                },
                "retry_attempts": 3,
                "retry_delay": 60
            }
        }
    
    def _create_default_templates(self):
        """Create default email templates if they don't exist."""
        # Morning briefing template
        briefing_template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #2196F3; color: white; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #2196F3; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background-color: #f5f5f5; border-radius: 3px; }
        .priority { color: #FF6B35; font-weight: bold; }
        .blocker { color: #FF0000; font-weight: bold; }
        .completed { color: #4CAF50; font-weight: bold; }
        .table { border-collapse: collapse; width: 100%; }
        .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .table th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌅 Daily Morning Briefing - {{date}}</h1>
        <p>Sprint Health: <span class="{{sprint_health_class}}">{{sprint_health}}</span></p>
    </div>
    
    <div class="section">
        <h2>📊 Sprint Metrics</h2>
        <div class="metric">📋 Total Tasks: {{total_tasks}}</div>
        <div class="metric">✅ Completed: {{completed_tasks}}</div>
        <div class="metric">📈 Progress: {{completion_rate}}%</div>
        <div class="metric">🎯 Team Velocity: {{team_velocity}}</div>
    </div>
    
    {% if today_priorities %}
    <div class="section">
        <h2>🎯 Today's Priorities</h2>
        {% for priority in today_priorities %}
        <div class="priority">• {{priority}}</div>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if blockers %}
    <div class="section">
        <h2>🚫 Active Blockers</h2>
        {% for blocker in blockers %}
        <div class="blocker">🚫 {{blocker.title}} - {{blocker.impact}}</div>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if recommendations %}
    <div class="section">
        <h2>💡 Recommendations</h2>
        {% for rec in recommendations %}
        <div class="priority">💡 {{rec}}</div>
        {% endfor %}
    </div>
    {% endif %}
    
    <div class="section">
        <p><a href="{{dashboard_url}}">View Full Dashboard</a> | <a href="{{report_url}}">Detailed Report</a></p>
    </div>
</body>
</html>
        """
        
        briefing_template_path = self.templates_dir / "morning_briefing.html"
        if not briefing_template_path.exists():
            briefing_template_path.write_text(briefing_template, encoding='utf-8')
        
        # End-of-day report template
        eod_template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #4CAF50; color: white; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #4CAF50; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background-color: #f5f5f5; border-radius: 3px; }
        .accomplishment { color: #4CAF50; font-weight: bold; margin: 5px 0; }
        .challenge { color: #FF6B35; font-weight: bold; margin: 5px 0; }
        .tomorrow { color: #2196F3; font-weight: bold; margin: 5px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌙 End-of-Day Report - {{date}}</h1>
        <p>Daily Productivity Score: {{productivity_score}}/10</p>
    </div>
    
    <div class="section">
        <h2>📊 Daily Summary</h2>
        <div class="metric">✅ Tasks Completed: {{completed_today}}</div>
        <div class="metric">🚀 Tasks Started: {{started_today}}</div>
        <div class="metric">🚫 Blocked Tasks: {{blocked_today}}</div>
        <div class="metric">📈 Daily Velocity: {{daily_velocity}}</div>
    </div>
    
    {% if accomplishments %}
    <div class="section">
        <h2>🎉 Key Accomplishments</h2>
        {% for accomplishment in accomplishments %}
        <div class="accomplishment">✅ {{accomplishment}}</div>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if challenges %}
    <div class="section">
        <h2>⚠️ Challenges Faced</h2>
        {% for challenge in challenges %}
        <div class="challenge">⚠️ {{challenge}}</div>
        {% endfor %}
    </div>
    {% endif %}
    
    {% if tomorrow_prep %}
    <div class="section">
        <h2>🗓️ Tomorrow's Preparation</h2>
        {% for item in tomorrow_prep %}
        <div class="tomorrow">📋 {{item}}</div>
        {% endfor %}
    </div>
    {% endif %}
    
    <div class="section">
        <p><a href="{{dashboard_url}}">View Dashboard</a> | <a href="{{detailed_report_url}}">Detailed Report</a></p>
    </div>
</body>
</html>
        """
        
        eod_template_path = self.templates_dir / "eod_report.html"
        if not eod_template_path.exists():
            eod_template_path.write_text(eod_template, encoding='utf-8')
    
    async def send_morning_briefing(self, briefing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send morning briefing email."""
        if not self.enabled:
            self.logger.info("Email integration disabled, skipping briefing email")
            return {"status": "skipped", "reason": "email_disabled"}
        
        try:
            # Load template
            template_path = self.templates_dir / "morning_briefing.html"
            template = Template(template_path.read_text(encoding='utf-8'))
            
            # Prepare template data
            template_data = self._prepare_briefing_template_data(briefing_data)
            
            # Render HTML content
            html_content = template.render(**template_data)
            
            # Send to team leads and stakeholders
            recipients = self._get_briefing_recipients()
            
            result = await self._send_email(
                recipients=recipients,
                subject=f"📊 Daily Morning Briefing - {datetime.now().strftime('%Y-%m-%d')}",
                html_content=html_content,
                text_content=self._html_to_text(html_content)
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending morning briefing: {e}")
            return {"status": "error", "message": str(e)}
    
    async def send_eod_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send end-of-day report email."""
        if not self.enabled:
            self.logger.info("Email integration disabled, skipping EOD report email")
            return {"status": "skipped", "reason": "email_disabled"}
        
        try:
            # Load template
            template_path = self.templates_dir / "eod_report.html"
            template = Template(template_path.read_text(encoding='utf-8'))
            
            # Prepare template data
            template_data = self._prepare_eod_template_data(report_data)
            
            # Render HTML content
            html_content = template.render(**template_data)
            
            # Send to all recipients
            recipients = self._get_all_recipients()
            
            result = await self._send_email(
                recipients=recipients,
                subject=f"📈 End-of-Day Report - {datetime.now().strftime('%Y-%m-%d')}",
                html_content=html_content,
                text_content=self._html_to_text(html_content)
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending EOD report: {e}")
            return {"status": "error", "message": str(e)}
    
    def _prepare_briefing_template_data(self, briefing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare template data for morning briefing."""
        sprint_metrics = briefing_data.get("sprint_metrics", {})
        
        return {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "total_tasks": sprint_metrics.get("total_tasks", 0),
            "completed_tasks": sprint_metrics.get("completed_tasks", 0),
            "completion_rate": f"{sprint_metrics.get('completion_rate', 0):.1f}",
            "team_velocity": sprint_metrics.get("team_velocity", "N/A"),
            "sprint_health": briefing_data.get("sprint_health", {}).get("status", "UNKNOWN"),
            "sprint_health_class": self._get_health_css_class(briefing_data.get("sprint_health", {}).get("status", "UNKNOWN")),
            "today_priorities": briefing_data.get("today_priorities", [])[:5],  # Top 5
            "blockers": briefing_data.get("blockers", [])[:3],  # Top 3
            "recommendations": briefing_data.get("recommendations", [])[:3],  # Top 3
            "dashboard_url": "http://localhost:5000/dashboard/realtime_dashboard.html",
            "report_url": briefing_data.get("output_file", "#")
        }
    
    def _prepare_eod_template_data(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare template data for end-of-day report."""
        daily_summary = report_data.get("daily_summary", {})
        task_analysis = report_data.get("task_analysis", {})
        
        return {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "productivity_score": task_analysis.get("productivity_score", 5),
            "completed_today": task_analysis.get("completed_count", 0),
            "started_today": task_analysis.get("started_count", 0),
            "blocked_today": task_analysis.get("blocked_count", 0),
            "daily_velocity": daily_summary.get("daily_velocity", "N/A"),
            "accomplishments": daily_summary.get("key_accomplishments", [])[:5],
            "challenges": daily_summary.get("challenges_faced", [])[:3],
            "tomorrow_prep": report_data.get("tomorrow_prep", {}).get("recommended_actions", [])[:5],
            "dashboard_url": "http://localhost:5000/dashboard/realtime_dashboard.html",
            "detailed_report_url": report_data.get("output_file", "#")
        }
    
    def _get_health_css_class(self, health_status: str) -> str:
        """Get CSS class for sprint health status."""
        health_classes = {
            "HEALTHY": "completed",
            "NEEDS_ATTENTION": "priority",
            "AT_RISK": "blocker",
            "CRITICAL": "blocker"
        }
        return health_classes.get(health_status, "priority")
    
    def _get_briefing_recipients(self) -> List[str]:
        """Get recipients for morning briefing."""
        recipients = []
        recipients.extend(self.email_config.get("recipients", {}).get("team_leads", []))
        recipients.extend(self.email_config.get("recipients", {}).get("stakeholders", []))
        return list(set(recipients))  # Remove duplicates
    
    def _get_all_recipients(self) -> List[str]:
        """Get all email recipients."""
        recipients = []
        for role, emails in self.email_config.get("recipients", {}).items():
            recipients.extend(emails)
        return list(set(recipients))  # Remove duplicates
    
    async def _send_email(self, recipients: List[str], subject: str, 
                         html_content: str, text_content: str,
                         attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send email with retry logic."""
        if not recipients:
            return {"status": "skipped", "reason": "no_recipients"}
        
        for attempt in range(self.email_config.get("retry_attempts", 3)):
            try:
                # Create message
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.email_config.get("from_address", "ai-system@company.com")
                msg['To'] = ", ".join(recipients)
                
                # Add text and HTML parts
                msg.attach(MIMEText(text_content, 'plain'))
                msg.attach(MIMEText(html_content, 'html'))
                
                # Add attachments if provided
                if attachments:
                    for attachment_path in attachments:
                        self._add_attachment(msg, attachment_path)
                
                # Send email
                with smtplib.SMTP(self.email_config.get("smtp_server", "smtp.gmail.com"), 
                                 self.email_config.get("smtp_port", 587)) as server:
                    if self.email_config.get("use_tls", True):
                        server.starttls()
                    
                    username = self.email_config.get("username")
                    password = self.email_config.get("password")
                    
                    if username and password:
                        server.login(username, password)
                    
                    server.send_message(msg)
                
                self.logger.info(f"Email sent successfully to {len(recipients)} recipients")
                return {
                    "status": "success",
                    "recipients": recipients,
                    "attempt": attempt + 1
                }
                
            except Exception as e:
                self.logger.warning(f"Email send attempt {attempt + 1} failed: {e}")
                if attempt < self.email_config.get("retry_attempts", 3) - 1:
                    await asyncio.sleep(self.email_config.get("retry_delay", 60))
                else:
                    return {"status": "error", "message": str(e)}
    
    def _add_attachment(self, msg: MIMEMultipart, attachment_path: str):
        """Add attachment to email message."""
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {Path(attachment_path).name}'
            )
            msg.attach(part)
        except Exception as e:
            self.logger.warning(f"Could not add attachment {attachment_path}: {e}")
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML to plain text."""
        # Simple HTML to text conversion
        import re
        
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', html_content)
        
        # Replace HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
    
    def configure_email(self, smtp_server: str, smtp_port: int, username: str, 
                       password: str, from_address: str) -> bool:
        """Configure email settings."""
        try:
            self.email_config.update({
                "enabled": True,
                "smtp_server": smtp_server,
                "smtp_port": smtp_port,
                "username": username,
                "password": password,
                "from_address": from_address
            })
            
            # Save to config file
            self.config["email"] = self.email_config
            with open("config/daily_cycle.json", 'w') as f:
                json.dump(self.config, f, indent=4)
            
            self.enabled = True
            self.logger.info("Email configuration updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configuring email: {e}")
            return False
    
    def add_recipients(self, role: str, emails: List[str]) -> bool:
        """Add email recipients for a specific role."""
        try:
            if "recipients" not in self.email_config:
                self.email_config["recipients"] = {}
            
            if role not in self.email_config["recipients"]:
                self.email_config["recipients"][role] = []
            
            # Add new emails
            for email in emails:
                if email not in self.email_config["recipients"][role]:
                    self.email_config["recipients"][role].append(email)
            
            # Save to config file
            self.config["email"] = self.email_config
            with open("config/daily_cycle.json", 'w') as f:
                json.dump(self.config, f, indent=4)
            
            self.logger.info(f"Added {len(emails)} recipients to {role}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding recipients: {e}")
            return False


async def main():
    """Main entry point for email integration testing."""
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(description="Email Integration System")
    parser.add_argument("--test", action="store_true", help="Test email configuration")
    parser.add_argument("--configure", action="store_true", help="Configure email settings")
    parser.add_argument("--send-test", action="store_true", help="Send test email")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    email_system = EmailIntegration()
    
    if args.configure:
        print("Email configuration (leave blank to skip):")
        smtp_server = input("SMTP Server (default: smtp.gmail.com): ").strip() or "smtp.gmail.com"
        smtp_port = input("SMTP Port (default: 587): ").strip()
        smtp_port = int(smtp_port) if smtp_port else 587
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        from_address = input("From Address: ").strip()
        
        if username and password and from_address:
            email_system.configure_email(smtp_server, smtp_port, username, password, from_address)
            print("✅ Email configuration saved")
        else:
            print("❌ Configuration skipped - missing required fields")
    
    elif args.test:
        print(f"Email enabled: {email_system.enabled}")
        print(f"SMTP Server: {email_system.email_config.get('smtp_server', 'Not configured')}")
        print(f"Recipients configured: {len(email_system._get_all_recipients())} total")
    
    elif args.send_test:
        # Send test briefing
        test_data = {
            "sprint_metrics": {"total_tasks": 105, "completed_tasks": 2, "completion_rate": 1.9},
            "sprint_health": {"status": "NEEDS_ATTENTION"},
            "today_priorities": ["Complete Phase 6 implementation", "Fix dashboard bugs"],
            "blockers": [],
            "recommendations": ["Focus on high-priority tasks"],
            "output_file": "test-briefing.md"
        }
        
        result = await email_system.send_morning_briefing(test_data)
        print(f"Test email result: {result}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
