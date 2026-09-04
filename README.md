# NVIDIA Delegate Skill

Skill reutilizable para delegar trabajo desde un modelo principal a modelos alojados en NVIDIA NIM, incluyendo DeepSeek, Kimi y Nemotron.

El flujo separa dos casos:

- `scripts/ask.py` para análisis o redacción sin herramientas.
- `opencode run` para inspeccionar, editar y probar un repositorio.

La respuesta del trabajador queda limitada a 12 líneas y 250 palabras para evitar devolver grandes cantidades de texto al contexto del modelo principal.

## Seguridad

Este repositorio no contiene claves, tokens, contraseñas, archivos de configuración privados ni rutas personales. El helper obtiene la credencial exclusivamente desde la variable de entorno `NVIDIA_API_KEY` y nunca la imprime.

No agregues `.env`, `config`, `auth.json`, claves privadas ni credenciales al repositorio.

## Requisitos

- Python 3.9 o posterior para `scripts/ask.py`.
- OpenCode para delegación agentic sobre repositorios.
- Una cuenta y API key de NVIDIA NIM.
- Los modelos elegidos habilitados en el provider NVIDIA de OpenCode.

## Instalación

Cloná el repositorio:

```powershell
git clone https://github.com/PabloIan92/nvidia-delegate-skill.git
```

Copiá `.claude/skills/nvidia-delegate/` al directorio de skills del proyecto o a `~/.claude/skills/`. OpenCode también puede cargarlo desde una ruta configurada en `skills.paths`.

Definí `NVIDIA_API_KEY` fuera del repositorio antes de usar el helper.

## Contenido

- `.claude/skills/nvidia-delegate/SKILL.md`: reglas de selección, delegación y revisión.
- `.claude/skills/nvidia-delegate/scripts/ask.py`: cliente de texto con salida acotada.
- `tests/test_ask.py`: pruebas del límite de salida y manejo seguro de credenciales.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```
