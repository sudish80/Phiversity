"""Cloud storage integration for uploading generated videos to S3 or Cloudinary"""
import os
import time
from pathlib import Path
from typing import Optional, Literal
import logging

logger = logging.getLogger(__name__)

StorageBackend = Literal["s3", "cloudinary", "local"]


class CloudStorage:
    """Handle uploads to cloud storage services"""
    
    def __init__(self, backend: Optional[StorageBackend] = None):
        self.backend = backend or os.getenv("STORAGE_BACKEND", "local")
        
        if self.backend == "s3":
            self._init_s3()
        elif self.backend == "cloudinary":
            self._init_cloudinary()
    
    def _init_s3(self):
        """Initialize AWS S3 client"""
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.bucket_name = os.getenv('AWS_S3_BUCKET')
            logger.info(f"S3 storage initialized with bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize S3: {e}")
            self.backend = "local"
    
    def _init_cloudinary(self):
        """Initialize Cloudinary client"""
        try:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(
                cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                api_key=os.getenv('CLOUDINARY_API_KEY'),
                api_secret=os.getenv('CLOUDINARY_API_SECRET')
            )
            self.cloudinary = cloudinary
            logger.info("Cloudinary storage initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Cloudinary: {e}")
            self.backend = "local"
    
    def upload_video(self, local_path, job_id: str) -> str:
        """Upload video to cloud storage and return public URL.
        
        Accepts either a Path or str for local_path.
        """
        local_path = Path(local_path)
        if self.backend == "local":
            return str(local_path.relative_to(Path.cwd()))
        
        try:
            if self.backend == "s3":
                return self._upload_to_s3(local_path, job_id)
            elif self.backend == "cloudinary":
                return self._upload_to_cloudinary(local_path, job_id)
        except Exception as e:
            logger.error(f"Cloud upload failed: {e}. Falling back to local.")
        
        return str(local_path.relative_to(Path.cwd()))
    
    def _upload_to_s3(self, local_path: Path, job_id: str) -> str:
        """Upload to AWS S3 with private ACL for commercial use security"""
        key = f"videos/{job_id}/{local_path.name}"
        
        # Use 'private' ACL to prevent public access - required for commercial use
        self.s3_client.upload_file(
            str(local_path),
            self.bucket_name,
            key,
            ExtraArgs={'ContentType': 'video/mp4', 'ACL': 'private'}
        )
        
        # Store the S3 key for signed URL generation, not a public URL
        # The backend will generate signed URLs when user requests the artifact
        s3_key = key
        logger.info(f"Uploaded to S3 (private): {s3_key}")
        return f"s3://{self.bucket_name}/{s3_key}"
    
    def _upload_to_cloudinary(self, local_path: Path, job_id: str) -> str:
        """Upload to Cloudinary with restricted access for commercial use"""
        # Use 'authenticated' access mode to prevent public access
        response = self.cloudinary.uploader.upload(
            str(local_path),
            resource_type="video",
            public_id=f"manimations/{job_id}/{local_path.stem}",
            overwrite=True,
            access_mode="authenticated"  # Restrict access to authenticated users only
        )
        
        # Return a reference key, not the direct URL - backend will generate signed URLs
        public_id = response.get('public_id')
        logger.info(f"Uploaded to Cloudinary (authenticated): {public_id}")
        return f"cloudinary://{public_id}"
    
    def upload_json(self, local_path: Path, job_id: str) -> str:
        """Upload JSON plan to cloud storage with private access for commercial use"""
        if self.backend == "local":
            return str(local_path.relative_to(Path.cwd()))
        
        try:
            if self.backend == "s3":
                key = f"plans/{job_id}/{local_path.name}"
                # Use private ACL for commercial security
                self.s3_client.upload_file(
                    str(local_path),
                    self.bucket_name,
                    key,
                    ExtraArgs={'ContentType': 'application/json', 'ACL': 'private'}
                )
                # Return S3 key reference, not public URL
                return f"s3://{self.bucket_name}/{key}"
            elif self.backend == "cloudinary":
                # Use authenticated access for privacy
                response = self.cloudinary.uploader.upload(
                    str(local_path),
                    resource_type="raw",
                    public_id=f"manimations/{job_id}/{local_path.stem}",
                    access_mode="authenticated"
                )
                # Return reference key, not direct URL
                return f"cloudinary://{response.get('public_id')}"
        except Exception as e:
            logger.error(f"JSON upload failed: {e}")
        
        return str(local_path.relative_to(Path.cwd()))

    def generate_signed_url(self, storage_ref: str, expires_in: int = 3600) -> str:
        """Generate a signed URL for private cloud storage access.
        
        Args:
            storage_ref: S3 key (s3://bucket/key) or Cloudinary public_id (cloudinary://id)
            expires_in: URL expiration time in seconds (default 1 hour)
        
        Returns:
            Signed URL that provides temporary access to the private resource
        """
        if storage_ref.startswith("s3://"):
            # Generate presigned URL for S3
            bucket_key = storage_ref[5:]  # Remove 's3://'
            bucket_name, key = bucket_key.split('/', 1)
            try:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': key},
                    ExpiresIn=expires_in
                )
                logger.info(f"Generated signed S3 URL for: {key}")
                return url
            except Exception as e:
                logger.error(f"Failed to generate S3 signed URL: {e}")
                raise
        elif storage_ref.startswith("cloudinary://"):
            # Generate signed URL for Cloudinary
            public_id = storage_ref[13:]  # Remove 'cloudinary://'
            try:
                # Generate a signed URL that expires
                url = self.cloudinary.utils.cloudinary_url(
                    public_id,
                    sign_url=True,
                    expires_at=int(time.time() + expires_in)
                )[0]
                logger.info(f"Generated signed Cloudinary URL for: {public_id}")
                return url
            except Exception as e:
                logger.error(f"Failed to generate Cloudinary signed URL: {e}")
                raise
        else:
            # Local file - return as-is
            return storage_ref


# Global instance
storage = CloudStorage()
