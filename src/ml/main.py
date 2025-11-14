import torch
from PIL import Image
from torchvision import models, transforms

# Load ResNet-50 model (pretrained)
resnet50 = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
resnet50.eval()


# Preprocessing pipeline for input images
def preprocess_image(image_path):
    input_image = Image.open(image_path).convert("RGB")
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
def infer_resnet50(image_path):
    input_batch = preprocess_image(image_path)
    with torch.no_grad():
        output = resnet50(input_batch)
    # Get top-1 prediction
    _, predicted_idx = torch.max(output, 1)
    # Load ImageNet class labels
    labels_path = models.ResNet50_Weights.DEFAULT.meta["categories"]
    predicted_label = labels_path[predicted_idx.item()]
    return {"class_id": predicted_idx.item(), "class_name": predicted_label}
