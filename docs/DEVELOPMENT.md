# Desarrollo y restauración del entorno

La referencia fijada es **Python 3.14.4**, indicada en `.python-version`.
`pyproject.toml` conserva Python >=3.11 como compatibilidad declarada, pero la
restauración verificada y el workflow utilizan únicamente la versión fijada.

## Instalar desde una copia limpia

Clona el repositorio y sitúate en su raíz. Usa un intérprete Python 3.14.4;
comprueba la versión antes de crear el entorno:

```sh
python3.14 --version
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation -e '.[test,providers,dev]'
.venv/bin/python -m pip check
.venv/bin/python -c "import openai, anthropic, dotenv"
.venv/bin/python -m ruff check backend
.venv/bin/python -m pytest -q --tb=short
```

El lock fija dependencias directas, transitivas y herramientas de construcción.
El proyecto editable se instala sin resolver otras dependencias y sin crear un
entorno de construcción con versiones distintas. Instalar los SDK explícitamente
permite detectar su ausencia antes de que `importorskip` omita las pruebas M2.
Los tests usan transportes HTTP simulados; no requieren claves ni consumen APIs.

Para la demo local:

```sh
.venv/bin/python -m backend.app.cli demo
```

Para llamadas reales, copia `.env.example` a `.env` y completa las cuatro variables
M2. Solo `run` sin `--dry-run` llama a los proveedores. No están implementados Google,
una base de datos o un proveedor LLM ciudadano configurable por variables de entorno.

## Verificaciones automáticas

`.github/workflows/checks.yml` ejecuta los comandos anteriores en cada push,
pull request o lanzamiento manual, sobre Ubuntu 24.04 y macOS 15 Intel. Usa acciones fijadas
por SHA, permisos de lectura del contenido y ningún secreto de proveedor.
El workflow no configura protección de ramas: un fallo aparece como check fallido,
pero no impide por sí mismo un push o un merge administrativo.

Ruff comprueba errores básicos y nombres/imports (`E4`, `E7`, `E9`, `F`), siguiendo
su [configuración oficial](https://docs.astral.sh/ruff/configuration/). Solo se
exceptúa `E402` en `test_m2.py`, donde los imports dependen de `importorskip`.
El análisis estático de tipos completo se incorporará gradualmente; no se afirma
que exista un gate mypy ni se reformatea todo el código en este incremento.
Acciones oficiales: [checkout](https://github.com/actions/checkout) y
[setup-python](https://github.com/actions/setup-python).

## Alcance de los escenarios

`Scenario`, el esquema de acciones y los catálogos están especializados en PL-001.
Un escenario distinto requiere revisar esos contratos, no basta con cambiar el YAML.
M3 incorpora un ciudadano híbrido; no exige generalizar a múltiples escenarios.

## Actualizar versiones

Actualiza dependencias en un entorno de trabajo controlado y pasa la suite antes
de sustituir el lock. Registra conjuntamente cambios de `.python-version`, extras
si procede, lock y evidencia de restauración. Para capturar nombres y versiones,
sin URLs, credenciales ni rutas de instalaciones editables:

```sh
.venv/bin/python - <<'PY'
from importlib.metadata import distributions
from pathlib import Path
packages = sorted(
    {(d.metadata['Name'], d.version) for d in distributions()
     if d.metadata['Name'] and d.metadata['Name'].lower() != 'ai-police-lab'},
    key=lambda item: item[0].lower(),
)
Path('requirements-dev.lock').write_text(
    '# Entorno de desarrollo y pruebas M2; regenerar según docs/DEVELOPMENT.md.\n'
    '# Versiones exactas; no contiene credenciales, rutas locales ni el proyecto editable.\n'
    + ''.join(f'{name}=={version}\n' for name, version in packages)
)
PY
```

Después repite la instalación y los checks desde otra copia y un entorno vacío.
No cierres la actualización por el mero hecho de generar el fichero.

## Git, archivos privados y límites

`.gitignore` excluye `.env` y variantes salvo `.env.example`, entornos virtuales,
trazas privadas, bases de datos, cachés y productos de construcción. Revisa siempre
`git diff --cached --stat` y `git diff --cached` antes de un commit. Las pruebas
contienen credenciales ficticias identificadas como tales; nunca sustituirlas por
claves reales. Un repositorio privado es una copia remota, no autorización para
incluir secretos ni datos policiales reales.

El lock fija versiones, no hashes de artefactos ni un sistema operativo completo.
La restauración requiere que el índice de paquetes siga disponible. Esta evidencia
no garantiza respuestas LLM idénticas ni todas las versiones de Python/plataformas.
El manifiesto de cada ejecución mantiene `restoration_verified: false`: no realiza
una prueba de restauración automática. La verificación LAB-007 se refiere al entorno
probado y se registra aparte, no certifica cualquier futura ejecución.
