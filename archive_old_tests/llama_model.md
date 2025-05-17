# choose a workspace
mkdir -p ~/models/medicine_llm13b && cd ~/models/medicine_llm13b

# direct curl (link is the Raw button on HF)
curl -L -o <model_name>.gguf \
  https://huggingface.co/TheBloke/medicine-LLM-13B-GGUF/resolve/main/<model_link>

mkdir -p ~/ollama-<model_name> && cd ~/ollama-<model_name>

cat > Modelfile <<'EOF'
FROM /data/home/zzz49063/models/<model_name>/<model_name>>.gguf
# Most LLama-family chat checkpoints expect [INST] … [/INST]
TEMPLATE "<s>[INST] {{ .Prompt }} [/INST]"
# Soft prepromt for the model
SYSTEM "You are a concise and truthful medical assistant."
EOF


# use the real binary! adjust path if different
~/bin/bin/ollama create medicine13b-chat -f Modelfile
~/bin/bin/ollama list        # should now show medicine13b-chat 13B ready
