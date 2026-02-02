"""Cloud storage integration for uploading generated videos to S3 or Cloudinary"""
import os
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
    
    def upload_video(self, local_path: Path, job_id: str) -> str:
        """Upload video to cloud storage and return public URL"""
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
        
        return str(local_path.relative_to(Path.cwd()))
    
    def _upload_to_s3(self, local_path: Path, job_id: str) -> str:
        """Upload to AWS S3"""
        key = f"videos/{job_id}/{local_path.name}"
        
        self.s3_client.upload_file(
            str(local_path),
            self.bucket_name,
            key,
            ExtraArgs={'ContentType': 'video/mp4', 'ACL': 'public-read'}
        )
        
        region = os.getenv('AWS_REGION', 'us-east-1')
        url = f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{key}"
        logger.info(f"Uploaded to S3: {url}")
        return url
    
    def _upload_to_cloudinary(self, local_path: Path, job_id: str) -> str:
        """Upload to Cloudinary"""
        response = self.cloudinary.uploader.upload(
            str(local_path),
            resource_type="video",
            public_id=f"manimations/{job_id}/{local_path.stem}",
            overwrite=True
        )
        
        url = response.get('secure_url', response.get('url'))
        logger.info(f"Uploaded to Cloudinary: {url}")
        return url
    
    def upload_json(self, local_path: Path, job_id: str) -> str:
        """Upload JSON plan to cloud storage"""
        if self.backend == "local":
            return str(local_path.relative_to(Path.cwd()))
        
        try:
            if self.backend == "s3":
                key = f"plans/{job_id}/{local_path.name}"
                self.s3_client.upload_file(
                    str(local_path),
                    self.bucket_name,
                    key,
                    ExtraArgs={'ContentType': 'application/json', 'ACL': 'public-read'}
                )
                region = os.getenv('AWS_REGION', 'us-east-1')
                return f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{key}"
            elif self.backend == "cloudinary":
                response = self.cloudinary.uploader.upload(
                    str(local_path),
                    resource_type="raw",
                    public_id=f"manimations/{job_id}/{local_path.stem}"
                )
                return response.get('secure_url', response.get('url'))
        except Exception as e:
            logger.error(f"JSON upload failed: {e}")
        
        return str(local_path.relative_to(Path.cwd()))


# Global instance
storage = CloudStorage()
