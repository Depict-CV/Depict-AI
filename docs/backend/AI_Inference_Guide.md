# AI Inference Feature

## Overview

The AI Inference feature allows you to automatically annotate images in your projects using pre-trained machine learning models. Currently supports ResNet-50 for image classification.

## Features

### ✅ What It Does

- **Automatic Annotation**: Run inference on all unannotated images in a project
- **Batch Processing**: Process multiple images efficiently
- **ML Annotation Status**: Predictions marked as "ML Annotation" for review
- **Detailed Results**: See success/failure for each image
- **Optional Saving**: Choose whether to save predictions to database

## How to Use

### 1. Select a Project

First, select the project you want to run inference on from the Projects panel.

### 2. Open AI Panel

Click the AI Tools (🤖) icon in the sidebar.

### 3. Configure Inference

**Model Selection:**
- Currently: ResNet-50 (Image Classification)
- Trained on: ImageNet (1000 classes)
- Future: More models will be added

**Options:**
- **Save as Annotations**: Enable to automatically save predictions to database
- **Batch Limit**: Optionally limit how many images to process (useful for testing)

### 4. Run Inference

Click **"Run Inference on Project"** button.

The system will:
1. Find all images without annotations in the project
2. Run ResNet-50 inference on each image
3. Classify images into one of 1000 ImageNet categories
4. Save annotations to database (if enabled)
5. Display detailed results

### 5. Review Results

After inference completes, you'll see:
- **Total Processed**: Number of images analyzed
- **Successful**: Images successfully classified
- **Failed**: Images that encountered errors
- **Success Rate**: Percentage of successful predictions
- **Detailed List**: Individual results for each image with predictions

## API Endpoints

### Single Image Inference

```
POST /infer/resnet50
{
  "image_path": "/path/to/image.jpg"
}

Response:
{
  "class_id": 281,
  "class_name": "tabby cat"
}
```

### Batch Inference

```
POST /infer/resnet50/batch
{
  "data_ids": [1, 2, 3, 4],
  "project_id": 1,
  "save_annotations": true
}

Response:
{
  "total": 4,
  "successful": 3,
  "failed": 1,
  "results": [...],
  "annotations_saved": true
}
```

### Project Inference

```
POST /infer/resnet50/project
{
  "project_id": 1,
  "save_annotations": true,
  "limit": 100  // optional
}

Response:
{
  "total": 50,
  "successful": 48,
  "failed": 2,
  "results": [...],
  "annotations_saved": true,
  "project_id": 1,
  "project_name": "My Project"
}
```

## Model Details

### ResNet-50

**Architecture:**
- Deep Residual Network with 50 layers
- Pre-trained on ImageNet dataset
- 1000 output classes

**Input Requirements:**
- RGB images
- Resized to 256x256
- Center cropped to 224x224
- Normalized with ImageNet mean/std

**Output:**
- Class ID (0-999)
- Class Name (e.g., "golden retriever", "laptop", "mountain bike")

**Example Categories:**
- Animals: dogs, cats, birds, fish, insects
- Objects: furniture, electronics, vehicles, food
- Natural: plants, landscapes, weather
- And 900+ more categories

## Annotation Status

Predictions are saved with status: **`ML_ANNOTATION`**

This allows you to:
- Distinguish ML predictions from human annotations
- Review and verify ML predictions
- Approve or modify predictions as needed
- Track annotation source

## Performance

**Speed:**
- Local CPU: ~1-2 seconds per image
- GPU (if available): ~0.1-0.2 seconds per image
- Batch processing: Efficient for large datasets

**Accuracy:**
- Depends on image content and quality
- Best for ImageNet-like images
- May require review for domain-specific images

## Workflow Example

### Typical Usage

1. **Upload Images**: Import images to project via Import/Export panel
2. **Run Inference**: Use AI panel to auto-annotate all images
3. **Review Results**: Check predictions in results panel
4. **Verify Annotations**: Review ML annotations in gallery
5. **Correct Errors**: Manually edit incorrect predictions
6. **Approve**: Mark verified annotations as certified

### Quality Control

```
All Images (100)
    ↓
Run ML Inference
    ↓
ML Annotations (95 successful, 5 failed)
    ↓
Manual Review
    ↓
Corrections (10 images needed fixing)
    ↓
Certified Annotations (95 verified)
```

## Best Practices

### When to Use AI Inference

✅ **Good Use Cases:**
- Large datasets needing initial annotation
- Common objects/categories (ImageNet classes)
- Quick prototyping and exploration
- Reducing manual annotation workload

❌ **Not Recommended:**
- Highly specialized domains (medical, scientific)
- Custom categories not in ImageNet
- Critical applications requiring 100% accuracy
- Very low quality or corrupted images

### Optimization Tips

1. **Start Small**: Test with batch limit before processing all images
2. **Review First Batch**: Check accuracy on sample before full run
3. **Save Selectively**: Disable saving if just testing
4. **Monitor Failures**: Check failed images for patterns
5. **Iterate**: Correct patterns and re-run on failed images

## Troubleshooting

### "No unannotated images found"

**Cause**: All images in project already have annotations  
**Solution**: 
- Clear existing annotations if you want to re-annotate
- Upload new images to project

### Inference failing on images

**Cause**: Image file issues (corrupt, wrong format, inaccessible)  
**Solution**:
- Check image file integrity
- Verify file paths are correct
- Ensure MinIO/storage is accessible
- Check backend logs for specific errors

### Low accuracy predictions

**Cause**: Images don't match ImageNet distribution  
**Solution**:
- Use domain-specific models (future feature)
- Manual annotation for specialized content
- Fine-tune models on your data (future feature)

### Slow processing

**Cause**: CPU inference, large images  
**Solution**:
- Use GPU if available (configure PyTorch)
- Process in smaller batches
- Optimize image sizes

## Future Enhancements

### Planned Features

- [ ] Multiple model support (YOLOv8, SAM, etc.)
- [ ] Object detection (bounding boxes)
- [ ] Instance segmentation
- [ ] Custom model upload
- [ ] Fine-tuning on your data
- [ ] Active learning workflow
- [ ] Confidence scores display
- [ ] Batch selection for inference
- [ ] Progress bar during inference
- [ ] Export predictions to file

### Coming Soon

**YOLOv8 Object Detection:**
- Detect multiple objects per image
- Draw bounding boxes
- Multi-class detection

**Segment Anything Model (SAM):**
- Interactive segmentation
- Automatic mask generation
- Instance separation

## Integration with Workflow

### Complete Pipeline

```
1. Data Import
   ↓
2. AI Inference (Auto-annotation)
   ↓
3. Manual Review (Quality check)
   ↓
4. Corrections (Fix errors)
   ↓
5. Certification (Approve)
   ↓
6. Export (Training data ready)
```

### Annotation States

- **Pending**: No annotation yet
- **ML Annotation**: Auto-generated by AI
- **Human Annotation**: Manually created
- **To Review**: Needs verification
- **Certified**: Verified and approved
- **Rejected**: Marked as incorrect

## Technical Details

### Backend Implementation

**File**: `src/backend/api/ml.py`

**Endpoints:**
- `/infer/resnet50` - Single image
- `/infer/resnet50/batch` - Multiple images
- `/infer/resnet50/project` - Entire project

**Dependencies:**
- PyTorch
- torchvision
- PIL (Pillow)

### Frontend Implementation

**File**: `src/frontend/components/AIPanel.vue`

**Features:**
- Model selection interface
- Inference configuration
- Progress indication
- Results visualization
- Success rate calculation

### Database Schema

**Annotation Table:**
```python
Annotation(
    id=auto,
    status=ML_ANNOTATION,
    label="golden_retriever",
    annotation_score=None,  # Future: confidence score
    data_id=image_id,
    project_id=project_id,
    creation_date=now()
)
```

## Support

For issues or questions:
1. Check backend logs for errors
2. Verify image files are accessible
3. Test with single image first
4. Check API documentation at `/docs`

## Resources

- **PyTorch Models**: https://pytorch.org/vision/stable/models.html
- **ImageNet Classes**: https://gist.github.com/yrevar/942d3a0ac09ec9e5eb3a
- **ResNet Paper**: https://arxiv.org/abs/1512.03385
