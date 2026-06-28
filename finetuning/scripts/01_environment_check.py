import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"

print("CUDA:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0))

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto",
)

messages = [
    {"role": "system", "content": "Ты полезный ассистент. Отвечай кратко."},
    {"role": "user", "content": "Проверь, что модель работает. Ответь одним предложением."},
]

text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt").to(model.device)

with torch.no_grad():
    output = model.generate(**inputs, max_new_tokens=80)

print(tokenizer.decode(output[0], skip_special_tokens=True))
print("VRAM allocated GB:", round(torch.cuda.memory_allocated() / 1024**3, 2))
