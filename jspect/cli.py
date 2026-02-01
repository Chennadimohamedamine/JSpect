"""
Command-line interface for JSpect.
"""

import click
import os
import json
import sys
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()

# Import JSpect modules
try:
    from jspect.core.scanner import JavaScriptScanner
    from jspect.detectors.patterns import SecretPatterns
    from jspect.ai.manager import AIManager
except ImportError:
    from core.scanner import JavaScriptScanner
    from detectors.patterns import SecretPatterns
    from ai.manager import AIManager

console = Console()


class JSpectCLI:
    """JSpect command-line interface handler."""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize CLI."""
        self.config = self._load_config(config_path)
        self.scanner = JavaScriptScanner(config_path)
        self.patterns = SecretPatterns()
        self.ai_manager = None
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration."""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            return {}
        except Exception as e:
            console.print(f"[yellow]Warning: Could not load config: {e}[/yellow]")
            return {}
    
    def _init_ai(self, provider: str) -> bool:
        """Initialize AI manager."""
        try:
            self.ai_manager = AIManager()
            available = self.ai_manager.get_available_providers()
            
            if not available:
                console.print("[yellow]Warning: No AI providers available[/yellow]")
                return False
            
            return True
        except Exception as e:
            console.print(f"[red]Error initializing AI: {e}[/red]")
            return False
    
    def scan(
        self,
        source: str,
        source_type: str = 'url',
        ai_provider: Optional[str] = None,
        output_format: str = 'cli',
        output_file: Optional[str] = None,
        severity_filter: Optional[str] = None,
        type_filter: Optional[str] = None
    ):
        """
        Execute a scan.
        
        Args:
            source: URL, file path, or code to scan
            source_type: Type of source
            ai_provider: AI provider to use (None, 'claude', 'gemini', 'both')
            output_format: Output format
            output_file: Output file path
            severity_filter: Comma-separated severity levels to include
            type_filter: Comma-separated secret types to include
        """
        # Print header
        self._print_header()
        
        # Scan for JavaScript
        console.print(f"\n[cyan]📁 Scanning: {source}[/cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Fetching JavaScript...", total=None)
            
            try:
                # Fetch and analyze JavaScript
                if source_type == 'url':
                    code = self.scanner.fetch_from_url(source)
                elif source_type == 'file':
                    code = self.scanner.fetch_from_file(source)
                elif source_type == 'code':
                    code = source
                else:
                    raise ValueError(f"Unknown source type: {source_type}")
                
                progress.update(task, description="Analyzing code...")
                
                # Detect secrets
                findings = self.patterns.detect_secrets(code)
                
                progress.update(task, description=f"Found {len(findings)} potential secrets...")
                
                # Apply AI analysis if requested
                if ai_provider and findings:
                    if not self.ai_manager:
                        self._init_ai(ai_provider)
                    
                    if self.ai_manager:
                        progress.update(task, description=f"Running AI analysis ({ai_provider})...")
                        findings = self.ai_manager.analyze_batch(
                            findings,
                            code,
                            provider=ai_provider
                        )
                
                progress.update(task, description="Complete!", completed=True)
            
            except Exception as e:
                console.print(f"[red]Error during scan: {e}[/red]")
                return
        
        # Filter results
        findings = self._filter_findings(findings, severity_filter, type_filter)
        
        # Output results
        if output_format == 'cli':
            self._print_results(findings, ai_provider)
        elif output_format == 'json':
            self._output_json(findings, output_file)
        elif output_format == 'html':
            self._output_html(findings, output_file)
        elif output_format == 'markdown':
            self._output_markdown(findings, output_file)
        elif output_format == 'csv':
            self._output_csv(findings, output_file)
        else:
            console.print(f"[red]Unknown output format: {output_format}[/red]")
    
    def _filter_findings(self, findings, severity_filter, type_filter):
        """Filter findings based on criteria."""
        if not findings:
            return findings
        
        # Filter by severity
        if severity_filter:
            severities = [s.strip().lower() for s in severity_filter.split(',')]
            findings = [
                f for f in findings
                if f.get('severity', '').lower() in severities
            ]
        
        # Filter by type
        if type_filter:
            types = [t.strip().lower() for t in type_filter.split(',')]
            findings = [
                f for f in findings
                if f.get('type', '').lower() in types
            ]
        
        return findings
    
    def _print_header(self):
        """Print CLI header."""
        header = """
[bold cyan]🔍 JSpect - JavaScript Secret Scanner[/bold cyan]
[dim]AI-Powered Security Analysis Tool[/dim]
"""
        console.print(Panel(header, box=box.DOUBLE, border_style="cyan"))
    
    def _print_results(self, findings, ai_provider):
        """Print results to console."""
        if not findings:
            console.print("\n[green]✓ No secrets found![/green]\n")
            return
        
        # Group by severity
        by_severity = {
            'Critical': [],
            'High': [],
            'Medium': [],
            'Low': [],
            'Unknown': []
        }
        
        for finding in findings:
            severity = finding.get('severity', 'Unknown')
            by_severity[severity].append(finding)
        
        # Print findings by severity
        severity_colors = {
            'Critical': 'red',
            'High': 'orange1',
            'Medium': 'yellow',
            'Low': 'blue',
            'Unknown': 'white'
        }
        
        severity_icons = {
            'Critical': '🚨',
            'High': '⚠️',
            'Medium': '⚡',
            'Low': 'ℹ️',
            'Unknown': '❓'
        }
        
        for severity in ['Critical', 'High', 'Medium', 'Low', 'Unknown']:
            severity_findings = by_severity[severity]
            if not severity_findings:
                continue
            
            console.print(f"\n[bold {severity_colors[severity]}]" + "━" * 60 + "[/]")
            console.print(f"[bold {severity_colors[severity]}]{severity_icons[severity]} {severity.upper()} - {len(severity_findings)} finding(s)[/]")
            console.print(f"[bold {severity_colors[severity]}]" + "━" * 60 + "[/]\n")
            
            for i, finding in enumerate(severity_findings, 1):
                self._print_finding(finding, severity_colors[severity])
        
        # Print summary
        self._print_summary(findings, ai_provider)
    
    def _print_finding(self, finding, color):
        """Print a single finding."""
        table = Table(show_header=False, box=box.SIMPLE, border_style=color)
        
        # Type and description
        table.add_row(
            "[bold]Type:[/bold]",
            f"{finding.get('description', finding.get('type', 'Unknown'))}"
        )
        
        # Masked value
        masked = self.patterns.mask_secret(finding.get('value', ''))
        table.add_row("[bold]Value:[/bold]", f"[dim]{masked}[/dim]")
        
        # Location
        table.add_row(
            "[bold]Location:[/bold]",
            f"Line {finding.get('line_number', 'N/A')}"
        )
        
        # Context
        if finding.get('line_content'):
            table.add_row(
                "[bold]Context:[/bold]",
                f"[dim]{finding.get('line_content', '')[:80]}[/dim]"
            )
        
        # AI analysis
        if finding.get('ai_analysis'):
            confidence = finding.get('confidence_score', 0)
            table.add_row(
                "[bold]Confidence:[/bold]",
                f"{confidence}% (AI Verified)"
            )
            
            if finding.get('remediation'):
                table.add_row(
                    "[bold]Remediation:[/bold]",
                    finding.get('remediation', '')[:100]
                )
        
        console.print(table)
        console.print()
    
    def _print_summary(self, findings, ai_provider):
        """Print summary statistics."""
        console.print("\n[bold cyan]" + "━" * 60 + "[/]")
        console.print("[bold cyan]📊 Summary[/bold cyan]")
        console.print("[bold cyan]" + "━" * 60 + "[/]\n")
        
        # Count by severity
        by_severity = {}
        for finding in findings:
            severity = finding.get('severity', 'Unknown')
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        summary_parts = []
        severity_order = ['Critical', 'High', 'Medium', 'Low']
        
        for severity in severity_order:
            count = by_severity.get(severity, 0)
            if count > 0:
                summary_parts.append(f"{severity}: {count}")
        
        console.print(" | ".join(summary_parts))
        console.print(f"[bold]Total Secrets Found: {len(findings)}[/bold]")
        
        if ai_provider:
            console.print(f"[dim]AI Analysis: {ai_provider}[/dim]")
        
        console.print()
    
    def _output_json(self, findings, output_file):
        """Output results as JSON."""
        output = {
            'tool': 'JSpect',
            'version': '1.0.0',
            'findings': findings,
            'summary': {
                'total': len(findings),
                'by_severity': self._count_by_severity(findings)
            }
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)
            console.print(f"[green]✓ Results saved to {output_file}[/green]")
        else:
            print(json.dumps(output, indent=2))
    
    def _output_html(self, findings, output_file):
        """Output results as HTML."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>JSpect Scan Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #1e3a8a; color: white; padding: 20px; }}
        .finding {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
        .critical {{ border-left: 5px solid #dc2626; }}
        .high {{ border-left: 5px solid #ea580c; }}
        .medium {{ border-left: 5px solid #fbbf24; }}
        .low {{ border-left: 5px solid #3b82f6; }}
        .secret {{ background: #f3f4f6; padding: 5px; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 JSpect Scan Results</h1>
        <p>Total findings: {len(findings)}</p>
    </div>
"""
        
        for finding in findings:
            severity = finding.get('severity', 'Unknown').lower()
            masked = self.patterns.mask_secret(finding.get('value', ''))
            
            html += f"""
    <div class="finding {severity}">
        <h3>{finding.get('description', 'Unknown Secret')}</h3>
        <p><strong>Severity:</strong> {finding.get('severity', 'Unknown')}</p>
        <p><strong>Value:</strong> <span class="secret">{masked}</span></p>
        <p><strong>Line:</strong> {finding.get('line_number', 'N/A')}</p>
        <p><strong>Context:</strong> <code>{finding.get('line_content', '')}</code></p>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(html)
            console.print(f"[green]✓ Results saved to {output_file}[/green]")
        else:
            print(html)
    
    def _output_markdown(self, findings, output_file):
        """Output results as Markdown."""
        md = f"""# JSpect Scan Results

Total findings: {len(findings)}

---

"""
        
        for finding in findings:
            masked = self.patterns.mask_secret(finding.get('value', ''))
            md += f"""## {finding.get('description', 'Unknown Secret')}

- **Severity:** {finding.get('severity', 'Unknown')}
- **Type:** {finding.get('type', 'Unknown')}
- **Value:** `{masked}`
- **Line:** {finding.get('line_number', 'N/A')}
- **Context:** `{finding.get('line_content', '')}`

"""
            
            if finding.get('remediation'):
                md += f"**Remediation:** {finding.get('remediation', '')}\n\n"
            
            md += "---\n\n"
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(md)
            console.print(f"[green]✓ Results saved to {output_file}[/green]")
        else:
            print(md)
    
    def _output_csv(self, findings, output_file):
        """Output results as CSV."""
        import csv
        from io import StringIO
        
        output = StringIO() if not output_file else open(output_file, 'w', newline='')
        
        writer = csv.DictWriter(
            output,
            fieldnames=['severity', 'type', 'description', 'value', 'line_number', 'confidence']
        )
        writer.writeheader()
        
        for finding in findings:
            writer.writerow({
                'severity': finding.get('severity', 'Unknown'),
                'type': finding.get('type', 'Unknown'),
                'description': finding.get('description', ''),
                'value': self.patterns.mask_secret(finding.get('value', '')),
                'line_number': finding.get('line_number', ''),
                'confidence': finding.get('confidence_score', '')
            })
        
        if output_file:
            output.close()
            console.print(f"[green]✓ Results saved to {output_file}[/green]")
        else:
            print(output.getvalue())
    
    def _count_by_severity(self, findings):
        """Count findings by severity."""
        counts = {}
        for finding in findings:
            severity = finding.get('severity', 'Unknown')
            counts[severity] = counts.get(severity, 0) + 1
        return counts


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """JSpect - AI-Powered JavaScript Secret Scanner"""
    pass


@cli.command()
@click.argument('source')
@click.option('-f', '--file', 'is_file', is_flag=True, help='Treat source as file path')
@click.option('--code', is_flag=True, help='Treat source as direct code input')
@click.option('--ai', type=click.Choice(['claude', 'gemini', 'both']), help='Enable AI analysis')
@click.option('-o', '--output', help='Output file path')
@click.option('--format', type=click.Choice(['cli', 'json', 'html', 'markdown', 'csv']), default='cli', help='Output format')
@click.option('--severity', help='Filter by severity (comma-separated)')
@click.option('--type', 'type_filter', help='Filter by type (comma-separated)')
def scan(source, is_file, code, ai, output, format, severity, type_filter):
    """Scan JavaScript for secrets"""
    
    jspect = JSpectCLI()
    
    # Determine source type
    if code:
        source_type = 'code'
    elif is_file:
        source_type = 'file'
    else:
        source_type = 'url'
    
    try:
        jspect.scan(
            source=source,
            source_type=source_type,
            ai_provider=ai,
            output_format=format,
            output_file=output,
            severity_filter=severity,
            type_filter=type_filter
        )
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
def test():
    """Test AI provider connections"""
    console.print("[cyan]Testing AI providers...[/cyan]\n")
    
    try:
        manager = AIManager()
        status = manager.test_providers()
        
        for provider, is_available in status.items():
            if is_available:
                console.print(f"[green]✓ {provider.capitalize()}: Connected[/green]")
            else:
                console.print(f"[red]✗ {provider.capitalize()}: Not available[/red]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == '__main__':
    cli()
