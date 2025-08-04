

"""
Management Dashboard for Engineering Teams
Provides comprehensive dashboards for engineering teams and tech leads to monitor
code quality, technical debt, and software engineering metrics.
"""

import sqlite3
from src.infrastructure.utils.common_imports import (
    Any,
    Dict,
    Enum,
    List,
    Optional,
    Path,
    dataclass,
    datetime,
    json
)
from ..core.nfr_validator import NFRValidator
from ..core.quality_gates import QualityGatesEngine
from ..core.validator import Validator
from ..core.vv_validator import VVValidator


class MetricTrend(Enum):
    """Metric trend direction."""

    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


@dataclass
class DashboardMetric:
    """Dashboard metric with trend analysis."""

    name: str
    current_value: float
    previous_value: Optional[float]
    trend: MetricTrend
    target_value: float
    unit: str
    category: str
    priority: str  # "high", "medium", "low"


@dataclass
class TeamMetrics:
    """Team-level metrics."""

    team_name: str
    total_files: int
    total_issues: int
    technical_debt_hours: float
    code_quality_score: float
    security_score: float
    maintainability_score: float
    test_coverage: float
    last_updated: datetime


class ManagementDashboard:
    """Management dashboard for engineering teams and tech leads."""

    def __init__(self, root_path: Optional[Path] = None):
        self.root_path = root_path or Path.cwd()
        self.db_path = self.root_path / "reports" / "metrics.db"
        self.dashboard_path = self.root_path / "reports" / "dashboard"
        self.dashboard_path.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        # Initialize validators
        self.validator = Validator(root_path)
        self.unified_validator = self.validator  # Alias for backward compatibility
        self.quality_gates = QualityGatesEngine(root_path)
        self.vv_validator = VVValidator(root_path)
        self.nfr_validator = NFRValidator(root_path)

    def _init_database(self):
        """Initialize metrics database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    category TEXT NOT NULL,
                    team_name TEXT DEFAULT 'default',
                    additional_data TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS validation_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    overall_success BOOLEAN NOT NULL,
                    total_issues INTEGER NOT NULL,
                    critical_issues INTEGER NOT NULL,
                    warnings INTEGER NOT NULL,
                    duration REAL NOT NULL,
                    can_merge BOOLEAN NOT NULL,
                    report_data TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS team_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    team_name TEXT NOT NULL,
                    total_files INTEGER NOT NULL,
                    total_issues INTEGER NOT NULL,
                    technical_debt_hours REAL NOT NULL,
                    code_quality_score REAL NOT NULL,
                    security_score REAL NOT NULL,
                    maintainability_score REAL NOT NULL,
                    test_coverage REAL NOT NULL
                )
            """
            )

    def generate_management_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive management dashboard."""
        print("📊 Generating Management Dashboard...")

        # Run validation to get current metrics
        validation_report = self.unified_validator.run_validation()

        # Store metrics in database
        self._store_validation_metrics(validation_report)

        # Generate dashboard data
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "executive_summary": self._generate_executive_summary(validation_report),
            "key_metrics": self._generate_key_metrics(validation_report),
            "quality_trends": self._generate_quality_trends(),
            "team_metrics": self._generate_team_metrics(),
            "technical_debt": self._generate_technical_debt_analysis(validation_report),
            "compliance_overview": self._generate_compliance_overview(
                validation_report
            ),
            "recommendations": self._generate_management_recommendations(
                validation_report
            ),
            "alerts": self._generate_alerts(validation_report),
            "charts_data": self._generate_charts_data(),
        }

        # Save dashboard data
        self._save_dashboard_data(dashboard_data)

        # Generate HTML dashboard
        self._generate_html_dashboard(dashboard_data)

        return dashboard_data

    def _store_validation_metrics(self, validation_report: Dict[str, Any]):
        """Store validation metrics in database."""
        with sqlite3.connect(self.db_path) as conn:
            # Store validation run
            conn.execute(
                """
                INSERT INTO validation_runs 
                (overall_success, total_issues, critical_issues, warnings, duration, can_merge, report_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    validation_report["summary"]["overall_success"],
                    validation_report["summary"]["total_issues"],
                    validation_report["summary"]["critical_issues"],
                    validation_report["summary"]["warnings"],
                    validation_report["summary"]["total_duration"],
                    validation_report["summary"]["can_merge"],
                    json.dumps(validation_report),
                ),
            )

            # Store individual metrics
            metrics_to_store = [
                (
                    "test_coverage",
                    validation_report.get("phase_results", {})
                    .get("quality_gates", {})
                    .get("details", {})
                    .get("technical_debt", {})
                    .get("total_hours", 0),
                    "quality",
                ),
                (
                    "technical_debt_hours",
                    validation_report.get("phase_results", {})
                    .get("quality_gates", {})
                    .get("details", {})
                    .get("technical_debt", {})
                    .get("total_hours", 0),
                    "debt",
                ),
                (
                    "total_issues",
                    validation_report["summary"]["total_issues"],
                    "issues",
                ),
                (
                    "critical_issues",
                    validation_report["summary"]["critical_issues"],
                    "issues",
                ),
                ("warnings", validation_report["summary"]["warnings"], "issues"),
            ]

            for metric_name, value, category in metrics_to_store:
                conn.execute(
                    """
                    INSERT INTO metrics_history (metric_name, metric_value, category)
                    VALUES (?, ?, ?)
                """,
                    (metric_name, value, category),
                )

    def _generate_executive_summary(
        self, validation_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary for leadership."""
        summary = validation_report["summary"]

        # Calculate health score (0-100) - base it on coverage if available
        phase_results = validation_report.get("phase_results", {})
        quality_gates = phase_results.get("quality_gates", {}).get("details", {})
        coverage_percentage = quality_gates.get("metrics", {}).get(
            "coverage_percentage"
        )

        if coverage_percentage is not None:
            # Use coverage as base score and adjust for issues
            health_score = coverage_percentage
        else:
            # Fallback to default calculation
            health_score = 100

        if summary["critical_issues"] > 0:
            health_score -= min(summary["critical_issues"] * 20, 80)
        if summary["warnings"] > 10:
            health_score -= min((summary["warnings"] - 10) * 2, 20)

        # Determine overall status
        if health_score >= 90:
            status = "Excellent"
            status_color = "green"
        elif health_score >= 70:
            status = "Good"
            status_color = "yellow"
        elif health_score >= 50:
            status = "Needs Attention"
            status_color = "orange"
        else:
            status = "Critical"
            status_color = "red"

        return {
            "overall_health_score": health_score,
            "status": status,
            "status_color": status_color,
            "can_deploy": summary["can_merge"],
            "total_issues": summary["total_issues"],
            "critical_issues": summary["critical_issues"],
            "phases_completed": summary["phases_completed"],
            "total_duration_minutes": summary["total_duration"] / 60,
            "recommendation": self._get_executive_recommendation(health_score, summary),
        }

    def _get_executive_recommendation(
        self, health_score: float, summary: Dict[str, Any]
    ) -> str:
        """Get executive recommendation based on metrics."""
        if health_score >= 90:
            return "System is production-ready with excellent code quality."
        elif health_score >= 70:
            return "Good overall quality. Consider addressing warnings before next release."
        elif health_score >= 50:
            return "Quality issues detected. Review and address before deployment."
        else:
            return (
                "Critical issues found. Immediate attention required before deployment."
            )

    def _generate_key_metrics(
        self, validation_report: Dict[str, Any]
    ) -> List[DashboardMetric]:
        """Generate key metrics with trend analysis."""
        metrics = []

        # Get historical data for trend analysis
        historical_data = self._get_historical_metrics()

        # Define key metrics
        current_metrics = {
            "test_coverage": self._extract_metric_value(
                validation_report, "test_coverage", 0
            ),
            "technical_debt_hours": self._extract_metric_value(
                validation_report, "technical_debt_hours", 0
            ),
            "code_quality_score": 100
            - min(validation_report["summary"]["total_issues"] * 2, 100),
            "security_score": self._calculate_security_score(validation_report),
            "maintainability_score": self._calculate_maintainability_score(
                validation_report
            ),
            "critical_issues": validation_report["summary"]["critical_issues"],
        }

        # Create metrics with trends
        metric_configs = [
            ("test_coverage", "Test Coverage", "%", "quality", "high", 80.0),
            ("technical_debt_hours", "Technical Debt", "hours", "debt", "high", 10.0),
            (
                "code_quality_score",
                "Code Quality Score",
                "score",
                "quality",
                "high",
                85.0,
            ),
            ("security_score", "Security Score", "score", "security", "high", 90.0),
            (
                "maintainability_score",
                "Maintainability Score",
                "score",
                "maintainability",
                "medium",
                80.0,
            ),
            ("critical_issues", "Critical Issues", "count", "issues", "high", 0.0),
        ]

        for metric_key, name, unit, category, priority, target in metric_configs:
            current_value = current_metrics.get(metric_key, 0)
            previous_value = historical_data.get(metric_key)
            trend = self._calculate_trend(current_value, previous_value, target)

            metrics.append(
                DashboardMetric(
                    name=name,
                    current_value=current_value,
                    previous_value=previous_value,
                    trend=trend,
                    target_value=target,
                    unit=unit,
                    category=category,
                    priority=priority,
                )
            )

        return metrics

    def _extract_metric_value(
        self, validation_report: Dict[str, Any], metric_name: str, default: float
    ) -> float:
        """Extract metric value from validation report."""
        # This is a simplified extraction - in reality, you'd parse the specific report structure
        phase_results = validation_report.get("phase_results", {})

        if metric_name == "test_coverage":
            quality_gates = phase_results.get("quality_gates", {}).get("details", {})
            return quality_gates.get("metrics", {}).get("coverage_percentage", default)
        elif metric_name == "technical_debt_hours":
            return (
                phase_results.get("quality_gates", {})
                .get("details", {})
                .get("technical_debt", {})
                .get("total_hours", default)
            )

        return default

    def _calculate_security_score(self, validation_report: Dict[str, Any]) -> float:
        """Calculate security score based on validation results."""
        security_phase = validation_report.get("phase_results", {}).get(
            "security_scan", {}
        )
        if not security_phase:
            return 50.0

        security_details = security_phase.get("details", {})
        vulnerabilities = security_details.get("security_vulnerabilities", {}).get(
            "total_vulnerabilities", 0
        )
        owasp_compliance = security_details.get("owasp_compliance", {}).get(
            "compliance_percentage", 0
        )

        # Score based on vulnerabilities and OWASP compliance
        score = owasp_compliance - (vulnerabilities * 10)
        return max(0, min(100, score))

    def _calculate_maintainability_score(
        self, validation_report: Dict[str, Any]
    ) -> float:
        """Calculate maintainability score based on validation results."""
        nfr_phase = validation_report.get("phase_results", {}).get("nfr_validation", {})
        if not nfr_phase:
            return 50.0

        maintainability_metrics = nfr_phase.get("details", {}).get(
            "maintainability_metrics", {}
        )
        avg_complexity = maintainability_metrics.get("average_complexity", 10)
        duplication = maintainability_metrics.get("duplication_percentage", 10)
        doc_coverage = maintainability_metrics.get("documentation_coverage", 50)

        # Score based on complexity, duplication, and documentation
        score = doc_coverage - (avg_complexity * 2) - (duplication * 3)
        return max(0, min(100, score))

    def _get_historical_metrics(self) -> Dict[str, float]:
        """Get historical metrics for trend analysis."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT metric_name, metric_value
                FROM metrics_history
                WHERE timestamp > datetime('now', '-7 days')
                ORDER BY timestamp DESC
                LIMIT 20
            """
            )

            historical = {}
            for row in cursor:
                metric_name, value = row
                if metric_name not in historical:
                    historical[metric_name] = value

            return historical

    def _calculate_trend(
        self, current: float, previous: Optional[float], target: float
    ) -> MetricTrend:
        """Calculate trend direction."""
        if previous is None:
            return MetricTrend.STABLE

        change = current - previous

        # For metrics where higher is better (coverage, scores)
        if target > 50:
            if change > 0.5:
                return MetricTrend.IMPROVING
            elif change < -0.5:
                return MetricTrend.DECLINING
        else:
            # For metrics where lower is better (issues, debt)
            if change < -0.5:
                return MetricTrend.IMPROVING
            elif change > 0.5:
                return MetricTrend.DECLINING

        return MetricTrend.STABLE

    def _generate_quality_trends(self) -> Dict[str, Any]:
        """Generate quality trends over time."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT DATE(timestamp) as date, 
                       AVG(total_issues) as avg_issues,
                       AVG(critical_issues) as avg_critical,
                       AVG(warnings) as avg_warnings
                FROM validation_runs
                WHERE timestamp > datetime('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            """
            )

            trends = []
            for row in cursor:
                date, avg_issues, avg_critical, avg_warnings = row
                trends.append(
                    {
                        "date": date,
                        "total_issues": avg_issues,
                        "critical_issues": avg_critical,
                        "warnings": avg_warnings,
                    }
                )

            return {
                "data": trends,
                "period": "30 days",
                "trend_direction": self._calculate_overall_trend(trends),
            }

    def _calculate_overall_trend(self, trends: List[Dict[str, Any]]) -> str:
        """Calculate overall trend direction."""
        if len(trends) < 2:
            return "stable"

        first_week = trends[:7]
        last_week = trends[-7:]

        first_avg = sum(t["total_issues"] for t in first_week) / len(first_week)
        last_avg = sum(t["total_issues"] for t in last_week) / len(last_week)

        if last_avg < first_avg * 0.9:
            return "improving"
        elif last_avg > first_avg * 1.1:
            return "declining"
        else:
            return "stable"

    def _generate_team_metrics(self) -> List[TeamMetrics]:
        """Generate team-level metrics."""
        # For now, return a single team - in practice, you'd analyze by team/module
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM team_metrics
                ORDER BY timestamp DESC
                LIMIT 1
            """
            )

            row = cursor.fetchone()
            if row:
                return [
                    TeamMetrics(
                        team_name=row[2],
                        total_files=row[3],
                        total_issues=row[4],
                        technical_debt_hours=row[5],
                        code_quality_score=row[6],
                        security_score=row[7],
                        maintainability_score=row[8],
                        test_coverage=row[9],
                        last_updated=datetime.fromisoformat(row[1]),
                    )
                ]

            return []

    def _generate_technical_debt_analysis(
        self, validation_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate technical debt analysis."""
        tech_debt = (
            validation_report.get("phase_results", {})
            .get("quality_gates", {})
            .get("details", {})
            .get("technical_debt", {})
        )

        return {
            "total_hours": tech_debt.get("total_hours", 0),
            "total_days": tech_debt.get("total_days", 0),
            "breakdown": {
                "bugs": tech_debt.get("bugs", 0),
                "vulnerabilities": tech_debt.get("vulnerabilities", 0),
                "code_smells": tech_debt.get("code_smells", 0),
                "security_hotspots": tech_debt.get("security_hotspots", 0),
            },
            "priority_actions": self._generate_debt_priority_actions(tech_debt),
        }

    def _generate_debt_priority_actions(self, tech_debt: Dict[str, Any]) -> List[str]:
        """Generate priority actions for technical debt."""
        actions = []

        if tech_debt.get("vulnerabilities", 0) > 0:
            actions.append(
                f"🔒 Fix {tech_debt['vulnerabilities']} security vulnerabilities (HIGH PRIORITY)"
            )

        if tech_debt.get("bugs", 0) > 0:
            actions.append(f"🐛 Fix {tech_debt['bugs']} bugs")

        if tech_debt.get("code_smells", 0) > 10:
            actions.append(f"🧹 Address {tech_debt['code_smells']} code smells")

        if tech_debt.get("total_hours", 0) > 40:
            actions.append("⏰ Schedule technical debt sprint (>40 hours debt)")

        return actions

    def _generate_compliance_overview(
        self, validation_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate compliance overview."""
        compliance = validation_report.get("compliance_assessment", {})

        return {
            "iso_25010_compliant": compliance.get("iso_25010_compliant", False),
            "ready_for_production": compliance.get("ready_for_production", False),
            "overall_compliance_percentage": compliance.get(
                "overall_compliance_percentage", 0
            ),
            "principles_compliance": compliance.get("principles", {}),
            "recommendations": [
                "Implement automated quality gates",
                "Increase test coverage to 80%+",
                "Address security vulnerabilities",
                "Reduce technical debt below 20 hours",
            ],
        }

    def _generate_management_recommendations(
        self, validation_report: Dict[str, Any]
    ) -> List[str]:
        """Generate management-level recommendations."""
        recommendations = []
        summary = validation_report["summary"]

        # Calculate health score for excellent quality detection
        health_score = self._calculate_overall_health_score(validation_report)

        # Positive recommendations for excellent quality
        if health_score >= 90 and summary["critical_issues"] == 0:
            recommendations.append(
                "🌟 EXCELLENT: Code quality meets highest standards - continue current practices"
            )
            recommendations.append(
                "✅ DEPLOYMENT READY: All quality gates passed - system ready for production"
            )

        # Executive recommendations
        if summary["critical_issues"] > 0:
            recommendations.append(
                f"⚠️ EXECUTIVE ACTION REQUIRED: {summary['critical_issues']} critical issues blocking deployment"
            )

        if not summary["can_merge"]:
            recommendations.append(
                "🚫 DEPLOYMENT BLOCKED: Quality gates failed - review required"
            )

        # Process recommendations
        if summary["total_duration"] > 300:  # 5 minutes
            recommendations.append(
                "⏱️ PROCESS: Validation taking too long - consider optimization"
            )

        # Team recommendations
        if summary["warnings"] > 20:
            recommendations.append(
                "👥 TEAM: High warning count - schedule code quality review"
            )

        return recommendations

    def _calculate_overall_health_score(
        self, validation_report: Dict[str, Any]
    ) -> float:
        """Calculate overall health score using same logic as executive summary."""
        summary = validation_report["summary"]

        # Calculate health score (0-100) - base it on coverage if available
        phase_results = validation_report.get("phase_results", {})
        quality_gates = phase_results.get("quality_gates", {}).get("details", {})
        coverage_percentage = quality_gates.get("metrics", {}).get(
            "coverage_percentage"
        )

        if coverage_percentage is not None:
            # Use coverage as base score and adjust for issues
            health_score = coverage_percentage
        else:
            # Fallback to default calculation
            health_score = 100

        if summary["critical_issues"] > 0:
            health_score -= min(summary["critical_issues"] * 20, 80)
        if summary["warnings"] > 10:
            health_score -= min((summary["warnings"] - 10) * 2, 20)

        return health_score

    def _generate_alerts(
        self, validation_report: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate alerts for management attention."""
        alerts = []
        summary = validation_report["summary"]

        # Critical alerts
        if summary["critical_issues"] > 0:
            alerts.append(
                {
                    "level": "critical",
                    "message": f"{summary['critical_issues']} critical issues found",
                    "action": "Immediate review required",
                    "impact": "Deployment blocked",
                }
            )

        # High priority alerts
        if not summary["can_merge"]:
            alerts.append(
                {
                    "level": "high",
                    "message": "Quality gates failed",
                    "action": "Review quality standards",
                    "impact": "Cannot merge to main branch",
                }
            )

        # Medium priority alerts
        if summary["warnings"] > 15:
            alerts.append(
                {
                    "level": "medium",
                    "message": f"{summary['warnings']} warnings detected",
                    "action": "Schedule code review",
                    "impact": "Technical debt increasing",
                }
            )

        return alerts

    def _generate_charts_data(self) -> Dict[str, Any]:
        """Generate data for dashboard charts."""
        with sqlite3.connect(self.db_path) as conn:
            # Issues over time
            cursor = conn.execute(
                """
                SELECT DATE(timestamp) as date,
                       AVG(total_issues) as issues,
                       AVG(critical_issues) as critical,
                       AVG(warnings) as warnings
                FROM validation_runs
                WHERE timestamp > datetime('now', '-14 days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            """
            )

            issues_over_time = []
            for row in cursor:
                issues_over_time.append(
                    {
                        "date": row[0],
                        "total_issues": row[1],
                        "critical_issues": row[2],
                        "warnings": row[3],
                    }
                )

            # Quality distribution
            cursor = conn.execute(
                """
                SELECT 
                    SUM(CASE WHEN critical_issues = 0 THEN 1 ELSE 0 END) as healthy,
                    SUM(CASE WHEN critical_issues > 0 AND critical_issues <= 5 THEN 1 ELSE 0 END) as warning,
                    SUM(CASE WHEN critical_issues > 5 THEN 1 ELSE 0 END) as critical
                FROM validation_runs
                WHERE timestamp > datetime('now', '-7 days')
            """
            )

            quality_distribution = cursor.fetchone()

            return {
                "issues_over_time": issues_over_time,
                "quality_distribution": {
                    "healthy": quality_distribution[0] or 0,
                    "warning": quality_distribution[1] or 0,
                    "critical": quality_distribution[2] or 0,
                },
            }

    def _save_dashboard_data(self, dashboard_data: Dict[str, Any]):
        """Save dashboard data to JSON file."""
        dashboard_file = self.dashboard_path / "dashboard_data.json"

        with open(dashboard_file, "w", encoding="utf-8") as f:
            json.dump(dashboard_data, f, indent=2, default=str)

    def _generate_html_dashboard(self, dashboard_data: Dict[str, Any]):
        """Generate HTML dashboard for web viewing."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Code Quality Management Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .metric-card {{ background: white; padding: 20px; margin: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
        .metric-trend {{ font-size: 0.9em; margin-top: 5px; }}
        .trend-improving {{ color: #27ae60; }}
        .trend-declining {{ color: #e74c3c; }}
        .trend-stable {{ color: #95a5a6; }}
        .alert {{ padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .alert-critical {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .alert-high {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
        .alert-medium {{ background: #cff4fc; color: #055160; border: 1px solid #99eefc; }}
        .health-score {{ font-size: 3em; font-weight: bold; text-align: center; }}
        .health-excellent {{ color: #27ae60; }}
        .health-good {{ color: #f1c40f; }}
        .health-warning {{ color: #e67e22; }}
        .health-critical {{ color: #e74c3c; }}
        .recommendations {{ background: #e8f5e8; padding: 15px; border-radius: 4px; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🏗️ Code Quality Management Dashboard</h1>
            <p>Engineering Team Dashboard - Real-time Quality Metrics</p>
            <p class="timestamp">Last updated: {dashboard_data['timestamp']}</p>
        </div>
        
        <div class="metric-card">
            <h2>📊 Executive Summary</h2>
            <div class="health-score health-{dashboard_data['executive_summary']['status'].lower()}">
                {dashboard_data['executive_summary']['overall_health_score']:.0f}%
            </div>
            <p><strong>Status:</strong> {dashboard_data['executive_summary']['status']}</p>
            <p><strong>Deployment Status:</strong> {'✅ Ready' if dashboard_data['executive_summary']['can_deploy'] else '❌ Blocked'}</p>
            <p><strong>Recommendation:</strong> {dashboard_data['executive_summary']['recommendation']}</p>
        </div>
        
        <div class="metric-grid">
            {self._generate_metric_cards_html(dashboard_data['key_metrics'])}
        </div>
        
        <div class="metric-card">
            <h2>🚨 Alerts</h2>
            {self._generate_alerts_html(dashboard_data['alerts'])}
        </div>
        
        <div class="metric-card">
            <h2>💰 Technical Debt Analysis</h2>
            <p><strong>Total Debt:</strong> {dashboard_data['technical_debt']['total_hours']:.1f} hours ({dashboard_data['technical_debt']['total_days']:.1f} days)</p>
            <div class="recommendations">
                <h3>Priority Actions:</h3>
                <ul>
                    {self._generate_list_html(dashboard_data['technical_debt']['priority_actions'])}
                </ul>
            </div>
        </div>
        
        <div class="metric-card">
            <h2>📋 Management Recommendations</h2>
            <div class="recommendations">
                <ul>
                    {self._generate_list_html(dashboard_data['recommendations'])}
                </ul>
            </div>
        </div>
        
        <div class="metric-card">
            <h2>📈 Quality Trends</h2>
            <p><strong>Period:</strong> {dashboard_data['quality_trends']['period']}</p>
            <p><strong>Trend:</strong> {dashboard_data['quality_trends']['trend_direction'].title()}</p>
            <p><em>Chart visualization would be implemented with a JavaScript charting library</em></p>
        </div>
        
        <div class="metric-card">
            <h2>✅ Compliance Overview</h2>
            <p><strong>ISO/IEC 25010 Compliant:</strong> {'✅ Yes' if dashboard_data['compliance_overview']['iso_25010_compliant'] else '❌ No'}</p>
            <p><strong>Production Ready:</strong> {'✅ Yes' if dashboard_data['compliance_overview']['ready_for_production'] else '❌ No'}</p>
            <p><strong>Overall Compliance:</strong> {dashboard_data['compliance_overview']['overall_compliance_percentage']:.1f}%</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 minutes
        setTimeout(() => location.reload(), 300000);
    </script>
</body>
</html>
"""

        html_file = self.dashboard_path / "index.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"📊 Management dashboard generated: {html_file}")

    def _generate_metric_cards_html(self, metrics: List[DashboardMetric]) -> str:
        """Generate HTML for metric cards."""
        html = ""
        for metric in metrics:
            trend_class = f"trend-{metric.trend.value}"
            trend_icon = (
                "📈"
                if metric.trend == MetricTrend.IMPROVING
                else "📉" if metric.trend == MetricTrend.DECLINING else "➡️"
            )

            # Format value based on unit type
            if metric.unit == "%" and metric.current_value == int(metric.current_value):
                value_display = f"{int(metric.current_value)}{metric.unit}"
            else:
                value_display = f"{metric.current_value:.1f} {metric.unit}"

            html += f"""
            <div class="metric-card">
                <h3>{metric.name}</h3>
                <div class="metric-value">{value_display}</div>
                <div class="metric-trend {trend_class}">{trend_icon} {metric.trend.value.title()}</div>
                <p><small>Target: {metric.target_value} {metric.unit}</small></p>
            </div>
            """

        return html

    def _generate_alerts_html(self, alerts: List[Dict[str, Any]]) -> str:
        """Generate HTML for alerts."""
        if not alerts:
            return "<p>✅ No alerts - all systems healthy</p>"

        html = ""
        for alert in alerts:
            html += f"""
            <div class="alert alert-{alert['level']}">
                <strong>{alert['message']}</strong><br>
                <small>Action: {alert['action']} | Impact: {alert['impact']}</small>
            </div>
            """

        return html

    def _generate_list_html(self, items: List[str]) -> str:
        """Generate HTML list items."""
        return "".join(f"<li>{item}</li>" for item in items)

    def get_dashboard_url(self) -> str:
        """Get the URL to access the dashboard."""
        return f"file://{self.dashboard_path / 'index.html'}"
