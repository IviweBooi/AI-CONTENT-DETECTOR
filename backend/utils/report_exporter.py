#!/usr/bin/env python3
"""
Report Export System with Open-Closed Principle (OCP) Design

This module provides a flexible report export system that can be easily extended
to support new export formats without modifying existing code.
"""

import json
import csv
import io
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from dataclasses import dataclass

# Try to import PDF generation library
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available. PDF export will be disabled.")

@dataclass
class ReportData:
    """Data structure for report content."""
    title: str
    timestamp: datetime
    analysis_results: Dict[str, Any]
    text_content: str
    summary: Dict[str, Any]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ReportExporter(ABC):
    """Abstract base class for report exporters following OCP."""
    
    @abstractmethod
    def export(self, report_data: ReportData) -> bytes:
        """Export report data to specific format.
        
        Args:
            report_data: The report data to export
            
        Returns:
            bytes: The exported report as bytes
        """
        pass
    
    @abstractmethod
    def get_content_type(self) -> str:
        """Get the MIME content type for this export format."""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the file extension for this export format."""
        pass

class PDFReportExporter(ReportExporter):
    """PDF report exporter using ReportLab."""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF export. Install with: pip install reportlab")
        self.logger = logging.getLogger(__name__)
    
    def export(self, report_data: ReportData) -> bytes:
        """Export report as PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Build content
        content = []
        
        # Title
        content.append(Paragraph(report_data.title, title_style))
        content.append(Spacer(1, 20))
        
        # Timestamp
        content.append(Paragraph(f"<b>Generated:</b> {report_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        content.append(Spacer(1, 20))
        
        # Analysis Summary
        content.append(Paragraph("<b>Analysis Summary</b>", styles['Heading2']))
        summary_data = [
            ['Metric', 'Value'],
            ['AI Probability', f"{report_data.analysis_results.get('ai_probability', 0):.1%}"],
            ['Human Probability', f"{report_data.analysis_results.get('human_probability', 0):.1%}"],
            ['Confidence', f"{report_data.analysis_results.get('confidence', 0):.1%}"],
            ['Classification', report_data.analysis_results.get('classification', 'Analysis Pending')],
            ['Risk Level', report_data.analysis_results.get('risk_level', 'Not Assessed')]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(summary_table)
        content.append(Spacer(1, 20))
        
        # Confidence Indicators
        if 'confidence_indicators' in report_data.analysis_results:
            content.append(Paragraph("<b>Confidence Indicators</b>", styles['Heading2']))
            for indicator in report_data.analysis_results['confidence_indicators']:
                content.append(Paragraph(f"• {indicator}", styles['Normal']))
            content.append(Spacer(1, 20))
        
        # Feedback Messages
        if 'feedback_messages' in report_data.analysis_results:
            content.append(Paragraph("<b>Feedback Messages</b>", styles['Heading2']))
            for message in report_data.analysis_results['feedback_messages']:
                content.append(Paragraph(f"• {message}", styles['Normal']))
            content.append(Spacer(1, 20))
        
        # Individual Model Results
        if 'individual_results' in report_data.analysis_results:
            content.append(Paragraph("<b>Individual Model Results</b>", styles['Heading2']))
            individual_data = [['Model', 'Probability', 'Confidence']]
            
            for model_name, results in report_data.analysis_results['individual_results'].items():
                if results.get('probability') is not None:
                    individual_data.append([
                        model_name.replace('_', ' ').title(),
                        f"{results['probability']:.1%}",
                        f"{results.get('confidence', 0):.1%}"
                    ])
            
            if len(individual_data) > 1:
                individual_table = Table(individual_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
                individual_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                content.append(individual_table)
                content.append(Spacer(1, 20))
        
        # Text Content (truncated if too long)
        content.append(Paragraph("<b>Analyzed Text</b>", styles['Heading2']))
        text_preview = report_data.text_content[:1000] + "..." if len(report_data.text_content) > 1000 else report_data.text_content
        content.append(Paragraph(text_preview, styles['Normal']))
        
        # Build PDF
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()
    
    def get_content_type(self) -> str:
        return "application/pdf"
    
    def get_file_extension(self) -> str:
        return ".pdf"

class JSONReportExporter(ReportExporter):
    """JSON report exporter."""
    
    def export(self, report_data: ReportData) -> bytes:
        """Export report as JSON."""
        report_dict = {
            'title': report_data.title,
            'timestamp': report_data.timestamp.isoformat(),
            'analysis_results': report_data.analysis_results,
            'text_content': report_data.text_content,
            'summary': report_data.summary,
            'metadata': report_data.metadata
        }
        
        json_str = json.dumps(report_dict, indent=2, ensure_ascii=False)
        return json_str.encode('utf-8')
    
    def get_content_type(self) -> str:
        return "application/json"
    
    def get_file_extension(self) -> str:
        return ".json"

class CSVReportExporter(ReportExporter):
    """CSV report exporter for tabular data."""
    
    def export(self, report_data: ReportData) -> bytes:
        """Export report as CSV."""
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        # Write header
        writer.writerow(['Report Title', report_data.title])
        writer.writerow(['Generated', report_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])  # Empty row
        
        # Write analysis results
        writer.writerow(['Analysis Results'])
        writer.writerow(['Metric', 'Value'])
        
        for key, value in report_data.analysis_results.items():
            if isinstance(value, (str, int, float)):
                writer.writerow([key.replace('_', ' ').title(), value])
            elif isinstance(value, list) and key == 'confidence_indicators':
                writer.writerow([key.replace('_', ' ').title(), '; '.join(value)])
        
        writer.writerow([])  # Empty row
        
        # Write text content (truncated)
        writer.writerow(['Analyzed Text'])
        text_preview = report_data.text_content[:500] + "..." if len(report_data.text_content) > 500 else report_data.text_content
        writer.writerow([text_preview])
        
        csv_content = buffer.getvalue()
        buffer.close()
        return csv_content.encode('utf-8')
    
    def get_content_type(self) -> str:
        return "text/csv"
    
    def get_file_extension(self) -> str:
        return ".csv"

class ReportExportManager:
    """Manager class for handling different export formats."""
    
    def __init__(self):
        self.exporters: Dict[str, ReportExporter] = {}
        self.logger = logging.getLogger(__name__)
        
        # Register default exporters
        self._register_default_exporters()
    
    def _register_default_exporters(self):
        """Register default export formats."""
        try:
            self.register_exporter('pdf', PDFReportExporter())
        except ImportError:
            self.logger.warning("PDF exporter not available")
        
        self.register_exporter('json', JSONReportExporter())
        self.register_exporter('csv', CSVReportExporter())
    
    def register_exporter(self, format_name: str, exporter: ReportExporter):
        """Register a new export format.
        
        Args:
            format_name: Name of the format (e.g., 'pdf', 'json')
            exporter: ReportExporter instance
        """
        self.exporters[format_name.lower()] = exporter
        self.logger.info(f"Registered exporter for format: {format_name}")
    
    def get_available_formats(self) -> List[str]:
        """Get list of available export formats."""
        return list(self.exporters.keys())
    
    def export_report(self, report_data: ReportData, format_name: str) -> tuple[bytes, str, str]:
        """Export report in specified format.
        
        Args:
            report_data: The report data to export
            format_name: Export format name
            
        Returns:
            tuple: (exported_data, content_type, file_extension)
            
        Raises:
            ValueError: If format is not supported
        """
        format_name = format_name.lower()
        
        if format_name not in self.exporters:
            raise ValueError(f"Unsupported export format: {format_name}. Available formats: {self.get_available_formats()}")
        
        exporter = self.exporters[format_name]
        
        try:
            exported_data = exporter.export(report_data)
            content_type = exporter.get_content_type()
            file_extension = exporter.get_file_extension()
            
            self.logger.info(f"Successfully exported report in {format_name} format")
            return exported_data, content_type, file_extension
            
        except Exception as e:
            self.logger.error(f"Failed to export report in {format_name} format: {str(e)}")
            raise

def create_report_from_analysis(analysis_results: Dict[str, Any], text_content: str, 
                              title: str = "AI Content Detection Report") -> ReportData:
    """Create a ReportData object from analysis results.
    
    Args:
        analysis_results: Results from AI detection analysis
        text_content: The original text that was analyzed
        title: Report title
        
    Returns:
        ReportData: Structured report data
    """
    summary = {
        'ai_probability': analysis_results.get('ai_probability', 0),
        'confidence': analysis_results.get('confidence', 0),
        'classification': analysis_results.get('classification', 'Analysis Pending'),
        'risk_level': analysis_results.get('risk_level', 'Not Assessed')
    }
    
    metadata = {
        'text_length': len(text_content),
        'model_version': analysis_results.get('model_version', 'Current Version')
    }
    
    return ReportData(
        title=title,
        timestamp=datetime.now(),
        analysis_results=analysis_results,
        text_content=text_content,
        summary=summary,
        metadata=metadata
    )

# Global export manager instance
export_manager = ReportExportManager()

if __name__ == "__main__":
    # Example usage
    sample_analysis = {
        'ai_probability': 0.85,
        'human_probability': 0.15,
        'confidence': 0.92,
        'classification': 'Highly Likely AI-Generated',
        'risk_level': 'High',
        'detection_method': 'ensemble',
        'confidence_indicators': [
            '🎯 High confidence in detection results',
            '🤖 Very strong AI indicators detected'
        ],
        'feedback_messages': [
            'Strong AI patterns detected',
            'High confidence in classification'
        ],
        'individual_results': {
            'neural': {'probability': 0.87, 'confidence': 0.91},
            'rule_based': {'probability': 0.83, 'confidence': 0.93}
        }
    }
    
    sample_text = "This is a sample text for testing the report export functionality."
    
    # Create report data
    report_data = create_report_from_analysis(sample_analysis, sample_text)
    
    # Test exports
    print("Available export formats:", export_manager.get_available_formats())
    
    for format_name in export_manager.get_available_formats():
        try:
            data, content_type, extension = export_manager.export_report(report_data, format_name)
            print(f"✅ {format_name.upper()} export successful: {len(data)} bytes, {content_type}")
        except Exception as e:
            print(f"❌ {format_name.upper()} export failed: {e}")