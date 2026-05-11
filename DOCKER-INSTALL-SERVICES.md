# Guía: Docker Engine + NVIDIA GPU + Ollama + Open WebUI + n8n + Portainer en Ubuntu

Esta guía explica cómo instalar Docker Engine en Ubuntu, configurar los drivers de NVIDIA para usar la GPU con contenedores, y poner en marcha un stack de IA local con Ollama, Open WebUI, n8n y Portainer.

## Requisitos previos

- Un servidor o máquina virtual con Ubuntu 20.04 o superior
- Al menos 8GB de RAM y 40GB de almacenamiento
- GPU NVIDIA (recomendado para inferencia con Ollama)
- Acceso root o sudo

## Paso 1: Instalar Docker Engine

Docker ofrece un método oficial basado en su repositorio APT. Se realiza en dos partes.

### 1.1 — Añadir la clave GPG y el repositorio oficial de Docker

Ejecuta el siguiente bloque completo en la terminal:

```bash
# Añadir la clave GPG oficial de Docker
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Añadir el repositorio a las fuentes de APT
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
```

> Este método usa el formato moderno `.sources` de APT y detecta automáticamente la versión de Ubuntu instalada.

### 1.2 — Instalar Docker Engine y plugins

```bash
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Esto instala:

- `docker-ce` — el motor de Docker
- `docker-ce-cli` — la herramienta de línea de comandos
- `containerd.io` — el runtime de contenedores
- `docker-buildx-plugin` — soporte para builds multiplataforma
- `docker-compose-plugin` — Docker Compose integrado como subcomando (`docker compose`)

### 1.3 — Verificar la instalación

```bash
sudo docker run hello-world
```

### 1.4 — (Opcional) Usar Docker sin sudo

Para no tener que anteponer `sudo` a cada comando Docker, añade tu usuario al grupo `docker`:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

## Paso 2: Instalar los drivers de NVIDIA y el Container Toolkit

Para que Ollama pueda usar la GPU dentro de Docker es necesario instalar dos cosas: el driver de NVIDIA en el host y el **NVIDIA Container Toolkit**, que actúa de puente entre Docker y la GPU.

### 2.1 — Instalar el driver de NVIDIA

Comprueba primero qué GPU tienes:

```bash
lspci | grep -i nvidia
```

Instala el driver recomendado automáticamente con el paquete `ubuntu-drivers`:

```bash
sudo apt install ubuntu-drivers-common
sudo ubuntu-drivers autoinstall
```

> Si prefieres instalar una versión concreta (p. ej. 550), puedes hacerlo con `sudo apt install nvidia-driver-550`.

Reinicia el sistema para que el driver quede activo:

```bash
sudo reboot
```

Tras el reinicio, verifica que el driver funciona correctamente:

```bash
nvidia-smi
```

Deberías ver la información de tu GPU, la versión del driver y la versión máxima de CUDA soportada.

### 2.2 — Instalar el NVIDIA Container Toolkit

El toolkit permite a Docker exponer la GPU a los contenedores. Añade el repositorio oficial de NVIDIA:

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
```

Instala el toolkit:

```bash
sudo apt install nvidia-container-toolkit
```

Configura Docker para que use NVIDIA como runtime por defecto y reinicia el servicio:

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 2.3 — Verificar que Docker ve la GPU

```bash
docker run --rm --gpus all nvidia/cuda:12.0-base-ubuntu22.04 nvidia-smi
```

Si ves la salida de `nvidia-smi` dentro del contenedor, todo está correctamente configurado y Ollama podrá aprovechar la GPU.

## Paso 3: Poner en marcha Ollama con Open WebUI, n8n y Portainer

### 3.1 — Crear el archivo docker-compose.yml

Crea un archivo llamado `docker-compose.yml` en el directorio de trabajo y pega el siguiente contenido:

```yaml
services:
  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: always
    ports:
      - "9000:9000"
      - "9443:9443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: always
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_NUM_PARALLEL=4
      - OLLAMA_MAX_LOADED_MODELS=1
      - OLLAMA_FLASH_ATTENTION=1
      - OLLAMA_GPU_OVERHEAD=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    restart: always
    ports:
      - "3000:8080"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes:
      - open_webui_data:/app/backend/data
    depends_on:
      - ollama

  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      - ollama

volumes:
  portainer_data:
  ollama_data:
  open_webui_data:
  n8n_data:
```

Este `docker-compose.yml` define cuatro servicios:

| Servicio       | Imagen                                 | Puerto      | Descripción                                       |
| -------------- | -------------------------------------- | ----------- | -------------------------------------------------- |
| `portainer`  | `portainer/portainer-ce:latest`      | 9000 / 9443 | Panel de gestión de contenedores                  |
| `ollama`     | `ollama/ollama:latest`               | 11434       | Backend de inferencia LLM                          |
| `open-webui` | `ghcr.io/open-webui/open-webui:main` | 3000        | Interfaz web para interactuar con Ollama           |
| `n8n`        | `n8nio/n8n:latest`                   | 5678        | Plataforma de automatización de flujos de trabajo |

> **Nota sobre GPU:** El servicio `ollama` está configurado para usar todas las GPUs NVIDIA disponibles. Si tu máquina no tiene GPU NVIDIA, elimina el bloque `deploy` del servicio `ollama` antes de continuar.

### 3.2 — Levantar los contenedores

```bash
docker compose up -d
```

El flag `-d` ejecuta los contenedores en segundo plano (*detached mode*). Docker descargará las imágenes automáticamente si no están en caché.

### 3.3 — Verificar que los contenedores están corriendo

```bash
docker compose ps
```

Deberías ver los cuatro servicios con estado `running`.

### 3.4 — Descargar un modelo en Ollama

Una vez que el contenedor de Ollama esté activo, descarga un modelo. Por ejemplo, `llama3.2`:

```bash
docker exec -it ollama ollama pull llama3.2
```

Puedes explorar otros modelos disponibles en [https://ollama.com/library](https://ollama.com/library).

---

## Acceso a los servicios

| Servicio                    | URL                    |
| --------------------------- | ---------------------- |
| **Open WebUI**        | http://localhost:3000  |
| **n8n**               | http://localhost:5678  |
| **Portainer (HTTP)**  | http://localhost:9000  |
| **Portainer (HTTPS)** | https://localhost:9443 |
| **Ollama API**        | http://localhost:11434 |

> En el primer acceso a Portainer se te pedirá crear un usuario administrador.

---

## Comandos útiles

```bash
# Ver logs de un servicio
docker compose logs -f ollama

# Detener todos los servicios
docker compose down

# Detener y eliminar volúmenes (¡borra los datos!)
docker compose down -v

# Reiniciar un servicio concreto
docker compose restart open-webui
```

---

> Recuerda configurar autenticación y cifrado SSL/TLS si expones estos servicios fuera de tu red local.
>
