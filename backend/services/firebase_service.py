import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud import firestore as firestore_client

class FirebaseService:
    """
    Firebase service class to handle all Firebase operations including:
    - Firestore database operations
    - Firebase Authentication
    - Firebase Storage
    """
    
    def __init__(self):
        self.app = None
        self.db = None
        self.bucket = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK with service account credentials."""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Get service account path from environment variable
                service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
                
                if service_account_path and os.path.exists(service_account_path):
                    # Initialize with service account file
                    cred = credentials.Certificate(service_account_path)
                    self.app = firebase_admin.initialize_app(cred, {
                        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
                    })
                else:
                    # Try to initialize with default credentials (for production)
                    self.app = firebase_admin.initialize_app()
                
                print("Firebase Admin SDK initialized successfully")
            else:
                self.app = firebase_admin.get_app()
                print("Using existing Firebase app instance")
            
            # Initialize Firestore client
            self.db = firestore.client()
            
            # Initialize Storage bucket
            self.bucket = storage.bucket()
            
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            raise e
    
    # ==================== FIRESTORE OPERATIONS ====================
    
    def add_document(self, collection: str, data: Dict[str, Any], doc_id: Optional[str] = None) -> str:
        """Add a document to a Firestore collection."""
        try:
            if doc_id:
                doc_ref = self.db.collection(collection).document(doc_id)
                doc_ref.set(data)
                return doc_id
            else:
                doc_ref = self.db.collection(collection).add(data)
                return doc_ref[1].id
        except Exception as e:
            print(f"Error adding document to {collection}: {e}")
            raise e
    
    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document from a Firestore collection."""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting document {doc_id} from {collection}: {e}")
            raise e
    
    def update_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update a document in a Firestore collection."""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.update(data)
            return True
        except Exception as e:
            print(f"Error updating document {doc_id} in {collection}: {e}")
            raise e
    
    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document from a Firestore collection."""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting document {doc_id} from {collection}: {e}")
            raise e
    
    def get_collection(self, collection: str, limit: Optional[int] = None, 
                      order_by: Optional[str] = None, 
                      where_filters: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """Get documents from a Firestore collection with optional filtering and ordering."""
        try:
            query = self.db.collection(collection)
            
            # Apply where filters
            if where_filters:
                for field, operator, value in where_filters:
                    query = query.where(filter=FieldFilter(field, operator, value))
            
            # Apply ordering
            if order_by:
                query = query.order_by(order_by)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"Error getting collection {collection}: {e}")
            raise e
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    def save_feedback(self, feedback_data: Dict[str, Any]) -> str:
        """Save user feedback to Firestore."""
        try:
            # Add timestamp if not present
            if 'timestamp' not in feedback_data:
                feedback_data['timestamp'] = datetime.now().isoformat()
            
            # Add to feedback collection
            doc_id = self.add_document('feedback', feedback_data)
            
            # Update analytics counters
            self._update_analytics_counter('total_feedback', 1)
            
            return doc_id
        except Exception as e:
            print(f"Error saving feedback: {e}")
            raise e
    
    def get_feedback(self, limit: Optional[int] = None, 
                    feedback_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get feedback from Firestore with optional filtering."""
        try:
            where_filters = []
            if feedback_type:
                where_filters.append(('feedback_type', '==', feedback_type))
            
            return self.get_collection(
                'feedback', 
                limit=limit, 
                order_by='timestamp', 
                where_filters=where_filters if where_filters else None
            )
        except Exception as e:
            print(f"Error getting feedback: {e}")
            raise e
    
    def save_scan_result(self, scan_data: Dict[str, Any]) -> str:
        """Save scan result to Firestore."""
        try:
            # Add timestamp if not present
            if 'timestamp' not in scan_data:
                scan_data['timestamp'] = datetime.now().isoformat()
            
            # Add to scans collection
            doc_id = self.add_document('scans', scan_data)
            
            # Update analytics counters
            self._update_analytics_counter('total_scans', 1)
            
            return doc_id
        except Exception as e:
            print(f"Error saving scan result: {e}")
            raise e
    
    def get_scan_results(self, limit: Optional[int] = None, 
                        user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get scan results from Firestore with optional filtering."""
        try:
            where_filters = []
            if user_id:
                where_filters.append(('user_id', '==', user_id))
            
            return self.get_collection(
                'scans', 
                limit=limit, 
                order_by='timestamp', 
                where_filters=where_filters if where_filters else None
            )
        except Exception as e:
            print(f"Error getting scan results: {e}")
            raise e
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary from Firestore."""
        try:
            # Get analytics document
            analytics = self.get_document('analytics', 'summary')
            
            if not analytics:
                # Initialize analytics if it doesn't exist
                analytics = {
                    'total_feedback': 0,
                    'total_scans': 0,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                self.add_document('analytics', analytics, 'summary')
            
            return analytics
        except Exception as e:
            print(f"Error getting analytics summary: {e}")
            raise e
    
    def _update_analytics_counter(self, field: str, increment: int = 1):
        """Update analytics counter in Firestore."""
        try:
            analytics_ref = self.db.collection('analytics').document('summary')
            
            # Use transaction to ensure atomic update
            @firestore.transactional
            def update_counter(transaction, ref):
                doc = ref.get(transaction=transaction)
                if doc.exists:
                    current_value = doc.get(field, 0)
                    transaction.update(ref, {
                        field: current_value + increment,
                        'updated_at': datetime.now().isoformat()
                    })
                else:
                    transaction.set(ref, {
                        field: increment,
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    })
            
            transaction = self.db.transaction()
            update_counter(transaction, analytics_ref)
            
        except Exception as e:
            print(f"Error updating analytics counter {field}: {e}")
            raise e
    
    # ==================== AUTHENTICATION OPERATIONS ====================
    
    def verify_id_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token and return user info."""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"Error verifying ID token: {e}")
            return None
    
    def get_user(self, uid: str) -> Optional[Dict[str, Any]]:
        """Get user information by UID."""
        try:
            user = auth.get_user(uid)
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'email_verified': user.email_verified,
                'disabled': user.disabled,
                'metadata': {
                    'creation_timestamp': user.user_metadata.creation_timestamp,
                    'last_sign_in_timestamp': user.user_metadata.last_sign_in_timestamp
                }
            }
        except Exception as e:
            print(f"Error getting user {uid}: {e}")
            return None
    
    def create_custom_token(self, uid: str, additional_claims: Optional[Dict] = None) -> str:
        """Create a custom token for a user."""
        try:
            return auth.create_custom_token(uid, additional_claims)
        except Exception as e:
            print(f"Error creating custom token for {uid}: {e}")
            raise e
    
    def disable_user(self, uid: str) -> bool:
        """Disable a user account."""
        try:
            auth.update_user(uid, disabled=True)
            print(f"User {uid} has been disabled")
            return True
        except Exception as e:
            print(f"Error disabling user {uid}: {e}")
            return False
    
    def enable_user(self, uid: str) -> bool:
        """Enable a user account."""
        try:
            auth.update_user(uid, disabled=False)
            print(f"User {uid} has been enabled")
            return True
        except Exception as e:
            print(f"Error enabling user {uid}: {e}")
            return False
    
    def delete_user(self, uid: str) -> bool:
        """Delete a user account and all associated data."""
        try:
            # Delete user from Firebase Auth
            auth.delete_user(uid)
            
            # Delete user profile from Firestore
            user_ref = self.db.collection('users').document(uid)
            user_ref.delete()
            
            # Delete user's detection results
            detections_ref = self.db.collection('detections').where('userId', '==', uid)
            detections = detections_ref.get()
            for detection in detections:
                detection.reference.delete()
            
            # Delete user's feedback
            feedback_ref = self.db.collection('feedback').where('userId', '==', uid)
            feedback = feedback_ref.get()
            for fb in feedback:
                fb.reference.delete()
            
            print(f"User {uid} and all associated data have been deleted")
            return True
        except Exception as e:
            print(f"Error deleting user {uid}: {e}")
            return False
    
    # ==================== STORAGE OPERATIONS ====================
    
    def upload_file(self, file_path: str, destination_blob_name: str) -> str:
        """Upload a file to Firebase Storage."""
        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_filename(file_path)
            
            # Make the blob publicly readable (optional)
            blob.make_public()
            
            return blob.public_url
        except Exception as e:
            print(f"Error uploading file {file_path}: {e}")
            raise e
    
    def upload_file_from_memory(self, file_data: bytes, destination_blob_name: str, 
                               content_type: str = 'application/octet-stream') -> str:
        """Upload file data from memory to Firebase Storage."""
        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.upload_from_string(file_data, content_type=content_type)
            
            # Make the blob publicly readable (optional)
            blob.make_public()
            
            return blob.public_url
        except Exception as e:
            print(f"Error uploading file from memory: {e}")
            raise e
    
    def delete_file(self, blob_name: str) -> bool:
        """Delete a file from Firebase Storage."""
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting file {blob_name}: {e}")
            return False
    
    def get_file_url(self, blob_name: str) -> Optional[str]:
        """Get the public URL of a file in Firebase Storage."""
        try:
            blob = self.bucket.blob(blob_name)
            if blob.exists():
                return blob.public_url
            return None
        except Exception as e:
            print(f"Error getting file URL for {blob_name}: {e}")
            return None
    
    # ==================== MIGRATION UTILITIES ====================
    
    def migrate_json_data_to_firestore(self, json_file_path: str) -> bool:
        """Migrate existing JSON analytics data to Firestore."""
        try:
            if not os.path.exists(json_file_path):
                print(f"JSON file {json_file_path} does not exist")
                return False
            
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            # Migrate feedback data
            if 'feedback' in data and data['feedback']:
                for feedback in data['feedback']:
                    self.add_document('feedback', feedback)
                print(f"Migrated {len(data['feedback'])} feedback entries")
            
            # Migrate scan data
            if 'scans' in data and data['scans']:
                for scan in data['scans']:
                    self.add_document('scans', scan)
                print(f"Migrated {len(data['scans'])} scan entries")
            
            # Migrate accuracy feedback
            if 'accuracy_feedback' in data and data['accuracy_feedback']:
                for accuracy in data['accuracy_feedback']:
                    self.add_document('accuracy_feedback', accuracy)
                print(f"Migrated {len(data['accuracy_feedback'])} accuracy feedback entries")
            
            # Update analytics summary
            analytics_summary = {
                'total_feedback': len(data.get('feedback', [])),
                'total_scans': data.get('total_scans', len(data.get('scans', []))),
                'migrated_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            self.add_document('analytics', analytics_summary, 'summary')
            
            print("Data migration completed successfully")
            return True
            
        except Exception as e:
            print(f"Error migrating JSON data: {e}")
            return False


# Global Firebase service instance
firebase_service = None

def get_firebase_service() -> FirebaseService:
    """Get or create Firebase service instance."""
    global firebase_service
    if firebase_service is None:
        firebase_service = FirebaseService()
    return firebase_service

def initialize_firebase_service() -> FirebaseService:
    """Initialize Firebase service (can be called multiple times safely)."""
    return get_firebase_service()