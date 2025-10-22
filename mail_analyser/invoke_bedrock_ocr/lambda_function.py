# lambda_function.py
import os, json, urllib.parse, urllib.request, urllib.error, base64, time
import boto3
from botocore.config import Config

REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
OUTPUT_BUCKET = os.environ["OUTPUT_BUCKET"]
OUTPUT_PREFIX = os.getenv("OUTPUT_PREFIX", "results/ocr/")

# n8n webhook config
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")  # allow empty to skip during tests
N8N_WEBHOOK_TOKEN = os.getenv("N8N_WEBHOOK_TOKEN", "")  # will be sent as X-Webhook-Token
N8N_WEBHOOK_TIMEOUT = float(os.getenv("N8N_WEBHOOK_TIMEOUT", "8"))  # seconds

s3 = boto3.client("s3", region_name=REGION, config=Config(retries={"max_attempts": 2}))
textract = boto3.client("textract", region_name=REGION, config=Config(read_timeout=25, retries={"max_attempts": 2}))
brt = boto3.client("bedrock-runtime", region_name=REGION, config=Config(read_timeout=30, retries={"max_attempts": 2}))

def _imgfmt(ct):
    if ct == "image/png": return "png"
    if ct in ("image/jpg","image/jpeg"): return "jpeg"
    return "jpeg"

def bedrock_ocr_image(img_bytes, image_format):
    print(f"[bedrock] invoking {MODEL_ID} with image_format={image_format}, bytes={len(img_bytes)}")
    resp = brt.converse(
        modelId=MODEL_ID,
        messages=[{"role":"user","content":[
            {"image":{"format": image_format, "source": {"bytes": img_bytes}}},
            {"text":"Extract ALL visible text from the image. Return only the text, no commentary."}
        ]}],
        inferenceConfig={"maxTokens":1500,"temperature":0.0}
    )
    blocks = resp["output"]["message"]["content"]
    return "\n".join(b.get("text","") for b in blocks if "text" in b).strip()

def textract_pdf(bucket, key):
    print(f"[textract] DetectDocumentText s3://{bucket}/{key}")
    r = textract.detect_document_text(Document={"S3Object":{"Bucket":bucket,"Name":key}})
    return "\n".join(b["Text"] for b in r.get("Blocks",[]) if b.get("BlockType")=="LINE" and "Text" in b)

def post_to_n8n(payload: dict):
    """POST JSON to n8n webhook with X-Webhook-Token auth header."""
    if not N8N_WEBHOOK_URL:
        print("[n8n] skipped (N8N_WEBHOOK_URL not set)")
        return "skipped"

    if not N8N_WEBHOOK_TOKEN:
        print("[n8n] warning: N8N_WEBHOOK_TOKEN not set (request will not include X-Webhook-Token)")

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
    }
    # Add auth header if provided
    if N8N_WEBHOOK_TOKEN:
        headers["X-Webhook-Token"] = N8N_WEBHOOK_TOKEN

    req = urllib.request.Request(N8N_WEBHOOK_URL, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=N8N_WEBHOOK_TIMEOUT) as resp:
        return resp.read().decode(errors="replace")

def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))
    results = []
    for rec in event.get("Records", []):
        bucket = rec["s3"]["bucket"]["name"]
        key = urllib.parse.unquote(rec["s3"]["object"]["key"])
        print(f"[start] s3://{bucket}/{key}")

        out_key = f"{OUTPUT_PREFIX}{key.replace('/','_')}.json"
        try:
            head = s3.head_object(Bucket=bucket, Key=key)
            ct = head.get("ContentType","")
            print(f"[s3] content-type={ct}")

            if ct.startswith("image/") or key.lower().endswith((".png",".jpg",".jpeg")):
                obj = s3.get_object(Bucket=bucket, Key=key)
                img_bytes = obj["Body"].read()
                text = bedrock_ocr_image(img_bytes, _imgfmt(ct or "image/jpeg"))
                model_used = MODEL_ID
            elif ct == "application/pdf" or key.lower().endswith(".pdf"):
                text = textract_pdf(bucket, key)
                model_used = "textract.detect_document_text"
            else:
                text = f"(Unsupported content type: {ct})"
                model_used = "none"

            result = {
                "source_bucket": bucket,
                "source_key": key,
                "content_type": ct,
                "model": model_used,
                "image_ocr": text
            }
            print(f"[s3-put] s3://{OUTPUT_BUCKET}/{out_key}")
            s3.put_object(Bucket=OUTPUT_BUCKET, Key=out_key, Body=json.dumps(result).encode("utf-8"))

            try:
                n8n_resp = post_to_n8n({"bucket": OUTPUT_BUCKET, "key": out_key, **result})
                print(f"[n8n] {str(n8n_resp)[:120]}")
                result["n8n_status"] = "OK" if n8n_resp != "skipped" else "SKIPPED"
            except Exception as e:
                print(f"[n8n] error: {e}")
                result["n8n_status"] = f"ERROR: {e.__class__.__name__}"

            results.append(result)

        except Exception as e:
            # Always write a failure artifact to S3 to aid debugging
            err = {
                "error": str(e),
                "source_bucket": bucket,
                "source_key": key,
                "where": "handler"
            }
            fail_key = f"{OUTPUT_PREFIX}_failed/{key.replace('/','_')}.json"
            print(f"[error] {e}; writing {fail_key}")
            try:
                s3.put_object(Bucket=OUTPUT_BUCKET, Key=fail_key, Body=json.dumps(err).encode("utf-8"))
            except Exception as e2:
                print(f"[error] failed to write failure artifact: {e2}")
            raise
    return {"results": results} ⁠