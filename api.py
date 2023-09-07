import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForCausalLM, pipeline
import argparse
from fastapi import FastAPI, Request
import uvicorn, json, datetime
import nest_asyncio
from pyngrok import ngrok

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE


def torch_gc():
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()


app = FastAPI()


@app.post("/")
async def create_item(request: Request):
    global model, tokenizer, prompt_template
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    question = json_post_list.get('prompt')
    prompt = prompt_template.format(
        user_question=question.replace("#","")
    )
    sql_type = "自然语言转换成SQL查询"
    if sql_type in prompt:
        prompt += "```sql"
    else:
        prompt += ">>>"
    history = json_post_list.get('history')
    max_length = json_post_list.get('max_length')
    top_p = json_post_list.get('top_p')
    temperature = json_post_list.get('temperature')
    eos_token_id = tokenizer.convert_tokens_to_ids(["```"])[0]
    print("Loading a model and generating a SQL query for answering your question...")
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=300,
        do_sample=False,
        num_beams=5, # do beam search with 5 beams for high quality results
    )
    print("==========input========")
    print(prompt)
    generated_query = (
            pipe(
                prompt,
                num_return_sequences=1,
                eos_token_id=eos_token_id,
                pad_token_id=eos_token_id,
            )[0]["generated_text"]
    )

    response = generated_query

    if sql_type in prompt:
      response = response.split("`sql")[-1].split("`")[0].split(";")[0].strip() + ";"

    else:
      response = response.split(">>>")[-1].split("`")[0].strip()

    print("========output========")
    print(response)
    torch_gc()
    return response


if __name__ == '__main__':
    prompt_template = ""
    with open("prompt.md", "r") as f:
        prompt_template = f.read()
    tokenizer = AutoTokenizer.from_pretrained("/mnt/workspace/sqlcoder-model/sqlcoder", trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained("/mnt/workspace/sqlcoder-model/sqlcoder",
                                      trust_remote_code=True,
                                      # torch_dtype=torch.float16,
                                      load_in_8bit=True,
                                      device_map="auto",
                                      use_cache=True)
    ngrok_tunnel = ngrok.connect(8000)
    print('Public URL:', ngrok_tunnel.public_url)
    nest_asyncio.apply()
    uvicorn.run(app, host='0.0.0.0', port=8000, workers=1)



