"""
Comprehensive unit tests for Firebase Service
Tests Firebase integration including Firestore operations, error handling, and fallback mechanisms.
"""

import pytest
import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.firebase_service import FirebaseService


class TestFirebaseService(unittest.TestCase):
    """Test cases for FirebaseService"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock Firebase dependencies to avoid actual Firebase calls
        self.mock_firebase_admin = patch('services.firebase_service.firebase_admin').start()
        self.mock_credentials = patch('services.firebase_service.credentials').start()
        self.mock_firestore = patch('services.firebase_service.firestore').start()
        self.mock_auth = patch('services.firebase_service.auth').start()
        self.mock_storage = patch('services.firebase_service.storage').start()
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'FIREBASE_SERVICE_ACCOUNT_PATH': '/path/to/service-account.json',
            'FIREBASE_STORAGE_BUCKET': 'test-bucket.appspot.com'
        })
        self.env_patcher.start()
        
        # Mock Firebase app and services
        self.mock_app = MagicMock()
        self.mock_db = MagicMock()
        self.mock_bucket = MagicMock()
        
        # Configure mocks
        self.mock_firebase_admin._apps = {}  # Empty apps initially
        self.mock_firebase_admin.initialize_app.return_value = self.mock_app
        self.mock_firebase_admin.get_app.return_value = self.mock_app
        self.mock_firestore.client.return_value = self.mock_db
        self.mock_storage.bucket.return_value = self.mock_bucket
        
        # Sample test data
        self.sample_document = {
            'id': 'test_doc_123',
            'text': 'Sample text for testing',
            'ai_probability': 0.75,
            'timestamp': datetime.now().isoformat()
        }
        
        self.sample_feedback = {
            'feedback_type': 'accuracy',
            'rating': 5,
            'comment': 'Great detection accuracy',
            'user_id': 'user123'
        }
        
        self.sample_scan_result = {
            'text': 'Sample text for scanning',
            'ai_probability': 0.65,
            'human_probability': 0.35,
            'confidence': 0.8,
            'classification': 'Likely AI-Generated',
            'user_id': 'user123'
        }
    
    def tearDown(self):
        """Clean up after each test method."""
        patch.stopall()
        self.env_patcher.stop()
    
    def test_firebase_service_initialization_success(self):
        """Test successful Firebase service initialization"""
        # Mock successful initialization
        with patch('os.path.exists', return_value=True):
            service = FirebaseService()
            
            self.assertIsNotNone(service)
            self.assertEqual(service.app, self.mock_app)
            self.assertEqual(service.db, self.mock_db)
            self.assertEqual(service.bucket, self.mock_bucket)
            
            # Verify Firebase was initialized
            self.mock_firebase_admin.initialize_app.assert_called_once()
    
    def test_firebase_service_initialization_existing_app(self):
        """Test Firebase service initialization with existing app"""
        # Mock existing app
        self.mock_firebase_admin._apps = {'default': self.mock_app}
        
        service = FirebaseService()
        
        self.assertIsNotNone(service)
        self.assertEqual(service.app, self.mock_app)
        self.mock_firebase_admin.get_app.assert_called_once()
    
    def test_firebase_service_initialization_no_service_account(self):
        """Test Firebase service initialization without service account file"""
        with patch('os.path.exists', return_value=False):
            service = FirebaseService()
            
            # Should still initialize with default credentials
            self.assertIsNotNone(service)
            self.mock_firebase_admin.initialize_app.assert_called_once()
    
    def test_firebase_service_initialization_failure(self):
        """Test Firebase service initialization failure"""
        # Mock initialization failure
        self.mock_firebase_admin.initialize_app.side_effect = Exception("Firebase init failed")
        
        with self.assertRaises(Exception):
            FirebaseService()
    
    def test_add_document_success(self):
        """Test successful document addition"""
        service = FirebaseService()
        
        # Mock Firestore operations
        mock_doc_ref = MagicMock()
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        self.mock_db.collection.return_value = mock_collection
        
        # Test with specific document ID
        doc_id = service.add_document('test_collection', self.sample_document, 'test_doc_123')
        
        self.assertEqual(doc_id, 'test_doc_123')
        self.mock_db.collection.assert_called_with('test_collection')
        mock_collection.document.assert_called_with('test_doc_123')
        mock_doc_ref.set.assert_called_with(self.sample_document)
    
    def test_add_document_auto_id(self):
        """Test document addition with auto-generated ID"""
        service = FirebaseService()
        
        # Mock Firestore operations for auto ID
        mock_doc_ref = MagicMock()
        mock_doc_ref.id = 'auto_generated_id'
        mock_collection = MagicMock()
        mock_collection.add.return_value = (None, mock_doc_ref)
        self.mock_db.collection.return_value = mock_collection
        
        doc_id = service.add_document('test_collection', self.sample_document)
        
        self.assertEqual(doc_id, 'auto_generated_id')
        mock_collection.add.assert_called_with(self.sample_document)
    
    def test_add_document_failure(self):
        """Test document addition failure"""
        service = FirebaseService()
        
        # Mock Firestore failure
        self.mock_db.collection.side_effect = Exception("Firestore error")
        
        with self.assertRaises(Exception):
            service.add_document('test_collection', self.sample_document)
    
    def test_get_document_success(self):
        """Test successful document retrieval"""
        service = FirebaseService()
        
        # Mock Firestore operations
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = self.sample_document
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        self.mock_db.collection.return_value = mock_collection
        
        result = service.get_document('test_collection', 'test_doc_123')
        
        self.assertEqual(result, self.sample_document)
        self.mock_db.collection.assert_called_with('test_collection')
        mock_collection.document.assert_called_with('test_doc_123')
    
    def test_get_document_not_found(self):
        """Test document retrieval when document doesn't exist"""
        service = FirebaseService()
        
        # Mock document not found
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        self.mock_db.collection.return_value = mock_collection
        
        result = service.get_document('test_collection', 'nonexistent_doc')
        
        self.assertIsNone(result)
    
    def test_get_document_failure(self):
        """Test document retrieval failure"""
        service = FirebaseService()
        
        # Mock Firestore failure
        self.mock_db.collection.side_effect = Exception("Firestore error")
        
        with self.assertRaises(Exception):
            service.get_document('test_collection', 'test_doc_123')
    
    def test_update_document_success(self):
        """Test successful document update"""
        service = FirebaseService()
        
        # Mock Firestore operations
        mock_doc_ref = MagicMock()
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        self.mock_db.collection.return_value = mock_collection
        
        update_data = {'ai_probability': 0.85}
        result = service.update_document('test_collection', 'test_doc_123', update_data)
        
        self.assertTrue(result)
        mock_doc_ref.update.assert_called_with(update_data)
    
    def test_update_document_failure(self):
        """Test document update failure"""
        service = FirebaseService()
        
        # Mock Firestore failure
        self.mock_db.collection.side_effect = Exception("Firestore error")
        
        with self.assertRaises(Exception):
            service.update_document('test_collection', 'test_doc_123', {'data': 'value'})
    
    def test_delete_document_success(self):
        """Test successful document deletion"""
        service = FirebaseService()
        
        # Mock Firestore operations
        mock_doc_ref = MagicMock()
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        self.mock_db.collection.return_value = mock_collection
        
        result = service.delete_document('test_collection', 'test_doc_123')
        
        self.assertTrue(result)
        mock_doc_ref.delete.assert_called_once()
    
    def test_delete_document_failure(self):
        """Test document deletion failure"""
        service = FirebaseService()
        
        # Mock Firestore failure
        self.mock_db.collection.side_effect = Exception("Firestore error")
        
        with self.assertRaises(Exception):
            service.delete_document('test_collection', 'test_doc_123')
    
    def test_get_collection_success(self):
        """Test successful collection retrieval"""
        service = FirebaseService()
        
        # Mock Firestore operations
        mock_doc1 = MagicMock()
        mock_doc1.id = 'doc1'
        mock_doc1.to_dict.return_value = {'data': 'value1'}
        mock_doc2 = MagicMock()
        mock_doc2.id = 'doc2'
        mock_doc2.to_dict.return_value = {'data': 'value2'}
        
        mock_query = MagicMock()
        mock_query.stream.return_value = [mock_doc1, mock_doc2]
        self.mock_db.collection.return_value = mock_query
        
        result = service.get_collection('test_collection')
        
        expected = [
            {'id': 'doc1', 'data': 'value1'},
            {'id': 'doc2', 'data': 'value2'}
        ]
        self.assertEqual(result, expected)
    
    def test_get_collection_with_filters(self):
        """Test collection retrieval with filters"""
        service = FirebaseService()
        
        # Mock Firestore operations with filters
        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.stream.return_value = []
        self.mock_db.collection.return_value = mock_query
        
        where_filters = [('field', '==', 'value')]
        result = service.get_collection(
            'test_collection',
            limit=10,
            order_by='timestamp',
            where_filters=where_filters
        )
        
        self.assertEqual(result, [])
        mock_query.order_by.assert_called_with('timestamp')
        mock_query.limit.assert_called_with(10)
    
    def test_save_feedback_success(self):
        """Test successful feedback saving"""
        service = FirebaseService()
        
        # Mock add_document and _update_analytics_counter
        with patch.object(service, 'add_document', return_value='feedback_123') as mock_add:
            with patch.object(service, '_update_analytics_counter') as mock_update:
                doc_id = service.save_feedback(self.sample_feedback)
                
                self.assertEqual(doc_id, 'feedback_123')
                mock_add.assert_called_once()
                mock_update.assert_called_with('total_feedback', 1)
                
                # Check that timestamp was added
                call_args = mock_add.call_args[0]
                self.assertEqual(call_args[0], 'feedback')
                self.assertIn('timestamp', call_args[1])
    
    def test_save_feedback_with_timestamp(self):
        """Test feedback saving when timestamp is already present"""
        service = FirebaseService()
        
        feedback_with_timestamp = {**self.sample_feedback, 'timestamp': '2023-01-01T00:00:00'}
        
        with patch.object(service, 'add_document', return_value='feedback_123') as mock_add:
            with patch.object(service, '_update_analytics_counter'):
                service.save_feedback(feedback_with_timestamp)
                
                # Should not modify existing timestamp
                call_args = mock_add.call_args[0]
                self.assertEqual(call_args[1]['timestamp'], '2023-01-01T00:00:00')
    
    def test_save_scan_result_success(self):
        """Test successful scan result saving"""
        service = FirebaseService()
        
        with patch.object(service, 'add_document', return_value='scan_123') as mock_add:
            with patch.object(service, '_update_analytics_counter') as mock_update:
                doc_id = service.save_scan_result(self.sample_scan_result)
                
                self.assertEqual(doc_id, 'scan_123')
                mock_add.assert_called_once()
                mock_update.assert_called_with('total_scans', 1)
                
                # Check that timestamp was added
                call_args = mock_add.call_args[0]
                self.assertEqual(call_args[0], 'scans')
                self.assertIn('timestamp', call_args[1])
    
    def test_get_feedback_success(self):
        """Test successful feedback retrieval"""
        service = FirebaseService()
        
        expected_feedback = [self.sample_feedback]
        
        with patch.object(service, 'get_collection', return_value=expected_feedback) as mock_get:
            result = service.get_feedback(limit=10, feedback_type='accuracy')
            
            self.assertEqual(result, expected_feedback)
            mock_get.assert_called_once()
    
    def test_get_scan_results_success(self):
        """Test successful scan results retrieval"""
        service = FirebaseService()
        
        expected_scans = [self.sample_scan_result]
        
        with patch.object(service, 'get_collection', return_value=expected_scans) as mock_get:
            result = service.get_scan_results(limit=10, user_id='user123')
            
            self.assertEqual(result, expected_scans)
            mock_get.assert_called_once()
    
    def test_error_handling_consistency(self):
        """Test that all methods handle errors consistently"""
        service = FirebaseService()
        
        # Mock Firestore to always raise exceptions
        self.mock_db.collection.side_effect = Exception("Firestore error")
        
        methods_to_test = [
            ('add_document', ['collection', {'data': 'value'}]),
            ('get_document', ['collection', 'doc_id']),
            ('update_document', ['collection', 'doc_id', {'data': 'value'}]),
            ('delete_document', ['collection', 'doc_id']),
            ('get_collection', ['collection']),
        ]
        
        for method_name, args in methods_to_test:
            method = getattr(service, method_name)
            with self.assertRaises(Exception):
                method(*args)
    
    def test_service_availability_check(self):
        """Test checking if Firebase service is available"""
        # Test successful initialization
        service = FirebaseService()
        self.assertIsNotNone(service.db)
        self.assertIsNotNone(service.bucket)
        
        # Test with initialization failure
        with patch('services.firebase_service.firebase_admin.initialize_app', 
                  side_effect=Exception("Init failed")):
            with self.assertRaises(Exception):
                FirebaseService()


if __name__ == '__main__':
    unittest.main()