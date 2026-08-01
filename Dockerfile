# CUDA 12.1 destekli resmi PyTorch imajını taban olarak kullanıyoruz
FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-devel

# Konteyner içindeki çalışma dizinini ayarlıyoruz
WORKDIR /app

# Git gibi gerekli sistem paketlerini kuruyoruz
RUN apt-get update && apt-get install -y git curl libssl-dev libcurl4-openssl-dev && rm -rf /var/lib/apt/lists/*

# Unsloth ve bağımlılıklarını kuruyoruz
RUN pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
RUN pip install --no-deps trl peft accelerate bitsandbytes datasets transformers
RUN pip install --upgrade "torchvision>=0.27.0"

# Mevcut dizindeki (bilgisayarınızdaki) tüm dosyaları konteynerin içine kopyalıyoruz
COPY . /app

# Çıktıların (model ve checkpointlerin) barınacağı klasörü oluşturuyoruz
RUN mkdir -p /app/output

# Konteyner başlatıldığında çalıştırılacak varsayılan komut
CMD ["python", "local finetune.py"]
