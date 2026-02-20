from huggingface_hub import list_models
from transformers import pipeline

# Cache pipelines to avoid reloading models
PIPELINES = {}


def get_huggingface_models(task: str, limit=20):
    models = list_models(filter=task, sort="downloads", direction=-1, limit=limit)
    return [{"id": m.modelId, "downloads": m.downloads, "likes": m.likes} for m in models]


def get_pipeline(model_id: str, task: str):
    """Get or create a cached pipeline for the given model and task"""
    cache_key = f"{model_id}:{task}"
    if cache_key not in PIPELINES:
        print(f"Loading pipeline for {model_id} with task {task}...")
        PIPELINES[cache_key] = pipeline(task, model=model_id)
        print("Pipeline loaded successfully!")
    return PIPELINES[cache_key]


def run_local_inference(model_id: str, task: str, input_data):
    """Run inference using a Hugging Face model"""
    pipe = get_pipeline(model_id, task)
    result = pipe(input_data)
    return result


if __name__ == "__main__":
    print(get_huggingface_models(task="image-classification", limit=5))
