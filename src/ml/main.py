import os
from io import BytesIO

import torch
from minio import Minio
from PIL import Image
from torchvision import models, transforms

# Load ResNet-50 model (pretrained)
resnet50 = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
resnet50.eval()


def load_image_from_location(location, minio_config=None):
    """Load image from either local path or MinIO URL
    
    Args:
        location: File path or minio://bucket/path URL
        minio_config: Dict with endpoint, access_key, secret_key, use_ssl (optional)
    """
    if location.startswith('minio://'):
        # Parse MinIO URL: minio://bucket/path
        parts = location.replace('minio://', '').split('/', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid MinIO URL format: {location}")
        
        bucket_name, object_path = parts
        
        # Use provided config or fall back to environment variables
        if minio_config:
            endpoint = minio_config.get('endpoint', 'localhost:9000')
            access_key = minio_config.get('access_key', 'minioadmin')
            secret_key = minio_config.get('secret_key', 'minioadmin')
            use_ssl = minio_config.get('use_ssl', False)
        else:
            endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
            access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
            secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
            use_ssl = os.getenv('MINIO_USE_SSL', 'false').lower() == 'true'
        
        # Remove http/https prefix if present
        endpoint = endpoint.replace('http://', '').replace('https://', '')
        
        # Create MinIO client
        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=use_ssl
        )
        
        # Download image to BytesIO
        response = client.get_object(bucket_name, object_path)
        image_data = BytesIO(response.read())
        response.close()
        response.release_conn()
        
        return Image.open(image_data)
    else:
        # Local file path
        return Image.open(location)


# Preprocessing pipeline for input images
def preprocess_image(image_path, minio_config=None):
    input_image = load_image_from_location(image_path, minio_config).convert("RGB")
    preprocess = transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0)
    return input_batch


# Inference function
def infer_resnet50(image_path, minio_config=None):
    input_batch = preprocess_image(image_path, minio_config)
    with torch.no_grad():
        output = resnet50(input_batch)
    # Get top-1 prediction
    _, predicted_idx = torch.max(output, 1)
    # Load ImageNet class labels
    labels_path = models.ResNet50_Weights.DEFAULT.meta["categories"]
    predicted_label = labels_path[predicted_idx.item()]
    return {"class_id": predicted_idx.item(), "class_name": predicted_label}
