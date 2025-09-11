#!/usr/bin/env python3
"""
Test script for the report export functionality
"""

import os
import sys
from utils.report_exporter import export_manager, create_report_from_analysis
from utils.enhanced_ai_detector import detect_ai_content_enhanced

def test_report_export():
    """Test the report export functionality with sample data."""
    print("🧪 Testing Report Export Functionality")
    print("=" * 50)
    
    # Sample text for analysis
    sample_text = """
    Artificial intelligence has revolutionized numerous industries by providing 
    unprecedented capabilities in data processing, pattern recognition, and 
    automated decision-making. Machine learning algorithms can now analyze 
    vast datasets to identify trends and make predictions with remarkable 
    accuracy. This technological advancement has transformed sectors such as 
    healthcare, finance, transportation, and entertainment.
    """.strip()
    
    print(f"📝 Sample text length: {len(sample_text)} characters")
    print(f"📝 Text preview: {sample_text[:100]}...")
    print()
    
    # Perform AI detection analysis
    print("🔍 Performing AI content detection...")
    analysis_results = detect_ai_content_enhanced(sample_text)
    
    print(f"✅ Analysis complete:")
    print(f"   - AI Probability: {analysis_results.get('ai_probability', 0):.1%}")
    print(f"   - Confidence: {analysis_results.get('confidence', 0):.1%}")
    print(f"   - Classification: {analysis_results.get('classification', 'Unknown')}")
    print(f"   - Risk Level: {analysis_results.get('risk_level', 'Unknown')}")
    print()
    
    # Create report data
    print("📊 Creating report data...")
    report_data = create_report_from_analysis(
        analysis_results=analysis_results,
        text_content=sample_text,
        title="Test AI Content Detection Report"
    )
    print(f"✅ Report data created: {report_data.title}")
    print(f"   - Timestamp: {report_data.timestamp}")
    print(f"   - Metadata: {report_data.metadata}")
    print()
    
    # Test available export formats
    print("📋 Available export formats:")
    available_formats = export_manager.get_available_formats()
    for i, format_name in enumerate(available_formats, 1):
        print(f"   {i}. {format_name.upper()}")
    print()
    
    # Test each export format
    print("🚀 Testing export formats:")
    print("-" * 30)
    
    for format_name in available_formats:
        try:
            print(f"📤 Exporting as {format_name.upper()}...", end=" ")
            
            # Export report
            exported_data, content_type, file_extension = export_manager.export_report(
                report_data, format_name
            )
            
            # Save to file for verification
            output_filename = f"test_report_{format_name}{file_extension}"
            output_path = os.path.join("test_exports", output_filename)
            
            # Create output directory
            os.makedirs("test_exports", exist_ok=True)
            
            # Write exported data
            mode = 'wb' if format_name == 'pdf' else 'w'
            encoding = None if format_name == 'pdf' else 'utf-8'
            
            with open(output_path, mode, encoding=encoding) as f:
                if format_name == 'pdf':
                    f.write(exported_data)
                else:
                    f.write(exported_data.decode('utf-8'))
            
            print(f"✅ Success!")
            print(f"   - Size: {len(exported_data):,} bytes")
            print(f"   - Content-Type: {content_type}")
            print(f"   - File: {output_path}")
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
        
        print()
    
    print("🎉 Report export testing completed!")
    print(f"📁 Check the 'test_exports' directory for generated files.")
    
    # Test API endpoint format validation
    print("\n🔧 Testing format validation:")
    print("-" * 30)
    
    test_formats = ['pdf', 'json', 'csv', 'xml', 'invalid_format']
    for test_format in test_formats:
        if test_format in available_formats:
            print(f"✅ {test_format.upper()}: Supported")
        else:
            print(f"❌ {test_format.upper()}: Not supported")

if __name__ == "__main__":
    try:
        test_report_export()
    except Exception as e:
        print(f"💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)